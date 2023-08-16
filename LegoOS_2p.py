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

e = Experiment(name='LegoOS_2p')
e.checkpoint = True  # use checkpoint and restore to speed up simulation

img_prefix = os.path.abspath(os.path.dirname(__file__) + '/images')
node_0_img_path = img_prefix + '/2p_node_0.bzImage'
node_1_img_path = img_prefix + '/2p_node_1.bzImage'

# node_0
node_0 = LegoOSQemuHost(node_0_img_path, memory='8G', cores=8, debug=False)
node_0.sync = SYNC
node_0.name = 'node_0'
node_0.wait = True
e.add_host(node_0)

# node_0 NIC
node_0_nic  = E1000NIC()
node_0_nic.sync_mode = SYNC_MODE
node_0_nic.mac = '52:54:00:12:34:56'
node_0.add_nic(node_0_nic)
e.add_nic(node_0_nic)

# node_1
node_1 = LegoOSQemuHost(node_1_img_path, memory='8G', cores=8, debug=False)
node_1.sync = SYNC
node_1.name = 'node_1'
node_1.wait = True
e.add_host(node_1)

# node_1 NIC
node_1_nic = E1000NIC()
node_1_nic.sync_mode = SYNC_MODE
node_1_nic.mac = '52:54:00:12:34:57'
node_1.add_nic(node_1_nic)
e.add_nic(node_1_nic)

# network
network = SwitchNet()
network.sync = SYNC
node_0_nic.set_network(network)
node_1_nic.set_network(network)
e.add_network(network)

experiments = [e]
