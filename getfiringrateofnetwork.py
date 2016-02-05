# Import stuff
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import os
from constrained_foopsi import constrained_foopsi


# Load calcium trace given mat file and convert to CSV
class LoadCalciumTrace(object):
    def __init__(self, WorkingDirectory):
        self.WorkingDirectory = WorkingDirectory

    def get_data_from_matfile(self):
        mat_filenames = [f for f in os.listdir(self.WorkingDirectory) if f.endswith('.mat')]

        for ii in mat_filenames:
            print 'Collecting File...', ii
            alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, ii))
            # Get data and normalize
            calcium = alldata['CellZ5'][11:, :]
            calcium_dfof = (calcium - np.mean(calcium[10:30, :], 0)) / (np.std(calcium[10:30, :], 0) + 0.001)
            calcium_dfof_norm = (calcium_dfof - np.min(calcium_dfof, 0)) / (
                np.max(calcium_dfof, 0) - np.min(calcium_dfof, 0))

            # Append fish information
            fish_num = np.ones(np.size(calcium_dfof_norm, 1))*int(ii[4:7])
            plane_num = alldata['CellZ5'][3:, :]
            



if __name__ == '__main__':
    WorkingDirectory = '/Users/seetha/Desktop/Modelling/Data/Network/'

    Habenula = LoadCalciumTrace(WorkingDirectory)
    Habenula.get_data_from_matfile()

    # Habenula.convert_to_firing_rate(CalciumData)
    # Habenula.test()
