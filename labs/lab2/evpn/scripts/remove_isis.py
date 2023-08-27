from netmiko import ConnectHandler

creds = {"username": "developer", "password":"C1sco12345"}
devices = [{"ip": "198.18.1.21","interfaces": ["GigabitEthernet1/0/1","GigabitEthernet1/0/2"]},{"ip":"198.18.1.31","interfaces":["GigabitEthernet1/0/1"]},{"ip":"198.18.1.32","interfaces":["GigabitEthernet1/0/1"]}]

for i in devices:
    my_device = {
        "device_type": "cisco_ios",
        "ip": i["ip"],
        "username": creds["username"],
        "password": creds["password"],
    }

    for inter in i["interfaces"]:
        interface = f"interface {inter}"
        print(f"ISIS protocol removed from {interface}")
       
        net_connect =ConnectHandler(**my_device)
        net_connect.send_config_set([interface, "no ip router isis"])