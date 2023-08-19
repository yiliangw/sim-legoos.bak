from simbricks.orchestration.nodeconfig import IdleHost, LinuxNode
from simbricks.orchestration.simulators import QemuHost
import math


class LegoOSQemuHost(QemuHost):

    def __init__(self, kernel_path, memory, cores, debug=False, debug_port=1234):
        config = LinuxNode()
        config.app = IdleHost()
        super().__init__(config)
        # self.sync_period = 500000
        self.kernel_path = kernel_path
        self.memory = memory
        self.cores = cores
        self.debug = debug
        self.debug_port = debug_port

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
            f'-m {self.memory} -smp {self.cores} '
        )

        if self.debug:
            cmd += f' -gdb tcp:localhost:{self.debug_port} -S '

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
    