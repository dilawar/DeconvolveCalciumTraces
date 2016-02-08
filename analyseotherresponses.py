import os
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.cluster.vq import kmeans, vq
from scipy.signal import detrend


class Getotherresponses(object):
    def __init__(self, WorkingDirectory, stimulus_on_time, stimulus_off_time, smooth_window, numclusters):
        self.WorkingDirectory = WorkingDirectory
        self.stimulus_on_time = stimulus_on_time
        self.stimulus_off_time = stimulus_off_time
        self.smooth_window = smooth_window
        self.numclusters = numclusters

    def LoadData(self):
        mat_filenames = [f for f in os.listdir(self.WorkingDirectory) if f.endswith('.mat')]

        for ii in mat_filenames:

            print 'Collecting File...', ii
            alldata = scipy.io.loadmat(os.path.join(self.WorkingDirectory, ii))

            # Get data and normalize
            calcium = alldata['CellZ5'][11:, :]
            # Seperate neuropil data
            row = alldata['CellZ5'][3, :]
            neuropil = alldata['NeuropilList']

            A2 = []
            A3 = np.array([])
            for jj in xrange(0, 5):
                A1 = calcium[:, row == jj + 1]
                A2 = A1[:, np.squeeze(neuropil[0][jj] == 0)]
                A3 = np.hstack((A3, A2)) if A3.size else A2

            calcium = A3

            calcium_detrend = self.detrend_calcium_trace(calcium)

            calcium_dfof = (calcium_detrend - np.mean(calcium_detrend[10:46, :], 0)) / \
                           (np.std(calcium_detrend[10:46, :], 0) + 0.001)

            calcium_signals_thresh = calcium_dfof[:, np.max(calcium_dfof, 0) > 3]
            print "Before Thresh %s After Thresh %s " % (np.shape(calcium_dfof), np.shape(calcium_signals_thresh))

            # Smooth data
            start_time = time.time()
            calcium_smooth = self.smooth_calcium_trace(calcium_signals_thresh, windowlen=self.smooth_window)

            print "Elapsed time for smoothing is %s seconds" % (time.time() - start_time)

            # Plot some stuff
            fs = plt.figure()
            gs = plt.GridSpec(2, 1, height_ratios=[2, 1])

            ax1 = fs.add_subplot(gs[0, :])
            plt.imshow(calcium_smooth.T, cmap='seismic', aspect='auto', vmin=-2, vmax=2)
            plt.colorbar()
            self.plot_vertical_lines_onset()
            self.plot_vertical_lines_offset()

            ax1 = fs.add_subplot(gs[1, :])
            plt.plot(np.mean(calcium_smooth, 1))
            plt.xlim((0, np.size(calcium_smooth, 0)))
            self.plot_vertical_lines_onset()
            self.plot_vertical_lines_offset()
            plt.tight_layout()

            plt.savefig('/Users/seetha/Desktop/Temp_Figures/' + ii[:-4] + 'smooth.png')

            np.savetxt(os.path.join(self.WorkingDirectory, 'ClusteringSignals', ii[:-4] + 'calcium_smooth.csv'),
                       calcium_smooth, delimiter=",")

    def kmeans_test(self):
        csv_filenames = [f for f in os.listdir(os.path.join(self.WorkingDirectory, 'ClusteringSignals')) if
                         f.endswith('.csv')]

        for ii in csv_filenames:
            print ii
            data = np.loadtxt(os.path.join(self.WorkingDirectory, 'ClusteringSignals', ii), delimiter=",")
            data = data.T

            # computing K-Means with K = 2 (2 clusters)
            centroids, _ = kmeans(data, self.numclusters)
            # assign each sample to a cluster
            idx, _ = vq(data, centroids)

            # some plotting using numpy's logical indexing
            plt.figure()
            num_such_clusters = np.zeros((self.numclusters, 1))
            for jj in xrange(0, self.numclusters):
                num_such_clusters[jj] = np.shape(data[idx == jj, :])[0]
                plt.plot(np.mean(data[idx == jj, :], 0),
                         label='Cluster %s Cells %s' % (jj, num_such_clusters[jj]))
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.xlim((0, np.size(data, 1)))
            self.plot_vertical_lines_onset()
            self.plot_vertical_lines_offset()
            plt.savefig('/Users/seetha/Desktop/Temp_Figures/' + ii[:-4] + 'kmean.png', bbox_inches='tight')

    def detrend_calcium_trace(self, calcium_trace):
        detrended = np.zeros(np.shape(calcium_trace))
        for ss in xrange(0, np.size(calcium_trace, 1)):
            detrended[:, ss] = detrend(calcium_trace[:, ss])
        return detrended

    def smooth_calcium_trace(self, calcium_trace, windowlen):
        smoothed_calcium_trace = np.zeros(np.shape(calcium_trace))
        for ss in xrange(0, np.size(calcium_trace, 1)):
            smoothed_calcium_trace[:, ss] = self.smooth_hanning(calcium_trace[:, ss], windowlen)
        return smoothed_calcium_trace

    @staticmethod
    def smooth_hanning(x, window_len):
        s = np.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
        w = np.ones(window_len, 'd')
        y = np.convolve(w / w.sum(), s, mode='valid')
        # print np.shape(y[window_len / 2:-window_len / 2 + 1])
        return y[:-window_len + 1]

    def plot_vertical_lines_onset(self):
        for ii in xrange(0, np.size(self.stimulus_on_time)):
            plt.axvline(x=self.stimulus_on_time[ii], linestyle='-', color='k', linewidth=2)

    def plot_vertical_lines_offset(self):
        for ii in xrange(0, np.size(self.stimulus_off_time)):
            plt.axvline(x=self.stimulus_off_time[ii], linestyle='--', color='k', linewidth=2)


if __name__ == '__main__':
    WorkingDirectory = '/Users/seetha/Desktop/Modelling/Data/Network/'
    stimulus_on_time = [46, 98, 142, 194]
    stimulus_off_time = [65, 117, 161, 213]
    numclusters = 10
    smooth_window = 20

    if not os.path.exists(os.path.join(WorkingDirectory, 'ClusteringSignals')):
        os.makedirs(os.path.join(WorkingDirectory, 'ClusteringSignals'))
    Habenula = Getotherresponses(WorkingDirectory, stimulus_on_time, stimulus_off_time, smooth_window, numclusters)
    CalciumSignal = Habenula.LoadData()
    Habenula.kmeans_test()
