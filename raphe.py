"""raphe.py: 

A small network of raphe neurons.

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
import pylab 
import sys


"""
A network with rapheN raphe neurons and interN interneurons. Each rapheN
neurons recive an external excitatory synapse. If one of those input is
shutdown, this network should shut down.
"""

rapheN = 6
interN = 3

monitors = []

stimulus = TimedArray(np.array([45, 1000]), dt=1500*ms)

raphe = NeuronGroup( rapheN
        , '''
            dv/dt = (ge+gi-(v+45*mV))/(40*ms) : volt
            dge/dt = -ge/(5*ms) : volt
            dgi/dt = -gi/(10*ms) : volt

        '''
        , threshold='v > -50*mV'
        , reset='v = -70*mV'
        )

# This is like previous group but only single neuron. We control this neuron
# using a TimedArray and it shuts off at 1500 millisec.
rapheWithClamp = NeuronGroup( 1
        , '''
            dv/dt = (ge+gi-(v+stimulus(t)*mV))/(40*ms) : volt
            dge/dt = -ge/(5*ms) : volt
            dgi/dt = -gi/(10*ms) : volt

        '''
        , threshold='v > -50*mV'
        , reset='v = -70*mV'
        )

rapheMonitor = SpikeMonitor( raphe )
rapheMonitor1 = SpikeMonitor( rapheWithClamp )

# I suspect interneurons to be very fast spiking with tau less than 1ms. These
# neurons also have low threhold. It is known that some interneurons fires as
# fast as 35Hz.
interneuronNet = NeuronGroup( interN
        , '''
            dv/dt = (ge+gi-(v+49*mV))/(5*ms) : volt
            dge/dt = -ge/(2*ms) : volt
            dgi/dt = -gi/(2*ms) : volt
        '''
        , threshold='v >-50*mV'
        , reset = 'v = -70*mV'
        )

# These interneurons make very weak inhibitory but many syapases onto each
# other.
interSyn = Synapses( interneuronNet, interneuronNet, pre='gi-=9*mV')
probConnection = 0.0 /interN
interSyn.connect( True, p = probConnection)

# However, raphe neurons make strong inhibitory synapses onto interneurons.
for rapheG in [ raphe, rapheWithClamp]:
    riToii = Synapses( rapheG, interneuronNet, pre='ge+=5*mV')
    riToii.connect( True, p = 0.5 )

interMonitor = SpikeMonitor( interneuronNet )

run( 3*second )
pylab.subplot(3, 1, 1)
plot( interMonitor.t, interMonitor.i, '.' )
pylab.title( 'Interneurons, p(IN --| IN) = %s' % probConnection  )
pylab.subplot(3, 1, 2)
plot( rapheMonitor.t, rapheMonitor.i, '.' )
pylab.subplot(3, 1, 3)
plot( rapheMonitor1.t, rapheMonitor1.i, '.' )
pylab.title( 'Raphe neurons' )
pylab.savefig( "%s.png" % sys.argv[0] )

