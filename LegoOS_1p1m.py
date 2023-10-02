'''
Simple LegoOS experiment, which sets up a pComponent and a mComponent connected
through ethernet.
'''
import simbricks.orchestration.experiments as exp
import simbricks.orchestration.simulators as sim

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components import LegoOSNode, LegoOSQemuHost

SYNC = os.getenv('LEGOSIM_SYNC')

PCOMP_MAC = os.getenv('LEGOSIM_PCOMP_MAC')
MCOMP_MAC = os.getenv('LEGOSIM_MCOMP_MAC')

PCOMP_IMG = os.getenv('LEGOSIM_PCOMP_IMG')
MCOMP_IMG = os.getenv('LEGOSIM_MCOMP_IMG')

if SYNC is None or PCOMP_MAC is None or MCOMP_MAC is None or \
    PCOMP_IMG is None or MCOMP_IMG is None:
    sys.stderr.write('Environment variables not set.\n')
    sys.exit(1)

SYNC = True if SYNC == '1' else False
SYNC_MODE = 2 if SYNC else 0

e = exp.Experiment(name='LegoOS_1p1m')
e.checkpoint = True  # use checkpoint and restore to speed up simulation

# network
network = sim.SwitchNet()
network.sync = SYNC
e.add_network(network)

# pComponent
pcomp_nodec = LegoOSNode(PCOMP_IMG)
pcomp = LegoOSQemuHost(pcomp_nodec, debug=False, debug_port=7500)
pcomp.name = 'p-component'
pcomp.wait = True
e.add_host(pcomp)

# pComponent NIC
pcomp_nic = sim.E1000NIC()
pcomp_nic.mac = PCOMP_MAC
pcomp.add_nic(pcomp_nic)
pcomp_nic.set_network(network)
e.add_nic(pcomp_nic)

# mComponent
mcomp_nodec = LegoOSNode(MCOMP_IMG)
mcomp = LegoOSQemuHost(mcomp_nodec, debug=False, debug_port=7501)
mcomp.name = 'm-component'
mcomp.wait = True
e.add_host(mcomp)

# mComponent NIC
mcomp_nic = sim.E1000NIC()
mcomp_nic.mac = MCOMP_MAC
mcomp.add_nic(mcomp_nic)
mcomp_nic.set_network(network)
e.add_nic(mcomp_nic)

# synchronization
for s in e.all_simulators():
    s.sync = SYNC
    s.sync_mode = SYNC_MODE

experiments = [e]
