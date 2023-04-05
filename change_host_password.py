from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import ssl

def change_host_password(vcenter_host, vcenter_user, vcenter_pass, new_password):
    # Connect to vCenter
    si = SmartConnectNoSSL(host=vcenter_host, user=vcenter_user, pwd=vcenter_pass)
    content = si.RetrieveContent()

    # Get all hosts managed by vCenter
    hosts = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    
    # Loop through each host and change the password
    for host in hosts.view:
        print("Updating password for host: " + host.name)
        try:
            host.UpdateESXiRootPassword(new_password)
            print("Password updated successfully")
        except vim.fault.HostConnectFault:
            print("Failed to connect to host")
        except vim.fault.InvalidState:
            print("Invalid state, host may be in maintenance mode")
        except vim.fault.InvalidLogin:
            print("Invalid credentials provided")

    # Disconnect from vCenter
    Disconnect(si)

# Get the vCenter connection details from user input
vcenter_host = input("Enter vCenter hostname or IP address: ")
vcenter_user = input("Enter vCenter username: ")
vcenter_pass = input("Enter vCenter password: ")
new_password = input("Enter vCenter NewPassword: ")

change_host_password(vcenter_host, vcenter_user, vcenter_pass, new_password)