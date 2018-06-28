import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import plotting

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
