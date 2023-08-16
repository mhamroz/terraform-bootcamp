#### HOW TO USE ####

# - Provision new users
# python3 lab_provision.py users -n 2 

# - Remove users
# python3 lab_provision.py users -n 2 --rm

# - Provision new devices
# python3 lab_provision.py cml -n 2 

# - Remove devices
# python3 lab_provision.py cml -n 2 --rm

# - Lab Verify
# python3 lab_provision.py verify -n 2 --command guestshell

# Provision 1 user
# python3 lab_provision.py user -u user0 -p cisco0

# Remove 1 user
# python3 lab_provision.py user -u user0 -p cisco0 --rm


#grok 
#ngrok config add-authtoken 1VrMtDwzu6qOvuoMsydLrgffres_6Sq3aVJyDzuBZshCfkK3i
#ngrok tcp 22


### remove docker containers from JS

#sudo docker rm $(docker ps -aq)

### remove docker images from JS

#docker rmi $(docker images -q)



import requests
import paramiko
import click
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### JUMPSERVER IP AND CREDS

js_hostname = '10.48.86.186'
js_username = 'root'
js_password = 'CATLab2023'


### CML URL AND TOKEN

cml_url = 'https://10.48.86.190/api/v0/labs/3cad6d'
jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb20uY2lzY28udmlybCIsImlhdCI6MTY4MTkwOTg2NywiZXhwIjoxNjgxOTk2MjY3LCJzdWIiOiJhM2M0Zjg4OS04ZWNjLTRkMGUtODM4OC1iMzU2NTQxZDNkYzIifQ.qwl8mLY6jCuc1ffS95Iqp1wVsbrjFtwv5BDV3k1seqQ'
@click.group()
def main():
    pass

@main.command()
@click.option('--number','-n',help='Number of users',required=True,type=int)
@click.option('--password','-p',help='Password prefix',required=True,default='cisco')
@click.option('--username','-u',help='Username prefix',required=True,default='user')
@click.option('--rm',is_flag=True,help='Remove users from server',default=False,show_default=True)

def users(number,password,username,rm):

    # Connect to the server via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(js_hostname, username=js_username, password=js_password)

    for i in range(1,number+1):
        # Create new users
        new_username = username + str(i)
        new_password = password + str(i)
        # Check if the user already exists
        stdin, stdout, stderr = ssh.exec_command(f"id {new_username}")
        user_exists = not bool(stderr.read())
        
        if rm:
            # Remove the user
            command = f"sudo userdel -r {new_username}"
            stdin, stdout, stderr = ssh.exec_command(command)

            # Check if the command was successful
            if stderr.read():
                # Kill user session
                command = f"sudo pkill -u {new_username}"
                stdin, stdout, stderr_kill = ssh.exec_command(command)
                command = f"sudo userdel -r {new_username}"
                stdin, stdout, stderr_remove = ssh.exec_command(command)
                if stderr_remove.read():
                    click.echo(f"Error removing user: {stderr_remove.read().decode()}")
                else:
                    click.echo(f"User {new_username} was removed successfully")
            else:
                click.echo(f"User {new_username} was removed successfully")
        else:

            # Create or update the user and password
            if user_exists:
                command = f"echo '{new_username}:{new_password}' | sudo chpasswd"
            else:
                command = f"sudo useradd -m {new_username}; echo '{new_username}:{new_password}' | sudo chpasswd"
            click.echo(command)
            stdin, stdout, stderr = ssh.exec_command(command)

            # Check if the command was successful
            if stderr.read():
                print(f"Error creating or updating user: {stderr.read().decode()}")
            else:
                if user_exists:
                    print(f"User {new_username} password was updated successfully")
                else:
                    print(f"User {new_username} was created successfully")

            # Transfer the zip file to the user's home directory
            sftp = ssh.open_sftp()
            local_path = './labs.zip'
            remote_path = f'/home/{new_username}/labs.zip'
            sftp.put(local_path, remote_path)
            sftp.close()

            # Unzip the file and remove it
            stdin, stdout, stderr = ssh.exec_command(f"sudo unzip {remote_path} -d /home/{new_username}; sudo rm {remote_path}")

            # Check if the command was successful
            if stderr.read():
                print(f"Error unzipping file: {stderr.read().decode()}")
            else:
                print(f"File was unzipped successfully")

                # Change the owner and permissions of the extracted files
                stdin, stdout, stderr = ssh.exec_command(f"sudo chown -R {new_username}:{new_username} /home/{new_username}/*; sudo chmod -R 700 /home/{new_username}/*")

                # Check if the command was successful
                if stderr.read():
                    print(f"Error changing owner and permissions: {stderr.read().decode()}")
                else:
                    print(f"Owner and permissions were changed successfully")

    # Close the SSH connection
    ssh.close()

@main.command()
@click.option('--password','-p',help='Password',required=True,default='cisco')
@click.option('--username','-u',help='Username',required=True,default='user')
@click.option('--rm',is_flag=True,help='Remove user from server',default=False,show_default=True)

