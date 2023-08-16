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

SYNC = False
SYNC_MODE = 2 if SYNC else 0

e = Experiment(name='LegoOS_1p1m')
e.checkpoint = True  # use checkpoint and restore to speed up simulation

img_prefix = os.path.abspath(os.path.dirname(__file__) + '/images')
pcomponent_img_path = img_prefix + '/1p1m_pcomponent.bzImage'
mcomponent_img_path = img_prefix + '/1p1m_mcomponent.bzImage'

# node_0
pcomponent = LegoOSQemuHost(pcomponent_img_path, memory='8G', cores=8, debug=False)
pcomponent.sync = SYNC
pcomponent.name = 'pcomponent'
pcomponent.wait = True
e.add_host(pcomponent)

# node_0 NIC
pcomponent_nic  = E1000NIC()
pcomponent_nic.sync_mode = SYNC_MODE
pcomponent_nic.mac = '52:54:00:12:34:56'
pcomponent.add_nic(pcomponent_nic)
e.add_nic(pcomponent_nic)

# node_1
mcomponent = LegoOSQemuHost(mcomponent_img_path, memory='8G', cores=8, debug=False)
mcomponent.sync = SYNC
mcomponent.name = 'mcomponent'
mcomponent.wait = True
e.add_host(mcomponent)

# node_1 NIC
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
