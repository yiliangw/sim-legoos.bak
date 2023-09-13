import simbricks.orchestration.nodeconfig as nodec
import simbricks.orchestration.simulators as sim

import typing as tp
import math
import os

class LegoOSApp(nodec.AppConfig):

    def __init__(self):
        super().__init__()


class LegoModuleLoading(nodec.AppConfig):
    
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    LEGO_MODULE_DIR = f'{PROJECT_DIR}/images/modules'
    
    def __init__(self, module_list: tp.List[str], resource_list: tp.List[tuple[str,str]]=[]):
        super().__init__()
        self.module_list = module_list
        self.resource_list = resource_list

    def config_files(self):
        m = {}
        r = {}
        for module in self.module_list:
            m[module] = open(f'{self.LEGO_MODULE_DIR}/{module}', 'rb')
        for dst_f, src_f in self.resource_list:
            r[dst_f] = open(f'{self.LEGO_MODULE_DIR}/{src_f}', 'rb')
        return {**m, **r, **super().config_files()}

    def run_cmds(self, node):
        cmds = []
        for module in self.module_list:
            cmds.append(f'insmod /tmp/guest/{module}')
            cmds.append('sleep 1')
        cmds.append('sleep infinity')
        return cmds


class LegoOSNode(nodec.NodeConfig):
    
    def __init__(self, kernel_path, memory='8G', cores=8):
        super().__init__()
        self.memory = memory
        self.cores = cores
        self.app = LegoOSApp()
        self.kernel_path = kernel_path


class LegoModuleNode(nodec.NodeConfig):

    def __init__(self, module_list: tp.List[str], memory='8G', cores=8):
        super().__init__()
        self.memory = memory
        self.cores = cores

        self.app = LegoModuleLoading(module_list)
        self.images_path = os.path.dirname(os.path.abspath(__file__)) + '/images'
        self.lego_disk_img = f'{self.images_path}/disk/ubuntu-14.04'
        self.lego_userdata_img = f'{self.images_path}/disk/user_data.img'
        self.lego_module_kernel = f'{self.images_path}/kernel/linux-3.13.1/arch/x86/boot/bzImage'


class LegoModuleQemuHost(sim.QemuHost):

    def __init__(self, node_config: LegoModuleNode, debug=False, debug_port=1234):
        super().__init__(node_config)
        self.debug = debug
        self.debug_port = debug_port
    
    def prep_cmds(self, env):
        return [
            f'{env.qemu_img_path} create -f qcow2 -o '
            f'backing_file="{self.node_config.lego_disk_img}" '
            f'{env.hdcopy_path(self)}'
        ]
    
    def run_cmd(self, env):
        accel = ',accel=kvm:tcg' if not self.sync else ''
        if self.node_config.kcmd_append:
            kcmd_append = ' ' + self.node_config.kcmd_append
        else:
            kcmd_append = ''

        cmd = (
            f'{env.qemu_path} -machine q35{accel} -enable-kvm -serial mon:stdio '
            '-cpu Skylake-Server -display none -nic none '
            f'-drive file={env.hdcopy_path(self)},if=ide,index=0,media=disk '
            f'-drive file={env.cfgtar_path(self)},if=ide,index=1,media=disk,driver=raw '
            f'-kernel {self.node_config.lego_module_kernel} '
            '-append "earlyprintk=ttyS0 console=ttyS0 root=/dev/sda1 ro '
            f'init=/home/ubuntu/guestinit.sh rw{kcmd_append}" '
            f'-m {self.node_config.memory} -smp {self.node_config.cores} '
            f'-L {env.repodir}/sims/external/qemu/pc-bios/ '
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


class LegoOSQemuHost(sim.QemuHost):

    def __init__(self, node_config: LegoOSNode, debug=False, debug_port=1234):
        super().__init__(node_config)
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
            f'-kernel {self.node_config.kernel_path} '
            f'-L {env.repodir}/sims/external/qemu/pc-bios/ '
            '-append "earlyprintk=ttyS0 console=ttyS0 memmap=2G$4G" '
            f'-m {self.node_config.memory} -smp {self.node_config.cores} '
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
    
