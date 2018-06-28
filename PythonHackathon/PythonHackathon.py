import remi.gui as gui
from remi import start, App
import pathlib
from xhtml2pdf import pisa
import urllib.request as urllib2
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import plotting
import pathlib as pl


class SubjectAnalyzer:

    def __init__(self,subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path):

        '''Get paths for files'''
        self.subject_nii_path = subject_nii_path
        self.mean_nii_path = mean_nii_path
        self.sd_nii_path = sd_nii_path
        self.atlas_nii_path = atlas_nii_path

        # Read nii images:
        self.load_data()
        # If data is OK, continue to analysis:
        if self.is_data_proper:
            self.calculate_zscore() # Calculate voxel z-scores
            self.calculate_atlas_results() # Calculate atlas areas mean values and z-scores
        else: # If data dimensions do not fit, output an error message detailing the error
            self.error_message = \
                "The following inputs: {}{}{}have an inconsistent have a dimension mismatch with the subject".format(
                    'mean map, ' if not self.is_mean_proper else '',
                    'st. dev. map, ' if not self.is_sd_proper else '',
                    'atlas, ' if not self.is_atlas_proper else '')

    def load_data(self):
        # Load nifti data of subject, mean and sd of "population" and atlas:
        self.subject_img = nib.load(self.subject_nii_path)
        self.mean_img = nib.load(self.mean_nii_path)
        self.sd_img = nib.load(self.sd_nii_path)
        self.atlas_img = nib.load(self.atlas_nii_path)

        self.shape = self.subject_img.shape # get dimensions of subject's data
        self.is_mean_proper = self.mean_img.shape == self.shape # test that the mean data is the same shape
        self.is_sd_proper = self.sd_img.shape == self.shape # test that the sd data is the same shape
        self.is_atlas_proper = self.atlas_img.shape == self.shape  # test that the atlas data is the same shape

        # set is_data_proper to false if one of the inputs is not in the same dimensions as the subject
        self.is_data_proper = self.is_mean_proper and self.is_sd_proper and self.is_atlas_proper

        self.subject_data = self.subject_img.get_data() # get subject data from image
        self.mean_data = self.mean_img.get_data() # get mean data from image
        self.sd_data = self.sd_img.get_data() # get SD data from image
        self.atlas_data = self.atlas_img.get_data() # get atlas data from image

        # set zeros values to nan for subject, mean and sd data
        self.subject_data[self.subject_data==0] = np.nan
        self.mean_data[self.mean_data == 0] = np.nan
        self.sd_data[self.sd_data == 0] = np.nan


    def calculate_zscore(self):
        '''
        calculates the zscore for each subject voxel based on the control mean and sd
        finds only significant voxels and saves them as "zs.nii.gz"
        '''
        self.zscores = (self.subject_data - self.mean_data) / self.sd_data # calculate zscores
        zscores = self.zscores
        zscores[np.isnan(zscores)] = 0 # replace nans with z scores temporarily
        # finds non significant values and replaces them with zeros for new variable:
        self.significant_zscores = np.where(np.abs(zscores)<=1.96,np.nan,zscores)
        # creates nifti template:
        self.significant_zscores_nii = nib.Nifti1Image(self.significant_zscores,self.subject_img.affine)
        nib.save(self.significant_zscores_nii, 'zs.nii.gz') # save nifti template
        zs_nii_path = self.significant_zscores_nii
        plotting.plot_glass_brain(zs_nii_path, threshold=1.96, colorbar=True, plot_abs=False,
                                  output_file='Z_map.png',vmax=5)


    def calculate_atlas_results(self):
        '''
        for each area in the atlas supplied, calculate the average value and z-score
        '''
        vals = np.zeros(self.atlas_data.max()) # initialize values array
        zs = np.zeros(self.atlas_data.max()) # initialize zscores array
        for i in range(1,self.atlas_data.max()+1): # for every area
            vals[i-1] = np.nanmean(self.subject_data[self.atlas_data == i]) # calculate mean value in area
            zs[i-1] = np.nanmean(self.zscores[self.atlas_data == i]) # calculate mean z-score in area

        vals = pd.Series(vals,index = np.arange(1,self.atlas_data.max()+1)) # create values series
        zs_s = pd.Series(zs,index = np.arange(1,self.atlas_data.max()+1)) # create zscore series
        self.area_data = pd.DataFrame({'Values': vals, 'Z-scores': zs_s}) # create dataframe from both
        self.area_data.index.name = 'Area' # change index name to area

        subject_data = self.area_data
        decimals = pd.Series([4, 2], index=['Values', 'Z-scores'])
        subject_data = subject_data.round(decimals)
        temp = [['Region', 'Value', 'Z-score']]
        for row in subject_data.iterrows():
            index, data = row
            temp.append([index] + data.tolist())
        self.table = temp



