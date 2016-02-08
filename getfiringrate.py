# Import stuff
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import os
from constrained_foopsi import constrained_foopsi


# Load calcium trace given mat file and convert to CSV
class LoadCalciumTrace(object):
    def __init__(self, WorkingDirectory, FileName, key):
        self.WorkingDirectory = WorkingDirectory
        self.FileName = FileName
        self.key = key

    def get_matfile_convert_to_csv(self):
        alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, self.FileName))  # Load data
        calcium = alldata[self.key]

        compiledata = []
        fishnumber = []
        regionnumber = []
        for ii in xrange(0, np.size(calcium, 1)):  # Compile from all fish
            compiledata.append(calcium[0, ii][11:, :])
            fishnumber.append(calcium[0, ii][4, :])
            regionnumber.append(calcium[0, ii][8, :])

        print fishnumber

        compiledata = np.asarray(np.hstack(compiledata))
        fishnumber = np.asarray(np.hstack(fishnumber))
        regionnumber = np.asarray(np.hstack(regionnumber))



        np.savetxt(os.path.join(self.WorkingDirectory, key + "_rawdata.csv"), compiledata, delimiter=",")

        print np.shape(compiledata)
        return compiledata

    def convert_to_firing_rate(self, calciumtraces):

        firingrate = []
        denoisedcalicumtrace = []
        for ii in xrange(0, np.size(calciumtraces, 1)):
            fluor = calciumtraces[:, ii]
            print 'Deconvolving..', ii

            deconvolvedresult = constrained_foopsi(fluor)
            print np.ndim(deconvolvedresult[5])

            if np.ndim(deconvolvedresult[5]) > 1:
                print 'Skipping..Cell ', ii
                continue
            firingrate.append(deconvolvedresult[5])
            denoisedcalicumtrace.append(deconvolvedresult[0])

        firingrate = np.asarray(np.vstack(firingrate)).T
        denoisedcalicumtrace = np.asarray(np.vstack(denoisedcalicumtrace)).T

        np.savetxt(os.path.join(self.WorkingDirectory, key + "_denoiseddata.csv"), denoisedcalicumtrace, delimiter=",")
        np.savetxt(os.path.join(self.WorkingDirectory, key + "_firingrate.csv"), firingrate, delimiter=",")

        plt.plot(np.clip(firingrate, 0, np.max(firingrate)), '.')
        plt.savefig('/Users/seetha/Desktop/test1.png')

    def test(self):
        firingrate = np.loadtxt(os.path.join(self.WorkingDirectory, "firingrate.csv"), delimiter=",")
        print 'Max ', np.max(firingrate), 'Min ', np.min(firingrate)
        plt.plot(np.clip(firingrate, 0, np.max(firingrate)), '.')
        plt.savefig('/Users/seetha/Desktop/test2.png')


if __name__ == '__main__':
    DataPath = '/Users/seetha/Desktop/Modelling/Data/Blue_Con_Fish104-109.mat'
    key = 'A_On_SubClusters'

    WorkingDirectory, FileName = os.path.split(DataPath)
    Habenula = LoadCalciumTrace(WorkingDirectory, FileName, key)
    CalciumData = Habenula.get_matfile_convert_to_csv()
    # Habenula.convert_to_firing_rate(CalciumData)
    # Habenula.test()
