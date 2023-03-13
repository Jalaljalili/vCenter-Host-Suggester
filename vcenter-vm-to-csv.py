from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import pandas as pd
import ssl
from pyVim import connect
from pyVmomi import vmodl


# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context
# Connect to vCenter server
si = SmartConnect(
    host="<vcenter_hostname>",
    user="<vcenter_username>",
    pwd="<vcenter_password>",
    port=int("<vcenter_port>")
)

# Get VM details
content = si.RetrieveContent()
vm_view = content.viewManager.CreateContainerView(
    content.rootFolder, [vim.VirtualMachine], True)
vms = vm_view.view

data = []
for vm in vms:
    # Get CPU, RAM, and disk details
    num_cpus = vm.summary.config.numCpu
    memory_mb = vm.summary.config.memorySizeMB
    num_disks = len(vm.config.hardware.device)
    has_gpu = False
    
    # Check for GPU
    for device in vm.config.hardware.device:
        if isinstance(device, vim.VirtualPCIPassthrough):
            has_gpu = True
            break
    
    # Add data to list
    data.append({
        "Name": vm.name,
        "Number of CPU": num_cpus,
        "Number of RAM": memory_mb,
        "Number of Disks": num_disks,
        "GPU": has_gpu
    })

# Disconnect from vCenter server
Disconnect(si)

# Convert data to DataFrame
df = pd.DataFrame(data)

# Calculate totals for each metric
totals = {
    "Number of CPU": df["Number of CPU"].sum(),
    "Number of RAM": df["Number of RAM"].sum(),
    "Number of Disks": df["Number of Disks"].sum(),
    "GPU": df["GPU"].sum()
}

# Print totals
print("Total Number of CPU: {}".format(totals["Number of CPU"]))
print("Total Number of RAM: {} MB".format(totals["Number of RAM"]))
print("Total Number of Disks: {}".format(totals["Number of Disks"]))
print("Total Number of VMs with GPU: {}".format(totals["GPU"]))

# Export data to CSV
df.to_csv("vm_details.csv", index=False)