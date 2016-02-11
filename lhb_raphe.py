"""lhb_raphe.py: 

A network of LHB and Raphe.

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
import helper
import pylab 

# Construct LHB
lhbN = 100
# Fraction of LHB neurons which are inhibitory
inhibFrac = 0.4
excFrac = 1.0 - inhibFrac

total = inhibFrac + excFrac
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

runTime = 10

print('[INFO] Constructing LHB with %s neurons' % lhbN )
print('[INFO]  Eq : %s' % lhbEqs )
lhb = NeuronGroup(lhbN
        , lhbEqs
        , threshold='v>-49.05*mV'
        , reset='v=-60*mV'
        )
lhb.v = '-60*mV*rand()'

# These neurons makes very sparse connection among themselves. Here we produce a
# spontenous activity.
lhbInhib = lhb[0:int(inhibFrac*lhbN)]
print("[INFO] Total inhibitory neurons: %s" % len(lhbInhib))
# Excitatory group.
lhbExc = lhb[int(inhibFrac*lhbN):int((inhibFrac+excFrac)*lhbN)+1]
print("[INFO] Total excitatory neurons %s" % len(lhbExc))
total = len(lhbExc) + len(lhbInhib) 
assert total == lhbN, "Expecting %s, got %s" % (lhbN, total)

## NOTE: Connectivity in LHB is not known.
excSynapses = Synapses( lhbExc, lhb, pre='ge+=%f*mV' % lhbExcSynapticWeight)
excSynapses.connect( True, p = 0.01 )    # p is the probability of release
inhSynapse = Synapses( lhbInhib, lhb, pre='gi-=%f*mV' % lhbInhibSynapticWeight)
inhSynapse.connect( True, p = 0.01 )

lhbMonitor = SpikeMonitor( lhb )

## Now create Raphe
rapheN = 15

# Model of LHB neurons.
tau = 10*ms
rapheEq = '''
dv/dt = (ge+gi-(v+49*mV))/(20*ms) : volt
dge/dt = -ge/(5*ms) : volt
dgi/dt = -gi/(10*ms) : volt

'''
raphe = NeuronGroup(lhbN, rapheEq, threshold='v>-49.5*mV', reset='v=-60*mV')
raphe.v = '-50*mV*rand()'
# and some inhibitory interneurons.
interNeurons = NeuronGroup(rapheN, rapheEq, threshold='v>-49.5*mV', reset='v=-60*mV')
interNeurons.v = '-50*mV*rand()'

# lhb makes connection to these neurons. Excitatory neurons make excitatory
# connection while inhibitory neurons makes inhibitory synapses.
e1Syn = Synapses( lhb, raphe, pre='ge+=%f*mV' % lhbExcSynapticWeight)
e2Syn = Synapses( lhb, interNeurons, pre='ge+=%f*mV' % lhbExcSynapticWeight)
# 0.01 is 1 synapse onto each raphe neuron (on avg)
e1Syn.connect( True, p = (3*(lhbInhibSynapticWeight /
    lhbExcSynapticWeight))/lhbN)
e2Syn.connect( True, p = 0.01 ) 

# Interneurons make inhibitory synapse onto raphe
interSyn = Synapses( interNeurons, raphe, pre='gi-=%f*mV' % lhbInhibSynapticWeight)
interSyn.connect( True, p = 4.0/rapheN )

rapheMonitor = SpikeMonitor( raphe )
interneuronsMonitor = SpikeMonitor( interNeurons )

def main( ):
    run( runTime*second )
    pylab.subplot(3, 1, 1)
    plot( lhbMonitor.t, lhbMonitor.i, '.')
    pylab.subplot(3, 1, 2)
    plot( rapheMonitor.t, rapheMonitor.i, '.' )
    pylab.subplot(3, 1, 3)
    plot( interneuronsMonitor.t, interneuronsMonitor.i, '.' )
    pylab.show()

if __name__ == '__main__':
    main()
