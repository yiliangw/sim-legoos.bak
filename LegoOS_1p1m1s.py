'''
Simple LegoOS experiment, which sets up a pComponent, a mComponent and 
a sComponent connected through ethernet.
'''
import simbricks.orchestration.experiments as exp
import simbricks.orchestration.simulators as sim

import sys
import os
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR_PATH)
from components import LegoOSNode, LegoModuleNode, LegoModuleQemuHost, LegoOSQemuHost, LegoModuleLoading

SYNC        = os.getenv('LEGOSIM_SYNC')

PCOMP_MAC   = os.getenv('LEGOSIM_PCOMP_MAC')
MCOMP_MAC   = os.getenv('LEGOSIM_MCOMP_MAC')
SCOMP_MAC   = os.getenv('LEGOSIM_SCOMP_MAC')

PCOMP_IMG   = os.getenv('LEGOSIM_PCOMP_IMG')
MCOMP_IMG   = os.getenv('LEGOSIM_MCOMP_IMG')

if SYNC is None or PCOMP_MAC is None or MCOMP_MAC is None or \
    SCOMP_MAC is None or PCOMP_IMG is None or MCOMP_IMG is None:
    sys.stderr.write('Environment variables not set.\n')
    sys.exit(1)


SYNC = True if SYNC == '1' else False
SYNC_MODE = 2 if SYNC else 0

e = exp.Experiment(name='LegoOS_1p1m1s')
e.checkpoint = True

# processor component
pcomp_nodec = LegoOSNode(PCOMP_IMG)
pcomp = LegoOSQemuHost(pcomp_nodec, debug=False, debug_port=7500)
pcomp.name = 'p-component'
pcomp.wait = True
e.add_host(pcomp)

pcomp_nic = sim.E1000NIC()
pcomp_nic.mac = PCOMP_MAC
pcomp.add_nic(pcomp_nic)
e.add_nic(pcomp_nic)

# memory component
mcomp_nodec = LegoOSNode(MCOMP_IMG)
mcomp = LegoOSQemuHost(mcomp_nodec, debug=False, debug_port=7501)
mcomp.name = 'm-component'
mcomp.wait = False
e.add_host(mcomp)

mcomp_nic = sim.E1000NIC()
mcomp_nic.mac = MCOMP_MAC
mcomp.add_nic(mcomp_nic)
e.add_nic(mcomp_nic)

# storage component
scomp_app = LegoModuleLoading(module_list=['ethfit.ko', 'storage.ko'], resource_list=[('test.py', f'{DIR_PATH}/test.py')])
scomp_nodec = LegoModuleNode()
scomp_nodec.app = scomp_app
scomp = LegoModuleQemuHost(scomp_nodec, debug=False, debug_port=7502)
scomp.name = 's-component'
scomp.wait = False
e.add_host(scomp)

scomp_nic = sim.E1000NIC()
scomp_nic.mac = SCOMP_MAC
scomp.add_nic(scomp_nic)
e.add_nic(scomp_nic)

# network
network = sim.SwitchNet()
pcomp_nic.set_network(network)
mcomp_nic.set_network(network)
scomp_nic.set_network(network)
e.add_network(network)

# synchronization
SYNC_PERIOD = 2000
for s in e.all_simulators():
    s.sync = SYNC
    s.sync_mode = SYNC_MODE
    s.sync_period = SYNC_PERIOD

# latency
PCI_LATENCY = SYNC_PERIOD
ETH_LATENCY = SYNC_PERIOD
for s in e.hosts:
    s.pci_latency = PCI_LATENCY
for s in e.nics:
    s.pci_latency = PCI_LATENCY
    s.eth_latency = ETH_LATENCY
for s in e.networks:
    s.eth_latency = ETH_LATENCY

experiments = [e]
