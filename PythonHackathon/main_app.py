import remi.gui as gui
from remi import start, App
import pathlib
from xhtml2pdf import pisa
import urllib.request as urllib2
from zscores import *


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

if __name__ == "__main__":
    """ starts the webserver"""

    start(MyApp, address='127.0.0.1', start_browser=True, multiple_instance=True)




