import numpy as np
import nibabel as nib
import pathlib as pl


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


data_folder=r'/Users/ayam/Documents/PythonHackathon_Mos/Data/HealthyControls/RawData'
a=GroupStatistics(data_folder)
a.run()


