'''
Simple LegoOS experiment, which sets up a pComponent and a mComponent connected
through ethernet.
'''
from simbricks.orchestration.experiments import Experiment
from simbricks.orchestration.simulators import E1000NIC, SwitchNet

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components import LegoOSQemuHost

SYNC = os.getenv('LEGOSIM_SYNC')
PCOMPONENT_IMG = os.getenv('LEGOSIM_PCOMPONENT_IMG')
MCOMPONENT_IMG = os.getenv('LEGOSIM_MCOMPONENT_IMG')

if SYNC is None or PCOMPONENT_IMG is None or MCOMPONENT_IMG is None:
    sys.stderr.write(
        'LEGOSIM_SYNC LEGOSIM_PCOMPONENT_IMG or LEGOSIM_MCOMPONENT_IMG not specified')
    exit(1)

SYNC = True if SYNC == 1 else False
SYNC_MODE = 2 if SYNC else 0

e = Experiment(name='LegoOS_1p1m')
e.checkpoint = True  # use checkpoint and restore to speed up simulation

# pcomponent
pcomponent = LegoOSQemuHost(PCOMPONENT_IMG, memory='8G', cores=8, debug=False, debug_port=9000)
pcomponent.sync = SYNC
pcomponent.name = 'pcomponent'
pcomponent.wait = True
e.add_host(pcomponent)

# pcomponent NIC
pcomponent_nic  = E1000NIC()
pcomponent_nic.sync_mode = SYNC_MODE
pcomponent_nic.mac = '52:54:00:12:34:56'
pcomponent.add_nic(pcomponent_nic)
e.add_nic(pcomponent_nic)

# mcomponent
mcomponent = LegoOSQemuHost(MCOMPONENT_IMG, memory='8G', cores=8, debug=False, debug_port=9001)
mcomponent.sync = SYNC
mcomponent.name = 'mcomponent'
mcomponent.wait = True
e.add_host(mcomponent)

# mcomponent NIC
mcomponent_nic = E1000NIC()
mcomponent_nic.sync_mode = SYNC_MODE
mcomponent_nic.mac = '52:54:00:12:34:57'
mcomponent.add_nic(mcomponent_nic)
e.add_nic(mcomponent_nic)

# network
network = SwitchNet()
network.sync = SYNC
pcomponent_nic.set_network(network)
mcomponent_nic.set_network(network)
e.add_network(network)

experiments = [e]
