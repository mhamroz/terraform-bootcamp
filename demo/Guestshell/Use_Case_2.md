# CONFIGURE LOOPBACK INTERFACE ON REMOTE DEVICE

This is EEM applet with Python script which configures Loopback interface on remote device if Loopback interface on local device is down (we will monitor if route to Loopback ip address is present on local device)

EEM script will run every minute

```
event timer cron cron-entry "*/1 * * * *"
```

and python script would be executed to run `show ip route | include Loopback10` command, if output would be empty then scrapli connection will be established to remote device and Loopback10 with same ip address will be configured.

<br>

## EEM applet

```
event manager applet LOOPBACK_10
event timer cron cron-entry "*/1 * * * *"
action 1.0 cli command "en"
action 2.0 cli command "guestshell run python3 loopback.py"
exit
exit
```

<br>

## Python script

```
from scrapli.driver.core import IOSXEDriver
import cli

route_output = cli.cli('show ip route | in Loopback10')
if '11.11.11.11' in route_output:
    print('Loopback10 up, route exists')
else:

    commands = ['conf t','interface Loopback10','ip address 11.11.11.11 255.255.255.255']

    router = {
        "host": "10.48.35.102",
        "auth_username": "cisco",
        "auth_password": "cisco",
        "auth_strict_key": False
    }

    conn = IOSXEDriver(**router)
    conn.open()
    check_loopback = conn.send_command('show ip route | in Loopback10')
    if '11.11.11.11' in check_loopback.result:
        print('Loopback10 down on local device, up on remote')
    else:
        execute_commands = conn.send_commands(commands)
        print(execute_commands.result)
        print('Loopback10 down, configuring Loopback10 on host: 10.48.35.102 !!!')
    
    conn.close()

```

<br></br>

Note. `debug EEM`

```
terminal monitor 
debug event manager action cli
```