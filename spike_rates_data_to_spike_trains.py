#!/usr/bin/env python

"""

Given a spike train data, generate spike trains.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import config as c
import numpy as np
import sys
import os

def get_firing_data( firing_rate_file, region_index = 1 ):
    print( '[INFO] Reading file %s' % firing_rate_file )
    with open(firing_rate_file, "r") as f:
        lines = f.read().split('\n')
    header, data = np.fromstring(lines[0],sep=','), lines[1:]
    use_cols = [ i for i, e in enumerate(header) if int(float(e)) == region_index ]
    print('[INFO] Reading %s out of %s columns' % (len(use_cols), header.size))
    fishName = os.path.split(firing_rate_file)[-1]
    # Clip the negative values
    d = np.genfromtxt(firing_rate_file
            , delimiter=','
            , skip_header=True
            , usecols = use_cols
            )
    d = np.clip(d, 0, d.max())
    return d.T

def generate_spikes( firing_rates ):
    """Given firing rates, generate spikes """
    spikesMat = []
    print("[DEBUG] Firing rate matrix shape: %s" % str(firing_rates.shape))
    gen_spikes = np.vectorize( lambda x, f: 1.0 if x < f else 0.0 )
    for col in firing_rates:
        spikesRow = []
        # Each entry is 1 second apart. We create possible spikes with given
        # firing rate at this moment and average firing rate in cofig file.
        for r in col:
            probFiring = r / c.firing_rate_in_lhb
            samples = np.random.random( c.firing_rate_in_lhb )
            spikes = gen_spikes(samples, probFiring)
            spikesRow.append( spikes )
        spikesRow = np.concatenate( spikesRow )
        spikesMat.append( spikesRow )
    spikesMat = np.vstack( spikesMat )
    return spikesMat 


def main( in_file ):
    firingRates = get_firing_data( in_file )
    spikesMat = generate_spikes( firingRates )
    ## Saving generated spike data to 
    spikeFile = "%s_deconvoluted_firing_rate.csv" % in_file 
    comment = '# firing_rate = %s\n' % c.firing_rate_in_lhb
    np.savetxt( spikeFile, spikesMat, delimiter = ',', footer = comment )
    print('[INFO] Done writing spiking data to %s' % spikeFile)

if __name__ == '__main__':
    inFile = sys.argv[1]
    main( inFile )
