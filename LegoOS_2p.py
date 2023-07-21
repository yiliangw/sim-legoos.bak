'''
Simple LegoOS experiment, which sets up a pComponent and a mComponent connected
through ethernet.
'''
from simbricks.orchestration.experiments import Experiment
from simbricks.orchestration.nodeconfig import IdleHost, LinuxNode
from simbricks.orchestration.simulators import QemuHost, E1000NIC, SwitchNet

import os
import math


class LegoOSQemuHost(QemuHost):

    def __init__(self, kernel_path):
        config = LinuxNode()
        config.app = IdleHost()
        super().__init__(config)
        self.kernel_path = kernel_path

    def run_cmd(self, env):
        accel = ',accel=kvm:tcg' if not self.sync else ''
        if self.node_config.kcmd_append:
            kcmd_append = ' ' + self.node_config.kcmd_append
        else:
            kcmd_append = ''

        '''
        The command from LegoOS
        '''
        cmd = (
            f'{env.qemu_path} -serial mon:stdio '
            '-cpu Skylake-Server -display none -nic none -no-reboot '
            f'-kernel {self.kernel_path} '
            '-append "earlyprintk=ttyS0 console=ttyS0 memmap=2G$4G" '
            f'-m 4G -smp 4 '
            # '-d int,cpu_reset '
        )

        if self.sync:
            unit = self.cpu_freq[-3:]
            if unit.lower() == 'ghz':
                base = 0
            elif unit.lower() == 'mhz':
                base = 3
            else:
                raise ValueError('cpu frequency specified in unsupported unit')
            num = float(self.cpu_freq[:-3])
            shift = base - int(math.ceil(math.log(num, 2)))

            cmd += f' -icount shift={shift},sleep=off '

        for dev in self.pcidevs:
            cmd += f'-device simbricks-pci,socket={env.dev_pci_path(dev)}'
            if self.sync:
                cmd += ',sync=on'
                cmd += f',pci-latency={self.pci_latency}'
                cmd += f',sync-period={self.sync_period}'
            else:
                cmd += ',sync=off'
            cmd += ' '

        # qemu does not currently support net direct ports
        assert len(self.net_directs) == 0
        # qemu does not currently support mem device ports
        assert len(self.memdevs) == 0
        return cmd

    
e = Experiment(name='LegoOS_2p')
e.checkpoint = True  # use checkpoint and restore to speed up simulation

img_prefix = os.path.abspath(os.path.dirname(__file__) + '/images')
node_0_img_path = img_prefix + '/2p_node_0.bzImage'
node_1_img_path = img_prefix + '/2p_node_1.bzImage'

# node_0
node_0 = LegoOSQemuHost(node_0_img_path)
node_0.name = 'node_0'
node_0.wait = True
e.add_host(node_0)

# node_0 NIC
node_0_nic  = E1000NIC()
node_0_nic.mac = '52:54:00:12:34:56'
node_0.add_nic(node_0_nic)
e.add_nic(node_0_nic)

# node_1
node_1 = LegoOSQemuHost(node_1_img_path)
node_1.name = 'node_1'
node_1.wait = True
e.add_host(node_1)

# node_1 NIC
node_1_nic = E1000NIC()
node_1_nic.mac = '52:54:00:12:34:57'
node_1.add_nic(node_1_nic)
e.add_nic(node_1_nic)

# network
network = SwitchNet()
node_0_nic.set_network(network)
node_1_nic.set_network(network)
e.add_network(network)

experiments = [e]
