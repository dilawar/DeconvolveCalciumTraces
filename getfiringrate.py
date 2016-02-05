#Import stuff
import scipy.io
import numpy as np

#Load calcium trace given mat file and convert to CSV
class LoadCalciumTrace(object):
    def __init__(self, DataPath):
        self.DataPath = DataPath

    def get_matfile_convert_to_csv(self):
        All_Data = scipy.io.loadmat(self.DataPath)
        Calcium = All_Data['A_On_SubClusters']
        print np.shape(Calcium)


if __name__ == '__main__':
    DataPath = '/Users/seetha/Desktop/Modelling/Data/Blue_Con_Fish104-109.mat'
    Habenula = LoadCalciumTrace(DataPath)
    Habenula.get_matfile_convert_to_csv()