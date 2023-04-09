from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import os
import datetime
import csv
import click
# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Connect to vCenter server
si = SmartConnect(
    host=os.environ.get("VCENTER_HOST"),
    user=os.environ.get("VCENTER_USER"),
    pwd=os.environ.get("VCENTER_PASS"),
    port=int("443")
)

# Get VM details
content = si.RetrieveContent()
vm_view = content.viewManager.CreateContainerView(
    content.rootFolder, [vim.VirtualMachine], True)
vms = vm_view.view

# Create a list to store VM info
vm_info_list = []

# Loop through all VMs and get their info
with click.progressbar(vms) as vms:
    for vm in vms:
        # Get the VM info
        vm_info = {}
        vm_info['Name'] = vm.name
        vm_info['Status'] = vm.summary.runtime.powerState
        vm_info['Shutdown Time'] = None
        
        # Get the shutdown time if the VM is powered off
        if vm.summary.runtime.powerState == 'poweredOff':
            if isinstance(vm.runtime.bootTime, datetime.datetime):
                shutdown_time = vm.runtime.bootTime + datetime.timedelta(seconds=vm.summary.quickStats.uptimeSeconds)
                vm_info['Shutdown Time'] = shutdown_time.strftime('%Y-%m-%d %H:%M:%S')

        # Add the VM info to the list
        vm_info_list.append(vm_info)

# Disconnect from vCenter server
Disconnect(si)

# Write the VM info to a CSV file
with open('vm_info.csv', 'w', newline='') as csvfile:
    fieldnames = ['Name', 'Status', 'Shutdown Time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for vm_info in vm_info_list:
        writer.writerow(vm_info)