def user(password,username,rm):

    # Connect to the server via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(js_hostname, username=js_username, password=js_password)

  
    # Create new users
    new_username = username
    new_password = password
    # Check if the user already exists
    stdin, stdout, stderr = ssh.exec_command(f"id {new_username}")
    user_exists = not bool(stderr.read())
        
    if rm:
        # Remove the user
        command = f"sudo userdel -r {new_username}"
        stdin, stdout, stderr = ssh.exec_command(command)

        # Check if the command was successful
        if stderr.read():
            # Kill user session
            command = f"sudo pkill -u {new_username}"
            stdin, stdout, stderr_kill = ssh.exec_command(command)
            command = f"sudo userdel -r {new_username}"
            stdin, stdout, stderr_remove = ssh.exec_command(command)
            if stderr_remove.read():
                click.echo(f"Error removing user: {stderr_remove.read().decode()}")
            else:
                 click.echo(f"User {new_username} was removed successfully")
        else:
            click.echo(f"User {new_username} was removed successfully")
    else:

        # Create or update the user and password
        if user_exists:
            command = f"echo '{new_username}:{new_password}' | sudo chpasswd"
        else:
            command = f"sudo useradd -m {new_username}; echo '{new_username}:{new_password}' | sudo chpasswd"
        click.echo(command)
        stdin, stdout, stderr = ssh.exec_command(command)

        # Check if the command was successful
        if stderr.read():
            print(f"Error creating or updating user: {stderr.read().decode()}")
        else:
            if user_exists:
                print(f"User {new_username} password was updated successfully")
            else:
                print(f"User {new_username} was created successfully")

        # Transfer the zip file to the user's home directory
        sftp = ssh.open_sftp()
        local_path = './labs.zip'
        remote_path = f'/home/{new_username}/labs.zip'
        sftp.put(local_path, remote_path)
        sftp.close()

        # Unzip the file and remove it
        stdin, stdout, stderr = ssh.exec_command(f"sudo unzip {remote_path} -d /home/{new_username}; sudo rm {remote_path}")

        # Check if the command was successful
        if stderr.read():
            print(f"Error unzipping file: {stderr.read().decode()}")
        else:
            print(f"File was unzipped successfully")

            # Change the owner and permissions of the extracted files
            stdin, stdout, stderr = ssh.exec_command(f"sudo chown -R {new_username}:{new_username} /home/{new_username}/*; sudo chmod -R 700 /home/{new_username}/*")

            # Check if the command was successful
            if stderr.read():
                print(f"Error changing owner and permissions: {stderr.read().decode()}")
            else:
                print(f"Owner and permissions were changed successfully")

    # Close the SSH connection
    ssh.close()

@main.command()
@click.option('--number','-n',help='Number of routers',required=True,type=int)
@click.option('--rm',is_flag=True,help='Remove routers from lab',default=False,show_default=True)
@click.option('--password','-p',help='Password prefix',required=True,default='cisco')
@click.option('--username','-u',help='Username prefix',required=True,default='user')

