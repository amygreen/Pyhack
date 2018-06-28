#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `PythonHackathon` package."""

import pytest
from PythonHackathon import *

class TestPythonHackathon:

    def test_zscores(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (sa.zscores[2,3,1] == -3)

    def test_area_zscores(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (np.round(sa.area_data.iloc[0,0],1) == 5.6)

    def test_area_values(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (np.round(sa.area_data.iloc[0,0],2) == -0.36)

    def test_correct_subject_input(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (sa.shape == (4,4,4))

    def test_wrong_mean_input(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean_wrong_size.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (~sa.is_data_proper) and (~sa.is_mean_proper)

    def test_wrong_sd_input(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd_wrong_size.nii'
        atlas_nii_path = 'test_atlas.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (~sa.is_data_proper) and (~sa.is_sd_proper)

    def test_wrong_atlas_input(self):
        subject_nii_path = 'test_subject.nii'
        mean_nii_path = 'test_mean.nii'
        sd_nii_path = 'test_sd.nii'
        atlas_nii_path = 'test_atlas_wrong_size.nii'
        sa = SubjectAnalyzer(subject_nii_path,mean_nii_path,sd_nii_path,atlas_nii_path)
        assert (~sa.is_data_proper) and (~sa.is_atlas_proper)
