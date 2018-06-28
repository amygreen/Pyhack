import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import os
from dipy.segment.mask import median_otsu
from dipy.core.histeq import histeq
from nipype.workflows.dmri.fsl.artifacts import ecc_pipeline
import dipy.reconst.dti as dti
from dipy.core.gradients import gradient_table
from dipy.reconst.dti import fractional_anisotropy, color_fa
from nipype.interfaces import fsl


class Preprocessing():

    def __init__(self,bvecs_file, bvals_file, dti4d_file, mni_template):
        self.bvecs_file = bvecs_file
        self.bvals_file = bvals_file
        self.dti4d_file = dti4d_file
        self.mni_template = mni_template
        self.img = nib.load(self.dti4d_file)
        self.data = self.img.get_data()


    def brain_segmentation(self):
        """
        This function does brain segmentation using Dipy - median_otsu
        :return:
        Two nifti files - binary mask and the brain mask
        """
        #self.data=self.data[:,:,:,4]
        self.b0_mask, self.mask = median_otsu(self.data, 3, 1, True,
                             vol_idx=range(5, 15), dilate=2)
        self.mask_img = nib.Nifti1Image(self.mask.astype(np.float32), self.img.affine)
        self.b0_img = nib.Nifti1Image(self.b0_mask.astype(np.float32), self.img.affine)
        fname = ''
        nib.save(self.mask_img, fname + '_binary_mask.nii.gz')
        nib.save(self.b0_img, fname + '_mask.nii.gz')

        '''sli = self.data.shape[2] // 2
        plt.figure('Brain segmentation')
        plt.subplot(1, 2, 1).set_axis_off()
        plt.imshow(histeq(self.data[:, :, sli].astype('float')).T,
                   cmap='gray', origin='lower')

        plt.subplot(1, 2, 2).set_axis_off()
        plt.imshow(histeq(self.b0_mask[:, :, sli].astype('float')).T,
                   cmap='gray', origin='lower')
        plt.show()'''


    def eddy_currnets_correction(self,diffustion_nii, difusion_bval, mask_nii):
        self.ecc = ecc_pipeline()
        self.ecc.inputs.inputnode.in_file = diffustion_nii
        self.ecc.inputs.inputnode.in_bval = difusion_bval
        self.ecc.inputs.inputnode.in_mask = mask_nii
        self.ecc.run()  # doctest: +SKIP


    def eddy_currnets_correction(self,diffustion_nii, difusion_bval, mask_nii):
        self.ecc = ecc_pipeline()
        self.ecc.inputs.inputnode.in_file = diffustion_nii
        self.ecc.inputs.inputnode.in_bval = difusion_bval
        self.ecc.inputs.inputnode.in_mask = mask_nii
        self.ecc.run()  # doctest: +SKIP


    def DTI_fit(self):
        """

        gtab = gradient_table(bvals_file, bvecs_file)
        tenmodel = dti.TensorModel(gtab)
        tenfit = tenmodel.fit(self.mask_img)
        FA = fractional_anisotropy(tenfit.evals)
        :return:
        """
        os.chdir(r'/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files')
        dti = fsl.DTIFit()
        dti.inputs.dwi = 'DTI4D.nii'
        dti.inputs.bvecs = 'bvecs'
        dti.inputs.bvals = 'bvals'
        dti.inputs.base_name = 'TP'
        dti.inputs.mask = 'nodif_brain_mask.nii'
        dti.inputs.output_type = 'NIFTI'
        dti.run()




bvecs_file='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/bvecs'
bvals_file='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/bvals'
dti4d_file='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/DTI4D.nii.gz'
mni_template='/Users/ayam/Documents/PythonHackathon_Mos/Data/mni151_2mm.nii'


file=Preprocessing(bvecs_file,bvals_file,dti4d_file,mni_template)
file.brain_segmentation()

file.DTI_fit()
#diffustion_nii='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/DTI4D.nii'
#difusion_bval='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/bvals'
#mask_nii='/Users/ayam/Documents/PythonHackathon_Mos/PythonHackathon_Mos/PythonHackathon_Mos/_mask.nii.gz'
#file.eddy_currnets_correction(diffustion_nii,difusion_bval,mask_nii)

diffustion_nii='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/DTI4D.nii'
difusion_bval='/Users/ayam/Documents/PythonHackathon_Mos/Data/Stroke/files/bvals'
mask_nii='/Users/ayam/Documents/PythonHackathon_Mos/PythonHackathon_Mos/PythonHackathon_Mos/_mask.nii.gz'
file.eddy_currnets_correction(diffustion_nii,difusion_bval,mask_nii)

