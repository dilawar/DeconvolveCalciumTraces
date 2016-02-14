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
import networkx as nx


"""
A network with rapheN raphe neurons and interN interneurons. Each rapheN
neurons recive an external excitatory synapse. If one of those input is
shutdown, this network should shut down.
"""


rapheN = 9
interN = 9
inputN = rapheN - 1

# Add the nodes.
graph_ = nx.DiGraph( ranksep = '1.0', nodesep = '1.0' )

rapheNode =  [ ('RA%d' % x) for x in range(rapheN) ] 
interNode = [ ('IN%d' % x) for x in range(interN) ] 
inputNode = [ ('i_%d' % x) for x in range(inputN) ] 

for n in rapheNode:
    graph_.add_node( n, label = n, color = 'blue' )
for n in interNode:
    graph_.add_node( n, label = n, color = 'red' )
for n in inputNode:
    graph_.add_node( n, label = n,  color = 'yellow' )

for e in zip(inputNode, rapheNode):
    graph_.add_edge( *e )

for e in zip(rapheNode, interNode):
    graph_.add_edge( *e , arrowhead = 'diamond' )

monitors = []

titleText = ""

shutdown = 1.5
stimulus = TimedArray(np.array([45, 58, 45]), dt=shutdown*second)

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
titleText += "Among all input neurons, one neuron shuts down at %s sec" % shutdown
titleText += " shown by red X"

inputMonitor = SpikeMonitor( inputNet )
inputClampedMonitor = SpikeMonitor( inputWithClamp )


# I suspect interneurons to be very fast spiking with tau less than 1ms. These
# neurons also have low threhold. It is known that some interneurons fires as
# fast as 35Hz.
interneuronNet = NeuronGroup( interN
        , '''
            dv/dt = (ge+gi-(v+45*mV))/(20*ms) : volt
            dge/dt = -ge/(7*ms) : volt
            dgi/dt = -gi/(7*ms) : volt
        '''
        , threshold='v > -46*mV'
        , reset = 'v = -60*mV'
        )
interMonitor = SpikeMonitor( interneuronNet )

rapheNet = NeuronGroup( rapheN
        , '''
            dv/dt = (ge+gi-(v+49*mV))/(20*ms) : volt
            dge/dt = -ge/(5*ms) : volt
            dgi/dt = -gi/(10*ms) : volt

        '''
        , threshold='v > -40*mV'
        , reset='v = -70*mV'
        )
rapheMonitor = SpikeMonitor( rapheNet )


# Input-net makes excitatory connections onto raphe. These connections are
# strong but one to one.
inputSyn = Synapses( inputNet, rapheNet, pre = 'v_post+=20*mV' )
inputSyn.connect( 'i+1==j' )

inputSyn1 = Synapses( inputWithClamp, rapheNet, pre = 'v_post+=20*mV' )
inputSyn1.connect( 'j==0' )

# Raphe neurons in turn one to one strong inhibitory connections onto
# interneurons.
raphe2Interneurons = Synapses( rapheNet, interneuronNet, pre='gi-=10*mV')
raphe2Interneurons.connect( 'i==j' )

# Interneurons makes weak inhibtory synapses onto raphe. In this version, these
# are sparse. To make sure that effect is similar to previous version, one
# hypothise that interneurons are exciting their neighbours.
inter2Raphe = Synapses( interneuronNet, rapheNet, pre='gi-=6*mV' )
probOfConnection = 1.0
inter2Raphe.connect( 'abs(i-j) <=3 and i!=j', p=probOfConnection)

# excite your neighbour
inter2interExc = Synapses( interneuronNet, interneuronNet, pre='ge+=5*mV')
inter2interExc.connect( 'abs(i-j)<=2 and i!=j' )

titleText += '\nProbabilty I --| R = %s, neighbourhood=%s' %(probOfConnection,4)
stamp = datetime.datetime.now().isoformat()
titleText += '\nSimulated on: \n%s' % stamp

# Connect in graph as well.
for n in interNode:
    for nn in rapheNode:
        graph_.add_edge( n, nn, arrowshape='tee' )

def simulate( runtime ):
    run( runtime*second )
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
    pylab.suptitle( titleText, fontsize=8, verticalalignment = 'top' )
    pylab.tight_layout()
    outfile = '%s.png' % sys.argv[0]
    print('[INFO] Writing output to %s' % outfile)
    pylab.savefig( "%s.png" % sys.argv[0] )

def write_graphviz( ):
    # Generate a networkx graph which represent what we are simulating.
    global graph_ 
    # Add connections here and we are done.
    nx.write_dot( graph_, 'network.dot' )
    #nx.draw( graph_ )
    #pylab.show()

def main( ):
    simulate( runtime = 7 )
    #write_graphviz( )

if __name__ == '__main__':
    main()
