import argparse
import scrapli
import re
import time

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Scrapli script to connect to a Cisco IOS-XE device and run show version")
parser.add_argument("host", help="IP address or hostname of the device")
parser.add_argument("username", help="Username for authentication")
parser.add_argument("password", help="Password for authentication")
parser.add_argument("commands", help="Choose which commands to run")

args = parser.parse_args()

# Define connection parameters using the command-line arguments
device = {
    "host": args.host,
    "auth_username": args.username,
    "auth_password": args.password,
    "auth_strict_key": False,  # Disable host key verification
    "platform": "cisco_iosxe",
}

# Create a Scrapli connection object
conn = scrapli.Scrapli(**device)


if args.commands == 'guestshell':
    # Open the connection
    conn.open()

    # Send the "show run | s hostname" command and print the output
    response = conn.send_command("show run | s hostname")
    print(response.result)

    # Send the "show iox" command and print the output
    response = conn.send_command("show iox")
    rex = re.compile(r'IOxman.*:\s+(.*)')
    w = rex.findall(response.result)
    if len(w) == 1:
        print("IOX is "+ w[0])
    else:
        print("IOX ERROR")

    # Send the "show app-hosting list" command and print the output
    response = conn.send_command("show app-hosting list")
    #rex = re.compile(r'IOxman.*:\s+(.*)')
    #w = rex.findall(response.result)
    print(response.result)

    #guestshell_commands = ['interface VirtualPortGroup0', 'ip address 192.168.10.1 255.255.255.0', 'interface VirtualPortGroup0', 'ip nat inside',  'interface GigabitEthernet1', 'ip nat outside', 'ip access-list extended NAT', 'permit ip 192.168.10.0 0.0.0.255 any', 'exit', 'ip nat inside source list NAT interface GigabitEthernet1 overload', 'app-hosting appid guestshell', 'app-vnic gateway0 virtualportgroup 0 guest-interface 0', 'guest-ipaddress 192.168.10.2 netmask 255.255.255.0', 'exit', 'app-default-gateway 192.168.10.1 guest-interface 0']

    #response = conn.send_configs(guestshell_commands)
    #print(response.result)

    #Enable guestshell
    #conn.send_command("guestshell enable")
elif args.commands == 'run':
    # Open the connection
    conn.open()
    commands=["guestshell run uname -a","guestshell run pwd","guestshell run df -h","guestshell run ls -la"]
    for j in commands:
        response = conn.send_command(j)
        print(response.result)


# Close the connection
conn.close()
