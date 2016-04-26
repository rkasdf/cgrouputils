import cgroup
import fileops
import os

class NoSuchKVMError(Exception):
    pass
class ValOutofRanege(Exception):
    pass
class kvmCgroup(cgroup.CGroup):
    def __init__(self, kvmname, subsystem):
        self.kvmname = kvmname
        staus = cgroup.SubsystemStatus
        subsystemPath = staus.paths[subsystem]
        fullPath = fileops.find(kvmname, subsystemPath)
        if not fullPath: 
            self.cgroup = False
            raise NoSuchKVMError("No such kvm found: " + kvmname)
        else:
            self.cgroup = True
            subsys = cgroup._get_subsystem(subsystem)
            cgroup.CGroup.__init__(self, subsys, fullPath)   

class kvmCpuLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'cpu')
    def cpulimit(self, percentage):
        if not self.cgroup:
            raise NoSuchKVMError("No such kvm found: " + self.kvmname)
        if percentage < 0 or percentage > 100:
            raise ValOutofRanege("The percentage value out of range:  " + percentage) 
        self.set_config('cfs_period_us', 100*int(percentage))
    def cpuunset(self):
        self.set_config('cpus', 10000)
        
class kvmCpusetLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, self.kvmname, 'cpuset')
    def cpusetlimit(self, cpuset):
        if not self.cgroup:
            raise NoSuchKVMError("No such kvm found: " + self.kvmname)        
        params = self.subsystem.get_default_configs()
        cpuseq = params['cpus']
        cpunum = ''
        while  cpuseq[-1] >= '0' and cpuseq[-1] <= '9':
            cpunum += cpuseq[-1]
        cpunum = int(cpunum)
        if cpunum < 1:
            raise Exception("Cpu number is wrong")
        for cpus in cpuset.split(','):
            if '-' in cpus:
                up, down = cpus.split('-')
                up, down = int(up), int(down)
                if up > down or up < 0 or down < 0 or up > cpunum or down > cpunum:
                    raise Exception("Wrong in cpuset: " + cpuset)
            else:
                if int(cpus) > cpunum:
                    raise Exception("Wrong in cpuset: " + cpuset)
        self.set_config('cpus', cpuset)
    def cpusetunset(self):
        if not self.cgroup:
            raise NoSuchKVMError("No such docker found: " + self.kvmname)
        params = self.subsystem.get_default_configs()
        cpuseq = params['cpus']
        self.set_config('cpus', cpuseq)

class kvmMemLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'memory')
    def memlimit(self, memory):
        if not self.cgroup:
            raise NoSuchKVMError("No such kvm found: " + self.kvmname)
        params = self.subsystem.get_default_configs()
        memmax = int(params['limit_in_bytes'])
        memory = int(memory)
        if memory > memmax:
            raise ValOutofRanege("Memory out of range: " + memory)
        self.set_config('limit_in_bytes', memory)
    def memunset(self):
        if not self.cgroup:
            raise NoSuchKVMError("No such kvm found: " + self.kvmname)
        self.set_config('limit_in_bytes', -1)

class kvmDiskLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'blk_io')
    def diskreadlimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such docker found: " + self.kvmname)
            return False
        major = int(os.stat(devpath).st_dev & 0xff)
        minor = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps', '%d:%d %d' %(major, minor, val))
        return True
    def diskreadunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such docker found: " + self.kvmname)
            return False
        major = int(os.stat(devpath).st_dev & 0xff)
        minor = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps', '%d:%d 0' %(major, minor))
        return True
    def diskwritelimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such docker found: " + self.kvmname)
            return False
        major = int(os.stat(devpath).st_dev & 0xff)
        minor = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps', '%d:%d %d' %(major, minor, val))
        return True
    def diskwriteunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such docker found: " + self.kvmname)
            return False
        major = int(os.stat(devpath).st_dev & 0xff)
        minor = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps', '%d:%d 0' %(major, minor))
        return True
    
        
        