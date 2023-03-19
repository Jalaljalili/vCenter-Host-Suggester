from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import ssl

# Get the vCenter connection details from user input
vcenter_host = input("Enter vCenter hostname or IP address: ")
vcenter_user = input("Enter vCenter username: ")
vcenter_pass = input("Enter vCenter password: ")

# Function to connect to vCenter server
def connect_to_vcenter(vcenter_host, vcenter_user, vcenter_pass):
    try:
        si = SmartConnectNoSSL(
            host=vcenter_host,
            user=vcenter_user,
            pwd=vcenter_pass)
        content = si.RetrieveContent()
        return si, content
    except Exception as e:
        print(f"Failed to connect to vCenter server: {e}")
        return None, None

# Function to format the size of disk and RAM
def format_bytes(bytes_input, is_ram=True):
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
    size_num = ""
    size_unit = ""
    for char in bytes_input:
        if char.isdigit() or char == ".":
            size_num += char
        else:
            size_unit += char.upper()
    if is_ram:
        size_unit = "GB" if size_unit == "MB" else size_unit
    if size_unit in units:
        num_bytes = float(size_num) * (1024 ** units[size_unit])
        if is_ram:
            num_bytes = int(num_bytes / (1024 ** 3))
        else:
            num_bytes = int(num_bytes)
        return num_bytes
    else:
        return None

# Function to suggest suitable hosts based on requirements
def suggest_host(vcenter_host, vcenter_user, vcenter_pass):
    # Connect to vCenter
    si, content = connect_to_vcenter(vcenter_host, vcenter_user, vcenter_pass)
    if not si:
        return None

    # Get the requirements of the virtual machine
    cpu = int(input("Enter required CPU cores: "))
    ram = format_bytes(input("Enter required RAM (in KB MB GB TB like 8GB): "))
    disk_size = format_bytes(input("Enter required disk size (in KB MB GB TB like 200GB): "), False)
    gpu = input("Enter required GPU (Y/N): ")

    # Find all suitable hosts
    suitable_hosts = []
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    for h in host_view.view:
        if h.summary.hardware.numCpuCores >= cpu and h.summary.hardware.memorySize >= ram and h.summary.hardware.cpuMhz >= 2000:
            for datastore in h.datastore:
                if datastore.summary.freeSpace >= disk_size:
                    if gpu == 'Y':
                        try:
                            if any(gpu_device.backing.graphicsMemorySize >= 1024 for gpu_device in h.hardware.pciDevice if hasattr(gpu_device, 'backing')):
                                remaining_cpu = h.summary.hardware.numCpuCores - cpu
                                remaining_ram = h.summary.hardware.memorySize - ram
                                remaining_disk = datastore.summary.freeSpace - disk_size
                                cpu_pct = remaining_cpu / h.summary.hardware.numCpuCores
                                ram_pct = remaining_ram / h.summary.hardware.memorySize
                                disk_pct = remaining_disk / datastore.summary.capacity
                                if cpu_pct <= 4 and ram_pct <= 1 and disk_pct <= 1:
                                    suitable_hosts.append((h, cpu_pct, ram_pct, disk_pct))
                                break
                        except ArithmeticError:
                            pass
                        else:
                        #if any(gpu_device.backing.graphicsMemorySize >= 1024 for gpu_device in h.hardware.pciDevice):
                            # Check remaining resources after adding new VM
                            remaining_cpu = h.summary.hardware.numCpuCores - cpu
                            remaining_ram = h.summary.hardware.memorySize - ram
                            remaining_disk = datastore.summary.freeSpace - disk_size
                            cpu_pct = remaining_cpu / h.summary.hardware.numCpuCores
                            ram_pct = remaining_ram / h.summary.hardware.memorySize
                            disk_pct = remaining_disk / datastore.summary.capacity
                            if cpu_pct <= 400 and ram_pct <= 100 and disk_pct <= 100:
                                suitable_hosts.append((h, cpu_pct, ram_pct, disk_pct))
                                break
                    else:
                        # Check remaining resources after adding new VM
                        remaining_cpu = h.summary.hardware.numCpuCores - cpu
                        remaining_ram = h.summary.hardware.memorySize - ram
                        remaining_disk = datastore.summary.freeSpace - disk_size
                        cpu_pct = remaining_cpu / h.summary.hardware.numCpuCores
                        ram_pct = remaining_ram / h.summary.hardware.memorySize
                        disk_pct = remaining_disk / datastore.summary.capacity
                        if cpu_pct <= 400 and ram_pct <= 100 and disk_pct <= 100:
                            suitable_hosts.append((h, cpu_pct, ram_pct, disk_pct))
                            break
    if not suitable_hosts:
        print("No suitable hosts found")
    else:
        # Sort suitable hosts based on remaining resources
        sorted_hosts = sorted(suitable_hosts, key=lambda x: (x[1], x[2], x[3]))
        print("Suitable hosts:")
        for h in sorted_hosts:
            print(h[0].name)
    # Disconnect from vCenter
    Disconnect(si)

    # Return the list of suitable hosts
    return [h[0] for h in sorted_hosts]

print(suggest_host(vcenter_host, vcenter_user, vcenter_pass))