class MyApp(App):
    """Main App for Z-score calculation and visual presentation"""

    def __init__(self, *args):
        impath = str(pathlib.Path('.').absolute())
        super(MyApp, self).__init__(*args, static_file_path=impath)

    def main(self):
        """ GUI contains two vertical containers: Menu at top and all other widgets underneath
            It also contains three horizontal containers:
            Left one contains subject name widget, date, remarks & instructions.
            Middle containers is devoted for table with results.
            Right containers contains the analyze button and data visualization"""

        vertical_container = gui.Widget(width=1050, margin='0px auto',
                                           style={'display': 'block', 'overflow': 'hidden'})
        horizontal_container = gui.Widget(width='100%', layout_orientation=gui.Widget.LAYOUT_HORIZONTAL, margin='0px',
                                         style={'display': 'block', 'overflow': 'auto'})

        sub_container_left = gui.Widget(width=300,
                                          style={'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        sub_container_right = gui.Widget(width=400,
                                      style={'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        sub_container_instructions = gui.Widget(width=250, height = 450, margin='10px',
                                      style={'display': 'block', 'overflow': 'auto', 'text-align': 'left'})

        """ Subject's number:"""
        self.txt_subject = gui.TextInput(width=230, height=35, margin='1px')
        self.txt_subject.set_text("Subject number")
        self.txt_subject.style['font-size'] = '18px'
        self.txt_subject.style['background'] = 'lightgreen'
        self.txt_subject.style['text-align'] = 'center'

        """ Date: """
        self.date_headline = gui.Label('Acquisition date:', width=230, height=20, margin='1px')
        self.date_headline.style['text-align'] = 'left'
        self.date = gui.Date('2018-01-01', width=230, height=30, margin='1px')
        self.date.style['font-size'] = '16px'

        """ Remarks box: """
        self.txt = gui.TextInput(width=230, height=70, margin='1px')
        self.txt.set_text('Add remarks here')

        """ Instructions: """
        inst1 = gui.Label('Instructions:', width=230, height=25, margin='0px')
        inst1.style['font-size'] = '16px'
        inst1.style['background'] = 'lightgray'
        inst2 = gui.Label("1. Set subject's number and acquisition date", width=230, height=45, margin='0px')
        inst2.style['background'] = 'lightgray'
        inst3 = gui.Label("2. Load files: subject's map file, wanted mask and general population data (mean, sd & template)",
            width=230, height=80, margin='0px')
        inst3.style['background'] = 'lightgray'
        inst4 = gui.Label("3. Press 'Analyze' button", width=230, height=25, margin='0px')
        inst4.style['background'] = 'lightgray'
        inst5 = gui.Label("4. Export your report", width=230, height=25, margin='0px')
        inst5.style['background'] = 'lightgray'

        sub_container_instructions.append([self.txt_subject,self.date_headline,self.date, self.txt, inst1, inst2, inst3, inst4, inst5])

        """ Create Table: """
        self.table = gui.Table.new_from_list([['Region', 'value', 'Z-score'],
                                              ['Prefrontal Lateral R', '80', '1.2'],
                                              ['Prefrontal Lateral L', '25', '1.99'],
                                              ['Sensorimotor R', '76', '0.23'],
                                              ['Sensorimotor L', '88', '2.55']], width=250, height=500, margin='10px')


        sub_container_left.append(self.table, key='table')

        """ Logo: """
        sagol_logo = gui.Image(r'/res/Sagollogo.png', width=300, height=60, margin='25px')
        sagol_logo.style['background'] = 'white'

        """ Analyze button: """
        self.bt_analyze = gui.Button("Analyze", width=350, height=30, margin='16px')
        self.bt_analyze.onclick.connect(self.on_analyze_pressed)

        """ Figure which be replace to visualized results: """
        self.figure_analyzed = gui.Image(r'/res/es.jpg', width=350, height=300, margin='10px')

        sub_container_right.append([sagol_logo, self.bt_analyze])
        sub_container_right.append(self.figure_analyzed, key='image')

        self.sub_container_left = sub_container_left
        self.sub_container_right = sub_container_right
        self.instructions = sub_container_instructions

        horizontal_container.append([self.instructions, self.sub_container_left, self.sub_container_right])

        """ Menu: """
        menu = gui.Menu(width='100%', height='30px')
        m1 = gui.MenuItem('Select Subject', width=100, height=30)
        m1.onclick.connect(self.menu_subject_clicked)
        m2 = gui.MenuItem('Properties', width=100, height=30)
        m3 = gui.MenuItem("Export as", width=100, height=30)
        m21 = gui.MenuItem('Select Mask', width=200, height=30)
        m21.onclick.connect(self.menu_mask_clicked)
        m22 = gui.MenuItem('General population data', width=200, height=30)
        m31 = gui.MenuItem('PDF', width=100, height=30)
        m31.onclick.connect(self.menu_pdf_clicked)
        m221 = gui.MenuItem('Select mean data', width=100, height=30)
        m221.onclick.connect(self.menu_mean_clicked)
        m222 = gui.MenuItem('Select SD data', width=100, height=30)
        m222.onclick.connect(self.menu_sd_clicked)
        m223 = gui.MenuItem('Select template', width=100, height=30)
        m223.onclick.connect(self.menu_template_clicked)
        menu.append([m1, m2, m3])
        m2.append([m21, m22])
        m3.append([m31])
        m22.append([m221, m222, m223])

        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)

        vertical_container.append([menubar, horizontal_container])

        return vertical_container

    def on_analyze_pressed(self, widget):
        subject_class = SubjectAnalyzer(self.map_file, self.mean_file, self.sd_file, self.mask_file)
        table_content = subject_class.table

        self.table = gui.Table.new_from_list(table_content, width=250, height=500, margin='10px')
        print([['Region', 'value', 'Z-score'], table_content])
        self.sub_container_left.append(self.table, key='table')
        self.figure_analyzed = gui.Image(r'/res/Z_map.png',width=350, height=150, margin='10px')

        self.sub_container_right.append(self.figure_analyzed, key='image')

    def menu_subject_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', "Select subject's map file", False,
                                                           '.')
        self.fileselectionDialog.confirm_value.connect(self.on_subject_fileselection_dialog_confirm)
        self.fileselectionDialog.show(self)

    def on_subject_fileselection_dialog_confirm(self, widget, filelist):
        """ Called when the user pressed 'Done' in the
        file selection dialog """
        self.map_file = filelist[0]

    def menu_mask_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select files and folders', False,
                                                           '.')
        self.fileselectionDialog.confirm_value.connect(self.on_mask_fileselection_dialog_confirm)
        self.fileselectionDialog.show(self)

    def on_mask_fileselection_dialog_confirm(self, widget, filelist):
        """ Called when the user pressed 'Done' in the
        file selection dialog """
        self.mask_file = filelist[0]

    def menu_mean_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select files and folders', False,
                                                           '.')
        self.fileselectionDialog.confirm_value.connect(self.on_mean_fileselection_dialog_confirm)
        self.fileselectionDialog.show(self)

    def on_mean_fileselection_dialog_confirm(self, widget, filelist):
        """ Called when the user pressed 'Done' in the
        file selection dialog """
        self.mean_file = filelist[0]

    def menu_sd_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select files and folders', False,
                                                           '.')
        self.fileselectionDialog.confirm_value.connect(self.on_sd_fileselection_dialog_confirm)
        self.fileselectionDialog.show(self)

    def on_sd_fileselection_dialog_confirm(self, widget, filelist):
        """ Called when the user pressed 'Done' in the
        file selection dialog """
        self.sd_file = filelist[0]

    def menu_template_clicked(self, widget):
        self.fileselectionDialog = gui.FileSelectionDialog('File Selection Dialog', 'Select files and folders', False,
                                                           '.')
        self.fileselectionDialog.confirm_value.connect(self.on_template_fileselection_dialog_confirm)
        self.fileselectionDialog.show(self)

    def on_template_fileselection_dialog_confirm(self, widget, filelist):
        """ Called when the user pressed 'Done' in the
        file selection dialog """
        self.template_file = filelist[0]


    def menu_pdf_clicked(self, widget):
        """ returns PDF file but doesn't keep the layout"""
        url = urllib2.urlopen('http://127.0.0.1:8081')
        sourceHtml = url.read()
        pisa.showLogging()
        outputFilename = "test555.pdf"
        resultFile = open(outputFilename, "w+b")
        pisaStatus = pisa.CreatePDF(sourceHtml, resultFile)
        resultFile.close()

