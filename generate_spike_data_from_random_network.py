#!/usr/bin/env python

"""generate_spike_data_from_random_network.py: 

    Create a random netwok with given parameters and generate spike trains.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"


from brian2 import *
import networkx as nx
import helper
import pylab 
import spike_to_gcamp as s2g

#prefs.codegen.target = 'cython'

# Construct LHB
N = 100
# Fraction of LHB neurons which are inhibitory
inhibFrac = 0.3
excFrac = 0.6
offFrac = 0.1

total = inhibFrac + excFrac + offFrac
assert np.isclose(total, 1.0), "Expected 1.0 got %s" % total

# Synaptic weights
lhbExcSynapticWeight = 1.62
lhbInhibSynapticWeight = 9     # Should be positive

# Model of LHB neurons.
tau = 10*ms
lhbEqs = '''
dv/dt = (ge+gi-(v+49*mV))/(20*ms) : volt
dge/dt = -ge/(5*ms) : volt
dgi/dt = -gi/(10*ms) : volt

'''

runTime = 20

print('[INFO] Constructing LHB with %s neurons' % N )
print('[INFO]  Eq : %s' % lhbEqs )
lhb = NeuronGroup(N
        , lhbEqs
        , threshold='v>-49.05*mV'
        , reset='v=-60*mV'
        , 
        )
lhb.v = -60*mV

# Inhibitory group
lhbInhib = lhb[0:int(inhibFrac*N)]
print("[INFO] Total inhibitory neurons: %s" % len(lhbInhib))
# Excitatory group.
lhbExc = lhb[int(inhibFrac*N):int((inhibFrac+excFrac)*N)+1]
print("[INFO] Total excitatory neurons %s" % len(lhbExc))
lhbOff = lhb[-int(offFrac*N):]
print('[INFO] Total off neurons: %s' % len(lhbOff))
total = len(lhbExc) + len(lhbInhib) + len(lhbOff) 
assert total == N, "Expecting %s, got %s" % (N, total)

## NOTE: Connectivity in LHB is not known.
excSynapses = Synapses( lhbExc, lhb, pre='ge+=%f*mV' % lhbExcSynapticWeight)
excSynapses.connect( True, p = 0.01 )    # p is the probability of release

inhSynapse = Synapses( lhbInhib, lhb, pre='gi-=%f*mV' % lhbInhibSynapticWeight)
inhSynapse.connect( True, p = 0.01 )


# Now create some more neuron which are input to excitatory neurons. These
# neurons are stimulated by current pulse.
onArray = np.random.random( int(2/defaultclock.dt) )
offArray = np.zeros( int(2/defaultclock.dt))
stimulus = TimedArray( 
        np.hstack( [ np.hstack([ onArray, offArray ]) for x in range( runTime / 2) ] )
        , dt= defaultclock.dt
        )

blueLightNeuron = NeuronGroup( 1
        , 'dv/dt = (-v + stimulus(t))/(10*ms) : 1'
        , threshold='v>=0.5', reset='v=0.0'
        )
blueLightNeuron.v = '0.5*rand()'

# These neurons turns on excitatory 
inputExcSynapses = Synapses( blueLightNeuron, lhbExc
        , pre='ge+=%f*mV' % lhbExcSynapticWeight
        )

inputExcSynapses.connect( True, p = 0.99 )

# These synapses tuns on lhbInhib neurons.
inputInhibSynapses = Synapses(blueLightNeuron, lhbInhib
        , pre='gi-=%f*mV' % lhbInhibSynapticWeight
        )
inputInhibSynapses.connect( True, p = 0.99 )

#pylab.figure()
#pylab.plot( stimulus.values )
#pylab.show( )

lhbMonitor = SpikeMonitor( lhb )
inputMonitor = SpikeMonitor( blueLightNeuron )

def main( ):
    net = Network( collect() )
    net.add( [ lhbMonitor, inputMonitor ] )
    net.run( runTime*second )
    pylab.subplot(2, 1, 1)
    plot( lhbMonitor.t, lhbMonitor.i, '.')

    binInterval = 0.5
    nspikesDict = helper.spikes_in_interval( lhbMonitor, runTime, binInterval)

    dtForFluroscenceComputation = 0.01
    rows = []
    for k in nspikesDict.keys():
        #print('[DEBUG] ======== Bins for neuron %s' % k )
        vec = nspikesDict[k]
        #print('         %s' % vec)
        r = np.zeros( runTime / dtForFluroscenceComputation )
        for _bin in vec:
            _bin = np.sort( _bin )
            if _bin.shape[0] > 0:
                r = s2g.spikes_to_fluroscence(r, _bin, dtForFluroscenceComputation)
        rows.append( r )

    pylab.subplot(2, 1, 2)
    pylab.plot( rows[4] )
    pylab.plot( rows[5] )
    pylab.savefig( './spikes_raster.png' )

if __name__ == '__main__':
    main()
