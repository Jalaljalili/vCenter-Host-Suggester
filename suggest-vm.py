from pyVim import connect
from pyVmomi import vim
import ssl 

def format_bytes(bytes_str, mb=True):
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
    num, unit = bytes_str[:-2], bytes_str[-2:].upper()
    if unit not in units:
        raise ValueError(f"Invalid unit: {unit}")
    bytes = float(num) * (1024 ** units[unit])
    if mb:
        return bytes / (1024 ** 2)
    
    return bytes

def suggest_host(vcenter_host, vcenter_user, vcenter_pass):
    # Connect to vCenter
    si = connect.SmartConnectNoSSL(host=vcenter_host, user=vcenter_user, pwd=vcenter_pass)
    content = si.RetrieveContent()

    # Get the requirements of the virtual machine
    cpu = int(input("Enter required CPU cores: "))
    ram = int(format_bytes(input("Enter required RAM (in KB MB GB TB like 8GB): ")))
    disk_size = int(format_bytes(input("Enter required disk size (in KB MB GB TB like 200GB): "),False))
    gpu = input("Enter required GPU (Y/N): ")

    # Find all suitable hosts
    suitable_hosts = []
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    for h in host_view.view:
        if h.summary.hardware.numCpuCores >= cpu and h.summary.hardware.memorySize >= ram and h.summary.hardware.cpuMhz >= 2000:
            for datastore in h.datastore:
                if datastore.summary.freeSpace >= disk_size:
                    if gpu == 'Y':
                        if any(gpu_device.backing.graphicsMemorySize >= 1024 for gpu_device in h.hardware.pciDevice):
                            suitable_hosts.append(h)
                            break
                    else:
                        suitable_hosts.append(h)
                        break

    if not suitable_hosts:
        print("No suitable hosts found")
    else:
        print("Suitable hosts:")
        for h in suitable_hosts:
            print(h.name)

    # Disconnect from vCenter
    connect.Disconnect(si)

    # Return the list of suitable hosts
    return suitable_hosts

def sort_hosts(hosts, requirements):
    cpu_usage = lambda h: h.summary.quickStats.overallCpuUsage
    cpu_allocated = lambda h: h.summary.quickStats.overallCpuDemand
    mem_usage = lambda h: h.summary.quickStats.overallMemoryUsage
    mem_allocated = lambda h: h.summary.quickStats.hostMemoryUsage
    ds_latency = lambda h: h.datastore[0].summary.latency
    ds_iops = lambda h: h.datastore[0].summary.iops
    host_metrics = [
        (cpu_usage, False),
        (cpu_allocated, False),
        (mem_usage, False),
        (mem_allocated, False),
        (ds_latency, True),
        (ds_iops, True)
    ]
    for metric, reverse in host_metrics:
        hosts.sort(key=metric, reverse=reverse)
    filtered_hosts = []
    for host in hosts:
        cpu_pct = (cpu_allocated(host) / host.summary.hardware.numCpuCores) * 100
        mem_pct = (mem_allocated(host) / host.summary.hardware.memorySize) * 100
        disk_pct = (requirements.disk_size / host.datastore[0].summary.capacity) * 100
        if cpu_pct <= 400 and mem_pct <= 100 and disk_pct <= 100:
            filtered_hosts.append(host)
    return filtered_hosts


# Get the vCenter connection details from user input
vcenter_host = input("Enter vCenter hostname or IP address: ")
vcenter_user = input("Enter vCenter username: ")
vcenter_pass = input("Enter vCenter password: ")

# Call the suggest_host() function to get the best host for a virtual machine
print(sort_hosts(suggest_host(vcenter_host, vcenter_user, vcenter_pass)))

