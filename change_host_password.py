# Import the required modules
import requests
import urllib3
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import os
import base64

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the vCenter server and credentials
vcenter_server = os.environ.get("VCENTER_SERVER")
vcenter_user = os.environ.get("VCENTER_USER")
vcenter_password = os.environ.get("VCENTER_PASS")
# Define the new password for ESXi hosts
new_password =  input("Enter new ESXi password: ")

# Connect to the vCenter server
si = SmartConnect(host=vcenter_server, user=vcenter_user, pwd=vcenter_password, sslContext=ssl._create_unverified_context())
content = si.RetrieveContent()

# Get all the ESXi hosts in the vCenter inventory
container = content.rootFolder  # starting point to look into
viewType = [vim.HostSystem]  # object types to look for
recursive = True  # whether to look into it recursively
containerView = content.viewManager.CreateContainerView(container, viewType, recursive)
esxi_hosts = containerView.view

# Loop through each ESXi host and change its password
for host in esxi_hosts:
    # Get the host name and IP address
    host_name = host.name
    host_ip = host.summary.config.name
    # Create a REST API session with the host
    session_url = f"https://{host_ip}/rest/com/vmware/cis/session"
    #session_headers = {"vmware-use-header-authn": "test", "vmware-api-session-id": "null"}
    # Create the session headers
    session_headers = {
    "Content-Type": "application/json",
    "vmware-api-session-id": None,
    "Authorization": "Basic " + base64.b64encode(f"{host_name}\\root:{new_password}".encode()).decode()
    }
    session_response = requests.post(session_url, auth=(vcenter_user, vcenter_password), verify=False, headers=session_headers)
    print (session_response)
    # Check if the session is successful
    if session_response.status_code == 200:
        print(f"Successfully connected to {host_name}")
        # Get the session ID from the response header
        session_id = session_response.headers["vmware-api-session-id"]
        
        # Create a payload with the new password
        payload = {"spec":{"password":new_password}}
        
        # Create a header with the session ID
        headers = {"vmware-api-session-id":session_id}
        
        # Send a PATCH request to change the password
        password_url = f"https://{host_ip}/rest/appliance/system/root"
        password_response = requests.patch(password_url, json=payload, verify=False, headers=headers)
        
        # Check if the password change is successful
        if password_response.status_code == 200:
            print(f"Successfully changed password for {host_name}")
        else:
            print(f"Failed to change password for {host_name}: {password_response.text}")
    else:
        print(f"Failed to connect to {host_name}: {session_response.text}")

# Disconnect from the vCenter server
Disconnect(si)
