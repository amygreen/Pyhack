import numpy as np
import pandas as pd
import nibabel as nib

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
        self.subject_img = nib.load(self.subject_nii_path)
        self.mean_img = nib.load(self.mean_nii_path)
        self.sd_img = nib.load(self.sd_nii_path)
        self.atlas_img = nib.load(self.atlas_nii_path)

        self.shape = self.subject_img.shape
        self.is_mean_proper = self.mean_img.shape == self.shape
        self.is_sd_proper = self.sd_img.shape == self.shape
        self.is_atlas_proper = self.atlas_img.shape == self.shape

        self.is_data_proper = self.is_mean_proper and self.is_sd_proper and self.is_atlas_proper

        self.subject_data = self.subject_img.get_data()
        self.mean_data = self.mean_img.get_data()
        self.sd_data = self.sd_img.get_data()
        self.atlas_data = self.atlas_img.get_data()

        self.subject_data[self.subject_data==0] = np.nan
        self.mean_data[self.mean_data == 0] = np.nan
        self.sd_data[self.sd_data == 0] = np.nan


    def calculate_zscore(self):
        self.zscores = (self.subject_data - self.mean_data) / self.sd_data
        zscores = self.zscores
        zscores[np.isnan(zscores)] = 0
        self.significant_zscores = np.where(np.abs(zscores)<=1.96,np.nan,zscores)
        self.significant_zscores_nii = nib.Nifti1Image(self.significant_zscores,self.subject_img.affine)
        nib.save(self.significant_zscores_nii, 'zs.nii.gz')

    def calculate_atlas_results(self):
        vals = np.zeros(self.atlas_data.max())
        zs = np.zeros(self.atlas_data.max())
        for i in range(1,self.atlas_data.max()+1):
            vals[i-1] = np.nanmean(self.subject_data[self.atlas_data == i])
            zs[i-1] = np.nanmean(self.zscores[self.atlas_data == i])

        vals = pd.Series(vals,index = np.arange(1,self.atlas_data.max()+1))
        zs_s = pd.Series(zs,index = np.arange(1,self.atlas_data.max()+1))
        self.area_data = pd.DataFrame({'Values': vals, 'Z-scores': zs_s})
        self.area_data.index.name = 'Area'
