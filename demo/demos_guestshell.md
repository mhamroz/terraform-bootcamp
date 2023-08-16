GUESTSHELL LAB DEVICE:
10.48.35.207 cisco:cisco

1. Example from lab: interface up
file: no_shut_int..py

cat << EOF > no_shut_int.py
import cli
import argparse
# Command line argument to specify interface
parser = argparse.ArgumentParser()
parser.add_argument("interface", help="Interface to bring up")
args = parser.parse_args()
# List of commands to execute
commands = [f'interface {args.interface}','no shut']
# Run commands using cli module
cli.configure(commands)
print(f'Interface {args.interface} was bringed up!!!')
EOF

event manager applet INTERFACE-DOWN
event syslog pattern "%LINEPROTO-5-UPDOWN.*changed state to down"
action 1.0 regexp "Interface\s+([^,]+)" $_syslog_msg match ifname
action 2.0 cli command "en"
action 3.0 cli command "guestshell run python3 no_shut_int.py $ifname"
exit
exit
 
debug eem:
terminal monitor 
debug event manager action cli


3. Use case 2: Webex:

file: message.py

event manager applet CONFIG_CHANGED
 event syslog pattern "%SYS-5-CONFIG_I: Configured from console by.*"
 action 1.0 regexp "\n*from console by ([^\s]+)" "$_syslog_msg" match user
 action 2.0 regexp "\n*from console by.*\(([^\)]+)" "$_syslog_msg" match from
 action 3.0 set text "$user,$from"
 action 4.0 cli command "en"
 action 5.0 cli command "guestshell run python3 message.py Yjc1ZjkzNTItMjcyNy00ZDQxLTkyNGYtYTRkMGRkMGVjZDdkNmI4ZmYzNzQtMGNj_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f kmazurki@cisco.com --text $text"

debug eem:
terminal monitor 
debug event manager action cli



3. Use case 2 : Remote device loopback

file: loopback.py

event manager applet LOOPBACK_10
event timer cron cron-entry "*/1 * * * *"
action 1.0 cli command "en"
action 2.0 cli command "guestshell run python3 loopback.py"
exit
exit

REMOTE DEVICE 10.48.35.102 loopback10 should be removed from this device

on 10.48.35.207 loopback10 with ip address 11.11.11.11 255.255.255.255 needs to exist

debug eem:
terminal monitor 
debug event manager action cli