"""minimal_network.py

A small network with 'single cell shutting down whole network' behaviour.

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


rapheN = 9
interN = 9
inputN = rapheN - 2

monitors = []

footer = ""

shutdown = 1.5
stimulus = TimedArray(np.array([45, 58]), dt=shutdown*second)

inputNet = NeuronGroup( inputN 
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
inputWithClamp = NeuronGroup( 1
        , '''
            dv/dt = (ge+gi-(v+stimulus(t)*mV))/(40*ms) : volt
            dge/dt = -ge/(5*ms) : volt
            dgi/dt = -gi/(10*ms) : volt

        '''
        , threshold='v > -50*mV'
        , reset='v = -70*mV'
        )
footer += "Among all input neurons, one neuron shuts down at %s sec" % shutdown
footer += " shown by red X"

inputMonitor = SpikeMonitor( inputNet )
inputClampedMonitor = SpikeMonitor( inputWithClamp )


# I suspect interneurons to be very fast spiking with tau less than 1ms. These
# neurons also have low threhold. It is known that some interneurons fires as
# fast as 35Hz.
interneuronNet = NeuronGroup( interN
        , '''
            dv/dt = (ge+gi-(v+49*mV))/(5*ms) : volt
            dge/dt = -ge/(1*ms) : volt
            dgi/dt = -gi/(2*ms) : volt
        '''
        , threshold='v >-50*mV'
        , reset = 'v = -70*mV'
        )
interMonitor = SpikeMonitor( interneuronNet )

rapheNet = NeuronGroup( rapheN
        , '''
            dv/dt = (ge+gi-(v+45*mV))/(40*ms) : volt
            dge/dt = -ge/(5*ms) : volt
            dgi/dt = -gi/(10*ms) : volt

        '''
        , threshold='v > -50*mV'
        , reset='v = -70*mV'
        )
rapheMonitor = SpikeMonitor( rapheNet )


# Input-net makes excitatory connections onto raphe. These connections are
# strong but one to one.
inputSyn = Synapses( inputNet, rapheNet, pre = 'ge+=10*mV' )
inputSyn.connect( True, p = 0.01 )

inputSyn = Synapses( inputWithClamp, rapheNet, pre = 'ge+=10*mV' )
#inputSyn.connect( 'i==j+2' )

# Raphe neurons in turn one to one strong inhibitory connections onto
# interneurons.
raphe2Interneurons = Synapses( rapheNet, interneuronNet, pre='gi-=10*mV')
#raphe2Interneurons.connect( 'i==j' )

# Interneurons makes weak inhibtory synapses onto raphe, These connections are
# dense.
inter2Raphe = Synapses( interneuronNet, rapheNet, pre='gi-=1*mV' )
#inter2Raphe.connect( True, p= 1.0)


run( 3*second )
marker = '.'
pylab.subplot(4, 1, 2)
pylab.plot( inputMonitor.t, inputMonitor.i, marker)
plot( inputClampedMonitor.t, inputClampedMonitor.i, 'x' )
pylab.title( 'Input spikes')

pylab.subplot(4, 1, 3)
plot( interMonitor.t, interMonitor.i, marker ) 

pylab.subplot(4, 1, 4)
plot( rapheMonitor.t, rapheMonitor.i, marker ) 
pylab.title( 'Raphe neurons' )
pylab.suptitle( footer, fontsize=8, verticalalignment = 'bottom' )
pylab.tight_layout()
outfile = '%s.png' % sys.argv[0]
print('[INFO] Writing output to %s' % outfile)
pylab.savefig( "%s.png" % sys.argv[0] )

