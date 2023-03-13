import ssl
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

def get_vm_details(vm):
    # Retrieve CPU and RAM details
    num_cpu = vm.config.hardware.numCPU
    memory_mb = vm.config.hardware.memoryMB
    
    # Retrieve disk details
    num_disks = len(vm.config.hardware.device)
    disks = []
    for device in vm.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualDisk):
            disks.append(device.capacityInBytes / 1024 / 1024 / 1024)
    
    # Retrieve GPU details
    has_gpu = False
    for device in vm.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualPCIPassthrough):
            has_gpu = True
            break
    
    return {
        "num_cpu": num_cpu,
        "memory_mb": memory_mb,
        "num_disks": num_disks,
        "disks": disks,
        "has_gpu": has_gpu
    }

def suggest_best_host(vm_details):
    # Query available hosts
    host_view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.HostSystem], True)
    hosts = host_view.view
    host_view.Destroy()
    
    # Filter hosts based on CPU, RAM, number of disks, and GPU
    compatible_hosts = []
    for host in hosts:
        if (host.hardware.cpuInfo.numCpuCores >= vm_details["num_cpu"] and
            host.hardware.memorySize / 1024 / 1024 >= vm_details["memory_mb"] and
            len(host.datastore) >= vm_details["num_disks"]):
            if not vm_details["has_gpu"]:
                compatible_hosts.append(host)
            else:
                for device in host.hardware.device:
                    if isinstance(device, vim.host.PciDevice):
                        if device.deviceName.startswith("NVIDIA"):
                            compatible_hosts.append(host)
                            break
    
    # Sort compatible hosts by available resources
    sorted_hosts = sorted(compatible_hosts, key=lambda host: host.summary.quickStats.overallMemoryUsage)
    
    return sorted_hosts[0] if sorted_hosts else None

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Connect to vCenter server
si = connect.SmartConnectNoSSL(
    host="<vcenter_hostname>",
    user="<vcenter_username>",
    pwd="<vcenter_password>",
    port=int("<vcenter_port>")
)
content = si.RetrieveContent()

# Retrieve VMs and get details
vm_view = content.viewManager.CreateContainerView(
    content.rootFolder, [vim.VirtualMachine], True)
vms = vm_view.view
vm_view.Destroy()

for vm in vms:
    vm_details = get_vm_details(vm)
    best_host = suggest_best_host(vm_details)
    print(f"VM: {vm.name}")
    print(f"Number of CPU: {vm_details['num_cpu']}")
    print(f"Number of RAM: {vm_details['memory_mb']} MB")
    print(f"Number of disks: {vm_details['num_disks']}")
    print(f"Disks: {vm_details['disks']} GB")
    print(f"Has GPU: {'Yes' if vm_details['has_gpu'] else 'No'}")
    print(f"Best host: {best_host.name if best_host else 'None'}")
    print()