def cml(number,rm,username,password):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json',
    }

    ## Starting x position of first router in CML GUI
    start_x = -2250
    step_x = 125

    ## Get Nodes from LAB

    response = requests.get(f'{cml_url}/nodes', headers=headers, verify=False)
    nodes = response.json()
    nodes_dir = {}
    for node in nodes:
        response = requests.get(f'{cml_url}/nodes/{node}', headers=headers, verify=False)
        node_details = response.json()

        if node_details['data']['label'] != 'unmanaged-switch-0' and node_details['data']['label'] != 'ext-conn-0':
            nodes_dir[node_details['data']['label']] = node_details['id']
        elif node_details['data']['label'] == 'unmanaged-switch-0':
            unmanaged_switch = node_details['id']
        elif node_details['data']['label'] == 'ext-conn-0':
            ext_conn = node_details['id']

    ## Get interfaces of unmanaged switch
    response = requests.get(f'{cml_url}/nodes/{unmanaged_switch}/interfaces', headers=headers, verify=False)
    sw_interfaces = response.json()

   # for jj in sw_interfaces:
   #     response = requests.get(f'{cml_url}/interfaces/{jj}', headers=headers, verify=False)
   #     print(response.json())
   #     input("DSDSDA")


    for i in range(1,number+1):
        x_position = start_x+step_x*i
        if rm:
            node_id = nodes_dir[f"R{i}"]

            #STOP node
            response = requests.put(f'{cml_url}/nodes/{node_id}/state/stop', headers=headers, verify=False)
            if response.status_code == 200:
                print(f"R{i} stopped successfully")
            else:
                print(f"R{i} error during stopping")

            #WIPE node
            response = requests.put(f'{cml_url}/nodes/{node_id}/wipe_disks', headers=headers, verify=False)
            if response.status_code == 200:
                print(f"R{i} wipped successfully")
            else:
                print(f"R{i} error during wipping disk")

            #DELETE node
            response = requests.delete(f'{cml_url}/nodes/{node_id}', headers=headers, verify=False)

            if response.status_code == 200:
                print(f"R{i} removed successfully")
            else:
                print(f"R{i} error during removal")
            
        else:
            ## Add routers to lab
            data = {
                "label": f"R{i}",
                "node_definition":"csr1000v",
                "image_definition":"csr1000v-170302",
                "x":x_position,"y":-250,
                "tags":[]
            }
            
            ## ADDING new router to LAB
            response = requests.post(f'{cml_url}/nodes', headers=headers, json = data, verify=False)

            if response.status_code == 200:
                node_id = response.json()['id']
                print(f"R{i} addded successfully, node_id = {node_id}")
            else:
                print(f"R{i} error during adding")

            ## ADD Gig1 interface to router
            json_data = {
             'node': node_id,
             'slot': 0,
            }

            response = requests.post(f'{cml_url}/interfaces', headers=headers, json=json_data, verify=False)
            if response.status_code == 200:
                interface_id = response.json()[0]['id']
                print(f"GigabitEthernet1 on R{i} addded successfully, interface_id = {interface_id}")
            else:
                print(f"Error while adding interface GigabitEthernet1 on R{i}")

            ## Create LINK
            json_data = {
                'src_int': f'{interface_id}',
                'dst_int': f'{sw_interfaces[i+2]}',
            }

            response = requests.post(f'{cml_url}/links', headers=headers, json=json_data, verify=False)
            if response.status_code == 200:
                link_id = response.json()['id']
                print(f"GigabitEthernet1 on R{i} addded successfully, link_id = {link_id}")
            else:
                print(f"Error while adding interface GigabitEthernet1 on R{i}")


            ## CONFIGURE router

            data = f"""username {username}{i} privilege 15 password 0 {password}{i}
no ip domain lookup
ip domain name cisco
hostname R{i}
crypto key generate rsa modulus 1024
crypto key generate rsa label SSH modulus 1024
ip http server
ip http secure-server
ip http authentication local
interface GigabitEthernet1
 ip address 192.168.1.{i} 255.255.255.0
 no shu
 ip nat outside
interface VirtualPortGroup0 
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 exit
ip access-list extended NAT
 permit ip 192.168.10.0 0.0.0.255 any
 exit
line vty 0 15
 login local
 transport input ssh
iox"""

            response = requests.put(f'{cml_url}/nodes/{node_id}/config', headers=headers, data =data, verify=False)
            if response.status_code == 200:
                print(f"R{i} configured successfully")
            else:
                print(f"R{i} error during configuration")

            ## START router
            response = requests.put(f'{cml_url}/nodes/{node_id}/state/start', headers=headers, verify=False)
            if response.status_code == 200:
                print(f"R{i} start successfully")
            else:
                print(f"R{i} error during starting")
##

    #        response = requests.get(f'{cml_url}/tile', headers=headers, verify=False)
    #        click.echo(response.json())

@main.command()
@click.option('--number','-n',help='Number of routers',required=True,type=int)
@click.option('--password','-p',help='Password prefix',required=True,default='cisco')
@click.option('--username','-u',help='Username prefix',required=True,default='user')
@click.option('--command','-c',help='Command',required=True,default='python')

def verify(number,username,password,command):
    
    for i in range(1,number+1):
        # Connect to the server via SSH
        user = username+str(i)
        passwd = password+str(i)
        router_ip = '192.168.1.' + str(i)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(js_hostname, username=user, password=passwd)
        stdin, stdout, stderr = ssh.exec_command(f"pwd")
        # Check if the command was successful
        if stderr.read():
            print(f"Error for user {user} : {stderr.read().decode()}")
        else:
            print(f"Login as user {user}")
            
            # Transfer test script
            stdin, stdout, stderr = ssh.exec_command("rm test_script.py")
            sftp = ssh.open_sftp()
            local_path = './test_script.py'
            remote_path = 'test_script.py'
            sftp.put(local_path, remote_path)
            sftp.close()
            
            # Run test script
            stdin, stdout, stderr = ssh.exec_command(f"python3 test_script.py {router_ip} {user} {passwd} {command}")
            output = stdout.read().decode()
            if 'hostname' in output:
                print(f"Login to {router_ip} as user {user}")
            else:
                print(f"ERROR Login to {router_ip} as user {user}")
            print(output)
        # Close the SSH connection
        stdin, stdout, stderr = ssh.exec_command("rm test_script.py")
        ssh.close()

if __name__ == '__main__':
    main()



#    for i in range(1,number+1):
 ##       # Create new users
  ##      new_username = username + str(i)
   #     new_password = password + str(i)
   #     # Check if the user already exists
   #     stdin, stdout, stderr = ssh.exec_command(f"id {new_username}")
   #     user_exists = not bool(stderr.read())