def run_gui():
    """ starts the webserver"""

    start(MyApp, address='127.0.0.1', start_browser=True, multiple_instance=True)

class GroupStatistics():
    """
    This class gets a folder that contains raw data files.
    It merges them into a large array and calculates mean and std per each voxel across all subjects.
    It returns two maps: mean and std maps.
    """

    def __init__(self,data_folder):
        self.data_foldername = data_folder
        if not pl.Path(data_folder).exists():
            raise TypeError(f'{data_folder} is not a valid path input')


    def run(self,mean=True,std=True):
        """
        Runs the methods of this class.
        :param mean: False if you don't want a mean map as output
        :param std: False if you don't want a std map as output
        :return: by default two maps of mean and std of each voxel.
        """
        self.merge_subjects()
        if mean:
            self.calculate_mean()
        if std:
            self.calculate_std()


    def merge_subjects(self):
        """
        Takes each subject's data and creates an array that contains all subjects.
        """
        foldername = pl.Path(self.data_foldername)
        self.files = [x for x in foldername.glob('*.nii.gz') if x.is_file()]
        arrays_list_to_stack=[]
        for i in range(len(self.files)):
            img=nib.load(str(self.files[i]))
            if len(img.get_data().shape) < 3:
                raise RuntimeError('one of the maps is invalid - contains less than 3 dimensions')
            elif len(img.get_data().shape) > 3:
                raise RuntimeError('one of the maps is invalid - contains more than 3 dimensions')
            arrays_list_to_stack.append(img.get_data())
        self.group_data=np.stack(arrays_list_to_stack,axis=0)


    def calculate_mean(self):
        """
        Calculates mean per voxel across all subjects
        :return: nifiti file - mean map
        """
        self.data_mean = np.mean(self.group_data,axis=0)
        self.data_mean_img = nib.Nifti1Image(self.data_mean, np.eye(4))
        nib.save(self.data_mean_img, 'data_mean.nii.gz')

    def calculate_std(self):
        """
        Calculates std per voxel across all subjects
        :return: nifiti file - std map
        """
        self.data_std = np.std(self.group_data,axis=0)
        self.data_std_img = nib.Nifti1Image(self.data_std, np.eye(4))
        nib.save(self.data_std_img, 'data_std.nii.gz')

def run_population_anaylsis(data_folder):
    a=GroupStatistics(data_folder)
    a.run()

