# VMware vCenter Server Integration

This Python script connects to a VMware vCenter Server, retrieves details for all virtual machines, and suggests the best host to run each virtual machine based on CPU, RAM, number of disks, and GPU availability. The script then writes the VM details to a CSV file, with each row containing the VM name and its corresponding host.

# Installation

To run this script, you'll need to install the following Python packages:
 * pyVmomi
 * pandas


You can install these packages using pip, the Python package manager:

```bash
pip install pyVmomi pandas
```
# Configuration

Before running the script, you'll need to edit the following variables in the code:

    <vcenter-hostname>: the hostname or IP address of your vCenter Server.
    <username>: your vCenter Server username.
    <password>: your vCenter Server password.
    <vcenter-port>: the port number to use for connecting to vCenter Server (default is 443).

Usage

To run the script, simply execute the vmware_integration.py file using Python:

```bash
python vmware_integration.py
```
The script will connect to vCenter Server, retrieve VM details, suggest the best host for each VM, and write the VM details to a CSV file named vm_details.csv. The CSV file will contain one row for each VM, with columns for the VM name, number of CPUs, amount of memory, number of disks, disk sizes, and GPU availability.

# Contact

If you have any questions or feedback about this code, please contact me at jalaljalili20@gmail.com.

That should give you a good starting point for writing a README file for your code. Be sure to update the contact information and license details as appropriate for your project.

# vCenter Host Suggester
This is a Python script that connects to a vCenter server and suggests suitable hosts for new virtual machines based on the requirements specified by the user.

## Prerequisites
  *  Python 3
  * PyVmomi library (can be installed via pip)
  *  A vCenter server with valid credentials

## Usage

1. Clone or download the repository to your local machine.

2. Open a terminal or command prompt and navigate to the downloaded directory.

3. Run the script using the following command:

```bash
python suggest_host.py
```
4. Follow the prompts to enter the required CPU cores, RAM, disk size, and GPU requirements.

5. The script will suggest a list of suitable hosts based on the given requirements.

6. Choose a host and create the new virtual machine.

## Sorting Algorithm

The suggested hosts are sorted based on the following metrics:

  *  CPU usage
  *  CPU allocated
  *  Memory usage
  *  Memory allocated
  *  Datastore latency
  *  Datastore IOPS

The algorithm also filters out hosts that have over-allocated resources in terms of disk and RAM, and hosts with CPU over-subscription more than 400%.

# Change Password for All Hosts Connected to vCenter
This Python script connects to vCenter and changes the password for all hosts that are connected to it.
## Prerequisites
  *  Python 3 installed on your machine
  *  The pyVmomi module installed. You can install it via pip:

```bash
pip install pyVmomi 
```
*  Access to vCenter with administrator privileges
## Usage

  1.  Clone the repository or download the script file change_host_password.py.

  2.  Open the change_host_password.py file in a text editor.

  3.  Modify the following variables at the top of the script according to your vCenter details and desired new password:

    vcenter_host: the hostname or IP address of the vCenter server.
    vcenter_user: the username to connect to vCenter.
    vcenter_pass: the password to connect to vCenter.
    new_password: the new password that will be set for all the hosts.

  4.  Save the modified script file.

  5.  Open a terminal or command prompt and navigate to the directory containing the change_host_password.py file.

  6.  Run the script:
  ```bash
  python change_host_password.py
  ```
  7.  Wait for the script to complete. The script will print the status of each host and whether the password change was successful or not.

## Disclaimer

Use this script at your own risk. The author is not responsible for any damage or loss caused by the use of this script. It is recommended that you test the script in a non-production environment before using it in a production environment.

## Author

This script was created by [Jalal Jalili].
