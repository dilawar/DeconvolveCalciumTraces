# Import stuff
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from constrained_foopsi import constrained_foopsi


# Load calcium trace given mat file and convert to CSV
class LoadCalciumTrace(object):
    def __init__(self, WorkingDirectory, FileName):
        self.WorkingDirectory = WorkingDirectory
        self.FileName = FileName

    def get_matfile_convert_to_csv(self):
        alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, self.FileName))  # Load data
        calcium = alldata['A_On_SubClusters']

        compiledata = []
        for ii in xrange(0, np.size(calcium, 1)):  # Compile from all fish
            compiledata.append(calcium[0, ii][11:, :])

        compiledata = np.asarray(np.hstack(compiledata))
        np.savetxt(os.path.join(self.WorkingDirectory, "rawdata.csv"), compiledata, delimiter=",")

        return compiledata

    def convert_to_firing_rate(self, calciumtraces):

        firingrate = []
        denoisedcalicumtrace = []
        for ii in xrange(0, 100): #np.size(calciumtraces, 1)):
            fluor = calciumtraces[:, ii]
            print 'Deconvolving..',ii
            deconvolvedresult = constrained_foopsi(fluor)
            firingrate.append(deconvolvedresult[5])
            denoisedcalicumtrace.append(deconvolvedresult[0])

        firingrate = np.asarray(np.vstack(firingrate)).T
        denoisedcalicumtrace = np.asarray(np.vstack(denoisedcalicumtrace)).T

        np.savetxt(os.path.join(self.WorkingDirectory, "denoiseddata.csv"), denoisedcalicumtrace, delimiter=",")
        np.savetxt(os.path.join(self.WorkingDirectory, "firingrate.csv"), firingrate, delimiter=",")

        plt.plot(firingrate, '.')
        plt.savefig('/Users/seetha/Desktop/test1.png')


if __name__ == '__main__':
    DataPath = '/Users/seetha/Desktop/Modelling/Data/Blue_Con_Fish104-109.mat'
    WorkingDirectory, FileName = os.path.split(DataPath)

    Habenula = LoadCalciumTrace(WorkingDirectory, FileName)
    CalciumData = Habenula.get_matfile_convert_to_csv()
    Habenula.convert_to_firing_rate(CalciumData)
