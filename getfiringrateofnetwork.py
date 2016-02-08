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
            compiledata_perfish = np.array([])
            print 'Collecting File...', ii
            alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, ii))

            # Get data and normalize
            calcium = alldata['CellZ5'][11:, :]
            calcium_dfof = (calcium - np.mean(calcium[10:30, :], 0)) / (np.std(calcium[10:30, :], 0) + 0.001)
            calcium_dfof_norm = (calcium_dfof - np.min(calcium_dfof, 0)) / (
                np.max(calcium_dfof, 0) - np.min(calcium_dfof, 0))

            # Append fish information
            fish_num = np.ones(np.size(calcium_dfof_norm, 1)) * int(ii[4:7])
            plane_num = (alldata['CellZ5'][3, :] < 4).astype(int)
            print plane_num.T
            np.savetxt(os.path.join(self.WorkingDirectory, ii[:-4] + '_planenum.csv'), plane_num.T, delimiter=",")

            compiledata_perfish = np.vstack((fish_num.T, plane_num.T, calcium_dfof_norm))

            print np.shape(compiledata_perfish)

            # Save array as csv
            np.savetxt(os.path.join(self.WorkingDirectory, 'RawdataCSV', ii[:-4] + "_rawdata.csv"), compiledata_perfish,
                       delimiter=",")

    def convert_to_firing_rate(self):

        rawdatacsv_filenames = [f for f in os.listdir(os.path.join(self.WorkingDirectory, 'RawdataCSV')) if
                                f.endswith('.csv')]

        for ff in rawdatacsv_filenames[2:]:

            print 'Deconvolving File...', ff

            calciumtraces = np.loadtxt(os.path.join(self.WorkingDirectory, 'RawdataCSV', ff), delimiter=",")
            print np.shape(calciumtraces)

            firingrate = []
            denoisedcalicumtrace = []
            cellsused = np.array([])

            for ii in xrange(0, np.size(calciumtraces, 1)):
                fluor = calciumtraces[2:, ii]  # First two rows are fish and plane number

                print 'Deconvolving..', ii
                try:
                    deconvolvedresult = constrained_foopsi(fluor)
                except ZeroDivisionError:
                    print 'Skipping..Cell ', ii
                    continue
                except ValueError:
                    print 'Skipping..Cell ', ii
                    continue

                if np.ndim(deconvolvedresult[5]) > 1:
                    print 'Skipping..Cell ', ii
                    continue

                print np.ndim(deconvolvedresult[5])
                cellsused = np.vstack((cellsused, ii)) if np.size(cellsused) else ii
                firingrate.append(deconvolvedresult[5])
                denoisedcalicumtrace.append(deconvolvedresult[0])

            firingrate = np.asarray(np.vstack(firingrate)).T
            firingrate = np.vstack((calciumtraces[1, cellsused].T, firingrate))
            denoisedcalicumtrace = np.asarray(np.vstack(denoisedcalicumtrace)).T
            denoisedcalicumtrace = np.vstack((calciumtraces[1, cellsused].T, denoisedcalicumtrace))

            np.savetxt(os.path.join(self.WorkingDirectory, 'DeconvolveddataCSV', ff[:-4] + "_denoiseddata.csv"),
                       denoisedcalicumtrace, delimiter=",")
            np.savetxt(os.path.join(self.WorkingDirectory, 'DenoisedDataCSV', ff[:-4] + "_firingrate.csv"), firingrate,
                       delimiter=",")

            plt.plot(np.clip(firingrate[2:, :], 0, np.max(firingrate[2:, :])), '.')
            plt.savefig(os.path.join(WorkingDirectory, 'Images', ff[:-4] + '.png'))

    def test(self):
        mat_filenames = [f for f in os.listdir(self.WorkingDirectory) if f.endswith('.mat')]
        for ii in mat_filenames:
            alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, ii))
            calcium = alldata['CellZ5'][11:, :]

            row = alldata['CellZ5'][3, :]
            neuropil = alldata['NeuropilList']

            count = 0
            for jj in xrange(0, 5):
                A1 = calcium[:, row == jj + 1]
                A2 = A1[:, np.squeeze(neuropil[0][jj] == 0)]
                count += np.size(A2, 1)

            print 'In Fish..', ii, 'Total Cells ', count


if __name__ == '__main__':
    WorkingDirectory = '/Users/seetha/Desktop/Modelling/Data/Network/'

    if not os.path.exists(os.path.join(WorkingDirectory, 'RawdataCSV')):
        os.makedirs(os.path.join(WorkingDirectory, 'RawdataCSV'))
    if not os.path.exists(os.path.join(WorkingDirectory, 'DenoisedDataCSV')):
        os.makedirs(os.path.join(WorkingDirectory, 'DenoisedDataCSV'))
    if not os.path.exists(os.path.join(WorkingDirectory, 'DeconvolveddataCSV')):
        os.makedirs(os.path.join(WorkingDirectory, 'DeconvolveddataCSV'))
    if not os.path.exists(os.path.join(WorkingDirectory, 'Images')):
        os.makedirs(os.path.join(WorkingDirectory, 'Images'))

    Habenula = LoadCalciumTrace(WorkingDirectory)
    Habenula.get_data_from_matfile()
    # Habenula.convert_to_firing_rate()
    # Habenula.test()
