# LAB 2 - BGP EVPN on IOS-XE Cat9k using Terraform

## Lab Overview

This lab demonstrates how to configure BGP EVPN VXLAN on Cisco Catalyst 9000 Series Switches running Cisco IOS XE software using Terraform. 

`Note` This lab focus on interacting with Cisco IOS-XE devices using Terraform and not on an in-depth technical exploration of BGP EVPN VXLAN. As a result, a deep understanding of EVPN is not required.

### BGP EVPN VXLAN

BGP EVPN VXLAN is a campus network solution for Cisco Catalyst 9000 Series Switches running Cisco IOS XE software. It is designed to provide L2/L3 network services with greater flexibility, mobility, and scalability and also address the well-known classic networking protocols challenges.

You can find additional information and the fundamental terminology necessary to understand BGP EVPN VXLAN through the following links:

- [BGP EVPN VXLAN Overview](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-8/configuration_guide/vxlan/b_178_bgp_evpn_vxlan_9300_cg/bgp_evpn_vxlan_overview.html)

- [Why Transition to BGP EVPN VXLAN in Enterprise Campus](https://blogs.cisco.com/networking/why-transition-to-bgp-evpn-vxlan-in-enterprise-campus)

- [Configuring EVPN VXLAN Layer 3 Overlay Network](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-8/configuration_guide/vxlan/b_178_bgp_evpn_vxlan_9300_cg/configuring_evpn_vxlan_layer_3_overlay_network.html)
- [Configuring EVPN VXLAN Layer 2 Overlay Network](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-8/configuration_guide/vxlan/b_178_bgp_evpn_vxlan_9300_cg/configuring_evpn_vxlan_layer_2_overlay_network.html)


<br>

In this lab we will be using modified code from [terraform-iosxe-evpn-example](https://github.com/netascode/terraform-iosxe-evpn-example) with [IOS-XE Provider](https://registry.terraform.io/providers/netascode/iosxe/latest/docs) and following modified Terraform modules:

- [evpn-ospf-underlay](https://registry.terraform.io/modules/netascode/evpn-ospf-underlay/iosxe/latest)
- [evpn-overlay](https://registry.terraform.io/modules/netascode/evpn-overlay/iosxe/latest)

`Note` Make sure to use version 0.3.3 of iosxe provider.

<br>

## Pre-requisites

- Use an IDE of your choice. This tutorial will assume Visual Studio Code

- Git installed

- `terraform` version 1.5.X installed on your local machine [Terraform](https://developer.hashicorp.com/terraform/downloads)

- Access to Catalyst 9000 series switches (2x Leafs, 1xSpine)

- Access to the internet

- Basic understanding of Terraform

## Time Estimates

60 minutes

<br></br>

## 1. Clone terraform-bootcamp repository to workstation

`Note` If you already clone the repository you can skip below steps and go to next task #2

Click on `Windows CMD prompt` icon on Workstation Desktop

![terraform_1](images/terraform_1.png)

Clone terraform-bootcamp-evpn repository to Desktop by running following command:

`git clone https://github.com/kuba-mazurkiewicz/terraform-bootcamp.git`

![terraform_2](images/terraform_2.png)

You will be asked to Sign in to GitHub. Use following `access token`:

```
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
```

![terraform_3](images/terraform_3.png)

After cloning the repository, open the repository folder on your desktop. Right-click on the `terraform-bootcamp` folder and select `Open with Code`

![terraform_4](images/terraform_4.png)

<br>

## 2. Remove legacy routing configuration from leafs and spine

On GigabitEthernet1/0/1 on leafs and GigabitEthernet1/0/1-2 on spine there is isis routing protcol configure. In our lab we will be using OSPF as underaly routing protocol. If we don't remove isis routing protocol from interfaces terraform destroy will not work properly (isis is not supported by iosxe provider).

To remove isis use following steps:

1. Install netmiko python library by running command `ip install netmiko`:

```ps
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> pip install netmiko
```

2. Navigate to scripts folder in labs/lab2/evpn/ and run python script `python remove_isis.py`

```ps
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn\scripts> python remove_isis.py
ISIS protocol removed from 198.18.1.21 - interface GigabitEthernet1/0/1
ISIS protocol removed from 198.18.1.21 - interface GigabitEthernet1/0/2
ISIS protocol removed from 198.18.1.31 - interface GigabitEthernet1/0/1
ISIS protocol removed from 198.18.1.32 - interface GigabitEthernet1/0/1
```

<br>

## 3. Inspect yaml files in `data` directory

The configuration is derived from a set of yaml files in the data directory. This allows to configure BGP EVPN VXLAN in minutes using an easy to use data model. It takes away the complexity of having to deal with references, dependencies or loops. By completely separating data (defining variables) from logic (infrastructure declaration), it allows the user to focus on describing the intended configuration while using a set of terraform modules.

Same approach is being used in `Cisco Nexus-as-Code` project. More information can be found here: https://cisco.com/go/nexusascode

<br>

To inspect files open Terminal in Visual Studio Code Editor by selecting `Terminal -> New Terminal`

![terraform_5](images/terraform_5.png)

![terraform_6](images/terraform_6.png)

Navigate to labs/lab2/evpn folder in terminal by executing command: `cd labs/lab2/evpn`

![terraform_10](images/terraform_10.png)

and expand same evpn folder on right hand side of Visual Studio Code to inspect files in Editor:

![terraform_11](images/terraform_11.png)

File `inventory.yaml` contains hostnames and urls for spine and leafs used in lab topology:

![terraform_13](images/terraform_13.png)

```yaml
---
fabric:
  inventory:
    spines:
      - name: SPINE-1
        url: https://198.18.1.21     
    leafs:
      - name: LEAF-1
        url: https://198.18.1.31
      - name: LEAF-2
        url: https://198.18.1.32
```

<br>

File `underlay.yaml` contains data used to configure ospf underlay between spine and leafs:

![terraform_12](images/terraform_12.png)

```yaml
---
fabric:
  underlay:
    loopbacks:
      - device: SPINE-1
        ipv4_address: 100.65.0.1
      - device: LEAF-1
        ipv4_address: 100.65.0.2
      - device: LEAF-2
        ipv4_address: 100.65.0.3

    vtep_loopbacks:
      - device: LEAF-1
        ipv4_address: 10.1.200.1
      - device: LEAF-2
        ipv4_address: 10.1.200.2

    loopback_id: 0
    pim_loopback_id: 100

    fabric_interface_type: GigabitEthernet
    leaf_fabric_interface_prefix: 1/0/
    leaf_fabric_interface_offset: 1
    spine_fabric_interface_prefix: 1/0/
    spine_fabric_interface_offset: 1

    anycast_rp_ipv4_address: 100.1.101.1

    ethernets:
      - device: SPINE-1
        name: 1/0/1
        ipv4_address: 100.64.0.1
        ipv4_address_mask: 255.255.255.252
      - device: SPINE-1
        name: 1/0/2
        ipv4_address: 100.64.0.5
        ipv4_address_mask: 255.255.255.252
      - device: LEAF-1
        name: 1/0/1
        ipv4_address: 100.64.0.2
        ipv4_address_mask: 255.255.255.252
      - device: LEAF-2
        name: 1/0/1
        ipv4_address: 100.64.0.6
        ipv4_address_mask: 255.255.255.252
```

<br>

File `overlay.yaml` contains data used to construct overlay L2 VNI on leafs:

![terraform_14](images/terraform_14.png)

```yaml
---
fabric:
  overlay:
    bgp_asn: 65000

    l2_services:
      - name: GREEN_10
        id: 10
        ipv4_multicast_group: 225.0.1.1
        ipv4_address: 10.10.10.1
        ipv4_mask: 255.255.255.0
        ip_learning: true
        re_originate_route_type5: true
```

<br>


## 4. Initialize a working directory (terraform init)

Run `terraform init` command to prepare working directory:

![terraform_7](images/terraform_7.png)

Terraform init command performs following steps:

1. Backend Initialization
```sh
Initializing the backend...
```

2. Module Installation

```
Initializing modules...
- iosxe_evpn_ospf_underlay in modules\terraform-iosxe-evpn-ospf-underlay
- iosxe_evpn_overlay in modules\terraform-iosxe-evpn-overlay
```

3. Provider Plugin Installation

```sh
Initializing provider plugins...
- Finding ciscodevnet/iosxe versions matching "0.3.3"...
- Finding netascode/utils versions matching ">= 0.2.4"...
- Installing ciscodevnet/iosxe v0.3.3...
- Installed ciscodevnet/iosxe v0.3.3 (signed by a HashiCorp partner, key ID 974C06066198C482)
- Installing netascode/utils v0.2.5...
- Installed netascode/utils v0.2.5 (self-signed, key ID 48630DA58CAFD6C0)
```

## 5. Provide credentials

Before provisioning infrastructure, you need to provide Terraform with credentials to access spines and leaves. This can be done either via  environment variables or by updating the provider configuration in main.tf.

Let's update main.tf provider configuration with following data:

```sh
provider "iosxe" {
  username = "developer"
  password = "C1sco12345"
  devices  = local.devices
}
```

Open main.tf file in Visual Studio Code and paste following 2 lines after line 25 in provider "iosxe" section:

```sh
  username = "developer"
  password = "C1sco12345"
```

![terraform_8](images/terraform_8.png)

<br>

## 6. Create execution plan (terraform plan)

Run `terraform plan` command to preview changes that Terraform plans to make to your infrastructure.

We will run terrafrom plan command with `--out=plan.tfplan` flag, which will save execution plan to file. In the next section we will use this file as input when executing `terraform apply` command.

```sh
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> terraform plan --out=plan.tfplan
data.utils_yaml_merge.model: Reading...
data.utils_yaml_merge.model: Read complete after 0s [id=1402c6957b6f4cecae36251e28434bd2ec4acaf1]

Terraform used the selected providers to generate the following execution plan.      
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.1"] will be created
  + resource "iosxe_interface_ethernet" "ethernet_fabric_interface" {
      + device            = "SPINE-1"
      + id                = (known after apply)
      + ipv4_address      = "100.64.0.1"
      + ipv4_address_mask = "255.255.255.252"
      + name              = "1/0/1"
      + shutdown          = false
      + switchport        = false
      + type              = "GigabitEthernet"
    }

  # module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.2"] will be created
  + resource "iosxe_interface_ethernet" "ethernet_fabric_interface" {
      + device            = "LEAF-1"
      + id                = (known after apply)
      + ipv4_address      = "100.64.0.2"
      + ipv4_address_mask = "255.255.255.252"
      + name              = "1/0/1"
      + shutdown          = false
      + switchport        = false
      + type              = "GigabitEthernet"
    }

...
<snip>
...

  # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"] will be created
  + resource "iosxe_interface_vlan" "l2_svi" {
      + autostate         = false
      + device            = "LEAF-1"
      + id                = (known after apply)
      + ipv4_address      = "10.10.10.1"
      + ipv4_address_mask = "255.255.255.0"
      + name              = 10
    }

  # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"] will be created
  + resource "iosxe_interface_vlan" "l2_svi" {
      + autostate         = false
      + device            = "LEAF-2"
      + id                = (known after apply)
      + ipv4_address      = "10.10.10.1"
      + ipv4_address_mask = "255.255.255.0"
      + name              = 10
    }

  # module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"] will be created
  + resource "iosxe_vlan_configuration" "l2_vlan_configuration" {
      + device            = "LEAF-1"
      + evpn_instance     = 10
      + evpn_instance_vni = 10010
      + id                = (known after apply)
      + vlan_id           = 10
    }

  # module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"] will be created
  + resource "iosxe_vlan_configuration" "l2_vlan_configuration" {
      + device            = "LEAF-2"
      + evpn_instance     = 10
      + evpn_instance_vni = 10010
      + id                = (known after apply)
      + vlan_id           = 10
    }

Plan: 62 to add, 0 to change, 0 to destroy.

──────────────────────────────────────────────────────────────────────────────────── 

Saved the plan to: plan.tfplan

To perform exactly these actions, run the following command to apply:
    terraform apply "plan.tfplan"
```

Your output might be different from sample output above, but at the end of the output you will see a summary of number of objects that will be added,changed or deleted.

![terraform_9](images/terraform_9.png)

At this stage no configuration changes will be made to spine and leaf devices, but the devices will be queried to refresh state entries in Terraform statefile (if any).

<br>

## 7. Apply execution plan (terraform apply)

The terraform `apply` command is used to apply changes in the configuration. We will use terraform apply with `plan.tfplan` file saved in previous step by running following command:

`terraform apply --parallelism=1 plan.tfplan`

`Note` The parallelism option in Terraform controls the number of resource operations (creation, updating, deletion, etc.) that can be performed concurrently. By default (10), Terraform attempts to perform these operations in parallel to improve efficiency and reduce the time it takes to apply changes. Parallel operations in Terraform can potentially cause errors when the underlying API is slow and unable to handle the requests. We will be creating 1 object at a time (`--parallelism=1`)

```sh
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> terraform apply 
--parallelism=1 plan.tfplan
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.pim_loopback["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.pim_loopback["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=100]       
module.iosxe_evpn_ospf_underlay.iosxe_msdp.msdp["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_msdp.msdp["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/ip/Cisco-IOS-XE-multicast:msdp]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.6"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.6"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.5"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.5"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/Vlan=10]
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Vlan=10]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-2"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp.bgp["SPINE-1"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["SPINE-1"]: Creation complete after 2s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-1"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["SPINE-1"]: Creation complete after 0s 
[id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-2/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-2/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-2/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-2/0"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.pim_loopback_interface_pim["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.pim_loopback_interface_pim["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=100/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-1"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/Loopback=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=1]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-2/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-2/SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.3]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-1/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-1/SPINE-1"]: Creation complete after 4s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.2]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-1/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-1/SPINE-1"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-2/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-2/SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-2"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-2"]: Creation complete after 4s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.pim_loopback_interface_ospf_process["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.pim_loopback_interface_ospf_process["SPINE-1"]: Creation complete after 4s [id=Cisco-IOS-XE-native:native/interface/Loopback=100/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["SPINE-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-2"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-2/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-2/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]        
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]        
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/0"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/0"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]      
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]      
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-2"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-1"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-2"]: Creating...
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-2"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/pim]
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-1/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-1/SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.2]
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-1/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-1/SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-2/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-2/SPINE-1"]: Creation complete after 3s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.3]
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-2/SPINE-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-2/SPINE-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-2"]: Creating...
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-2"]: Creation complete after 4s [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn]
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-1"]: Creation complete after 
0s [id=Cisco-IOS-XE-native:native/interface/nve=1]
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-1"]: Creating...
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-1"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn]
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-2"]: Creating...
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-2"]: Creation complete after 
0s [id=Cisco-IOS-XE-native:native/interface/nve=1]
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-1/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-1/10"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn-instance/evpn/instance/instance=10]
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-2/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-2/10"]: Creation complete after 1s [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn-instance/evpn/instance/instance=10]
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10]
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"]: Creating...
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"]: Creation complete after 0s [id=Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10]

Apply complete! Resources: 62 added, 0 changed, 0 destroyed.
```

<br>

We are using the local filesystem for the Terraform state file (`terraform.tfstate`) in this lab. Once terraform plan has been executed, Terraform updates project’s state file to reflect the changes made to the resources. This file is then unlocked so that new changes can be applied.

```ps
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> ls terraform.tfstate


    Directory: C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         8/20/2023  12:04 PM         122221 terraform.tfstate

```

You can view content of `terraform.tfstate` file in Visual Studio Code:

![terraform_15](images/terraform_15.png)

<br>

## 8. Verify BGP EVPN VXLAN Configuration


Once the configuration changes have been applied to spine and leafs devices we can verify the EVPN operational status by using Putty to login to devices.

Use the following details to log in to the devices:

| Device Name | Device IP | username / password | 
| --- | --- | --- |
| C9k-spine | 198.18.1.21 | developer/C1sco12345 | 
| C9k-leaf1 | 198.18.1.31 | developer/C1sco12345 | 
| C9k-leaf2 | 198.18.1.32 | developer/C1sco12345 | 


1. Use `show bgp l2vpn evpn summary` on C9k-spine (198.18.1.21) device to verify Spine BGP peering to the VTEP(s) in the EVPN address-family:

![terraform_16](images/terraform_16.png)


1. Use `show bgp l2vpn evpn summary` on C9k-leaf1 (198.18.1.31) and C9k-leaf2 (198.18.1.32) to verify VTEP BGP peering to the Spine in the EVPN address-family:

![terraform_17](images/terraform_17.png)

3. Use `show nve peers` to verify NVE peer relationship:

![terraform_18](images/terraform_18.png)

4. You can also verify operational status by checking if you have network connectivity between two ubuntu machines in CML.

- Open Google Chrome and click on CML bookmark:

![cml_1](images/cml_1.png)

- Login with credentials:

| username / password | 
| --- |
| guest/C1sco12345 | 
 

- Enter lab and locate 2 ubuntu machines (ubuntu-1 and ubuntu-2)

- Click on ubuntu-1 machine and open Console (if you are asked for username and password type: cisco / cisco)

![cml_2](images/cml_2.png)

- Ping ubuntu-2 machine (10.10.10.11)

![cml_3](images/cml_3.png)

`Note` ubuntu-2 machine might be misconfigured in this lab and ping might be unsuccessful. To check that open Console for ubuntu-2 machine and execute command: `ip addr show ens3`. If ip address is not matching 10.10.10.11 then change it using the following commands:
- ` sudo ip addr del 10.10.11.10/24 dev ens3 ` -  remove the current IP address assigned to the ens3 interface. Please be aware that the IP address "10.10.11.10/24" provided here is just an example. If you possess a different IP address while checking ``` ip -br a ```, kindly indicate your own.
- ` sudo ip addr add 10.10.10.11/24 dev ens3 ` - assign the new IP address.

<br>

## 9. Updating existing network configuration state

Because we've separated data from the Terraform code, making changes to the existing network configuration only requires editing the files in the data folder.

Let's change ipv4 address on SVI for VLAN10 from 10.10.10.1 to 192.168.10.1.

To do this open `overlay.yaml` file in Visual Studio Code and edit line nr 10:

change: 

```yaml
ipv4_address: 10.10.10.1
```

to:

```yaml
ipv4_address: 192.168.10.1
```

![terraform_19](images/terraform_19.png)

Now run `terraform plan` to check what changes terraform will make:

```sh
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> terraform plan  

<snip>

Terraform used the selected providers to generate the following execution plan.      
Resource actions are indicated with the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"] will be updated in-place
  ~ resource "iosxe_interface_vlan" "l2_svi" {
        id                = "Cisco-IOS-XE-native:native/interface/Vlan=10"
      ~ ipv4_address      = "10.10.10.1" -> "192.168.10.1"
        name              = 10
        # (3 unchanged attributes hidden)
    }

  # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"] will be updated in-place
  ~ resource "iosxe_interface_vlan" "l2_svi" {
        id                = "Cisco-IOS-XE-native:native/interface/Vlan=10"
      ~ ipv4_address      = "10.10.10.1" -> "192.168.10.1"
        name              = 10
        # (3 unchanged attributes hidden)
    }

Plan: 0 to add, 2 to change, 0 to destroy.

──────────────────────────────────────────────────────────────────────────────────── 

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee 
to take exactly these actions if you run "terraform apply" now.
```

In the summary terraform will flag the changes which will be executed to existing infrastructure with `terraform apply` command.

You can see that there would be 2 changes to resource "iosxe_interface_vlan" "l2_svi" on both leaf devices. IP Address on SVI for VLAN10 will be change from 10.10.10.1 to 192.168.10.1.

Let's run `terraform apply` command now:

```sh
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> terraform apply

<snip>

Apply complete! Resources: 0 added, 2 changed, 0 destroyed.
```

<br>

Verify that SVI IP Address for VLAN 10 on both leaf devices changed by running `show ip int brief` on both leaf devices:

![terraform_20](images/terraform_20.png)

<br>

## 10. Remove all network configurations for BGP EVPN VXLAN (terraform destroy)

To remove all network configurations for BGP EVPN VXLAN we can simply execute `terraform destroy --parallelism=1` command.

`Note` The parallelism option in Terraform controls the number of resource operations (creation, updating, deletion, etc.) that can be performed concurrently. By default (10), Terraform attempts to perform these operations in parallel to improve efficiency and reduce the time it takes to apply changes. Parallel operations in Terraform can potentially cause errors when the underlying API is slow and unable to handle the requests. We will be creating 1 object at a time (`--parallelism=1`)

Terraform destroy is used to tear down or destroy the resources that were created or managed using a Terraform configuration. When you run terraform destroy, Terraform identifies the resources defined in your configuration and takes the necessary actions to remove all managed resources in the Terraform state file.

```sh
PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn>terraform destroy

data.utils_yaml_merge.model: Reading...
data.utils_yaml_merge.model: Read complete after 0s [id=9f71c787c903954d0aedfaafb0496dd26ba1cf33]

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

<snip>

    # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"] will be destroyed
  - resource "iosxe_interface_vlan" "l2_svi" {
      - autostate         = false -> null
      - device            = "LEAF-1" -> null
      - id                = "Cisco-IOS-XE-native:native/interface/Vlan=10" -> null   
      - ipv4_address      = "192.168.10.1" -> null
      - ipv4_address_mask = "255.255.255.0" -> null
      - name              = 10 -> null
    }

  # module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"] will be destroyed
  - resource "iosxe_interface_vlan" "l2_svi" {
      - autostate         = false -> null
      - device            = "LEAF-2" -> null
      - id                = "Cisco-IOS-XE-native:native/interface/Vlan=10" -> null   
      - ipv4_address      = "192.168.10.1" -> null
      - ipv4_address_mask = "255.255.255.0" -> null
      - name              = 10 -> null
    }

  # module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"] will be destroyed
  - resource "iosxe_vlan_configuration" "l2_vlan_configuration" {
      - device            = "LEAF-1" -> null
      - evpn_instance     = 10 -> null
      - evpn_instance_vni = 10010 -> null
      - id                = "Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10" -> null
      - vlan_id           = 10 -> null
    }

  # module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"] will be destroyed
  - resource "iosxe_vlan_configuration" "l2_vlan_configuration" {
      - device            = "LEAF-2" -> null
      - evpn_instance     = 10 -> null
      - evpn_instance_vni = 10010 -> null
      - id                = "Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10" -> null
      - vlan_id           = 10 -> null
    }

Plan: 0 to add, 0 to change, 62 to destroy.

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-2/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-2/0"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.leaf_interface_ospf_process["LEAF-1/0"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-1/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.1]        
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-1/SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-1"]: Destruction complete after 4s
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-2/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.1]        
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_leaf["LEAF-2/SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/0"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-2"]: Destruction complete after 4s
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"]: Destroying... [id=Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10]
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-2/10"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.pim_loopback_interface_pim["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=100/ip/pim]    
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.pim_loopback_interface_pim["SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.pim_loopback_interface_ospf_process["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=100/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.pim_loopback_interface_ospf_process["SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"]: Destroying... [id=Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:configuration=10]
module.iosxe_evpn_overlay.iosxe_vlan_configuration.l2_vlan_configuration["LEAF-1/10"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-2/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-2/0"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-1/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.2]       
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-1/SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.loopback_interface_pim["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_msdp.msdp["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/ip/Cisco-IOS-XE-multicast:msdp]
module.iosxe_evpn_ospf_underlay.iosxe_msdp.msdp["SPINE-1"]: Destruction complete after 4s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/nve=1]
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.spine_interface_pim["SPINE-1/0"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=0/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.loopback_interface_ospf_process["SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-2/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn/l2vpn-evpn/neighbor=100.65.0.3]       
module.iosxe_evpn_overlay.iosxe_bgp_l2vpn_evpn_neighbor.bgp_l2vpn_evpn_neighbor_spine["LEAF-2/SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/pim]      
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Vlan=10]
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-1/10"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.leaf_interface_pim["LEAF-1/0"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/nve=1]
module.iosxe_evpn_overlay.iosxe_interface_nve.nve["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.spine_interface_ospf_process["SPINE-1/1"]: Destruction complete after 2s
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/ip/pim]
module.iosxe_evpn_ospf_underlay.iosxe_pim.pim["SPINE-1"]: Destruction complete after 
0s
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Vlan=10]
module.iosxe_evpn_overlay.iosxe_interface_vlan.l2_svi["LEAF-2/10"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/pim]      
module.iosxe_evpn_ospf_underlay.iosxe_interface_pim.vtep_loopback_interface_pim["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-1/0"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-2/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.leaf_interface_ospf["LEAF-2/0"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-2/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-2/SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-1/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.1]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_leaf["LEAF-1/SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.pim_loopback["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=100]
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.pim_loopback["SPINE-1"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-1/10"]: Destroying... [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn-instance/evpn/instance/instance=10]
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-1/10"]: Destruction complete after 4s
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-2/10"]: Destroying... [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn-instance/evpn/instance/instance=10]
module.iosxe_evpn_overlay.iosxe_evpn_instance.l2_evpn_instance["LEAF-2/10"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-1/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.2]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-1/SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["SPINE-1"]: Destruction complete after 3s
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/address-family/no-vrf/l2vpn=evpn]
module.iosxe_evpn_overlay.iosxe_bgp_address_family_l2vpn.bgp_l2vpn["LEAF-1"]: Destruction complete after 1s
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-2/SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000/neighbor=100.65.0.3]
module.iosxe_evpn_overlay.iosxe_bgp_neighbor.bgp_neighbor_spine["LEAF-2/SPINE-1"]: Destruction complete after 3s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/1"]: Destruction complete after 4s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/0"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1/ip/Cisco-IOS-XE-ospf:router-ospf/ospf]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ospf.spine_interface_ospf["SPINE-1/0"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf/ospf/process-id=1]
module.iosxe_evpn_ospf_underlay.iosxe_ospf.ospf["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn]
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/l2vpn/Cisco-IOS-XE-l2vpn:evpn_cont/evpn]
module.iosxe_evpn_overlay.iosxe_evpn.evpn["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_overlay.iosxe_bgp.bgp["SPINE-1"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["SPINE-1"]: Destruction complete after 1s
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp=65000]
module.iosxe_evpn_overlay.iosxe_bgp.bgp["LEAF-2"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-1"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/Loopback=1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_loopback.vtep_loopback["LEAF-2"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.2"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.2"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.1"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.1"]: Destruction complete after 1s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.6"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F1]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.6"]: Destruction complete after 0s
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.5"]: Destroying... [id=Cisco-IOS-XE-native:native/interface/GigabitEthernet=1%2F0%2F2]
module.iosxe_evpn_ospf_underlay.iosxe_interface_ethernet.ethernet_fabric_interface["100.64.0.5"]: Destruction complete after 1s

Destroy complete! Resources: 62 destroyed.

PS C:\Users\Administrator\Desktop\terraform-bootcamp\labs\lab2\evpn> 
```

Confirm that you want to proceed by removing these resources (network configuration), by typing yes

```
Destroy complete! Resources: 62 destroyed.
```

You’ve now successfully deleted all your BGP EVPN VXLAN network configuration that was deployed with Terraform on your Catalyst 9000 Switches running IOS-XE.


<br></br>

---

### Congratulations on your successful completion of the Terraform lab with BGP EVPN VXLAN on Cisco Catalyst 9K Switches. Well done!
