'''
Simple LegoOS experiment, which sets up a pComponent, a mComponent and 
a sComponent connected through ethernet.
'''
import simbricks.orchestration.experiments as exp
import simbricks.orchestration.simulators as sim

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components import LegoModuleNode, LegoModuleQemuHost

SYNC        = os.getenv('LEGOSIM_SYNC')
SCOMP_MAC   = os.getenv('LEGOSIM_SCOMP_MAC')

if SYNC is None or SCOMP_MAC is None:
    sys.stderr.write('Environment variables not set.\n')
    sys.exit(1)

PCOMP_IMG   = os.getenv('LEGOSIM_PCOMP_IMG')
MCOMP_IMG   = os.getenv('LEGOSIM_MCOMP_IMG')

SYNC = True if SYNC == 1 else False
SYNC_MODE = 2 if SYNC else 0

e = exp.Experiment(name='LegoOS_1p1m1s')
e.checkpoint = True

# storage component
scomp_node = LegoModuleNode(['ethfit.ko', 'storage.ko'])

scomp = LegoModuleQemuHost(scomp_node)
scomp.sync = SYNC
scomp.name = 'StorageComponent'
scomp.wait = True
e.add_host(scomp)

scomp_nic = sim.E1000NIC()
scomp_nic.sync_mode = SYNC_MODE
scomp_nic.mac = SCOMP_MAC
scomp.add_nic(scomp_nic)
e.add_nic(scomp_nic)

# TODO: pcomp and mcomp

# network
network = sim.SwitchNet()
network.sync = SYNC
scomp_nic.set_network(network)
e.add_network(network)

experiments = [e]
