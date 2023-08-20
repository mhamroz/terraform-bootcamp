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

In this lab we will be using code [terraform-iosxe-evpn-example](https://github.com/netascode/terraform-iosxe-evpn-example) with [IOS-XE Provider](https://registry.terraform.io/providers/netascode/iosxe/latest/docs) and following Terraform modules:

- [evpn-ospf-underlay](https://registry.terraform.io/modules/netascode/evpn-ospf-underlay/iosxe/latest)
- [evpn-overlay](https://registry.terraform.io/modules/netascode/evpn-overlay/iosxe/latest)


<br>

## Pre-requisites

- Use an IDE of your choice. This tutorial will assume Visual Studio Code

- Git installed

- Docker installed

- `terraform` version 1.5.X installed on your local machine [Terraform](https://developer.hashicorp.com/terraform/downloads)

- Access to Catalyst 9000 series switches (2x Leafs, 1xSpine)

- Access to the internet

- Basic understanding of Terraform

## Time Estimates

45 minutes

<br></br>

## 1. Clone terraform-bootcamp repository to workstation

Click on `Windows CMD prompt` icon on Workstation Desktop

![terraform_1](images/terraform_1.png)

Clone terraform-bootcamp-evpn repository to Desktop by running following command:

`git clone https://github.com/kuba-mazurkiewicz/terraform-bootcamp.git`

![terraform_2](images/terraform_2.png)

You will be asked to Sign in to GitHub. Use `access token` provided during labs

![terraform_3](images/terraform_3.png)

After cloning the repository, open the repository folder on your desktop. Right-click on the `terraform-bootcamp` folder and select `Open with Code`

![terraform_4](images/terraform_4.png)


Open Terminal in Visual Studio Code Editor by selecting `Terminal -> New Terminal`

![terraform_5](images/terraform_5.png)

![terraform_6](images/terraform_6.png)

<br>

## 2. Inspect yaml files in `data` directory

The configuration is derived from a set of yaml files in the data directory. This allows to configure BGP EVPN VXLAN in minutes using an easy to use data model. It takes away the complexity of having to deal with references, dependencies or loops. By completely separating data (defining variables) from logic (infrastructure declaration), it allows the user to focus on describing the intended configuration while using a set of terraform modules.

Same approach is being used in `Cisco Nexus-as-Code` project. More information can be found here: https://cisco.com/go/nexusascode

<br>

File `inventory.yaml` contains hostnames and urls for spine and leafs used in lab topology:

```
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

```
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
```

<br>

File `overlay.yaml` contains data used to construct overlay L2 VNI and L3 VNI on leafs:

```
---
fabric:
  overlay:
    bgp_asn: 65000

    l3_services:
      - name: GREEN
        id: 1000
      - name: BLUE
        id: 1010

    l2_services:
      - name: L2_101
        id: 101
        ipv4_multicast_group: 225.0.0.101
        ip_learning: true
      - name: L2_102
        id: 102
      - name: GREEN_1000
        id: 10
        ipv4_multicast_group: 225.0.1.1
        l3_service: GREEN
        ipv4_address: 10.10.10.1
        ipv4_mask: 255.255.255.0
        ip_learning: true
        re_originate_route_type5: true
      - name: BLUE_1011
        id: 1011
        l3_service: BLUE
        ipv4_address: 172.17.1.1
        ipv4_mask: 255.255.255.0
```

<br>


## 3. Initialize a working directory (terraform init)

Run `terraform init` command to prepare working directory:

![terraform_7](images/terraform_7.png)

Terraform init command performs following steps:

1. Backend Initialization
```
Initializing the backend...
```

2. Module Installation

```
Initializing modules...
- iosxe_evpn_ospf_underlay in modules\terraform-iosxe-evpn-ospf-underlay
- iosxe_evpn_overlay in modules\terraform-iosxe-evpn-overlay
```

3. Provider Plugin Installation

```
Initializing provider plugins...
- Finding ciscodevnet/iosxe versions matching ">= 0.3.0"...
- Finding netascode/utils versions matching ">= 0.2.4"...
- Installing netascode/utils v0.2.5...
- Installed netascode/utils v0.2.5 (self-signed, key ID 48630DA58CAFD6C0)
- Installing ciscodevnet/iosxe v0.3.3...
- Installed ciscodevnet/iosxe v0.3.3 (signed by a HashiCorp partner, key ID 974C06066198C482)
```

## 4. Provide credentials

Before provisioning infrastructure, you need to provide Terraform with credentials to access spines and leaves. This can be done either via  environment variables or by updating the provider configuration in main.tf.

Let's update main.tf provider configuration with following data:

```
provider "iosxe" {
  username = "developer"
  password = "C1sco12345"
  devices  = local.devices
}
```

Open main.tf file in Visual Studio Code and paste following 2 lines after line 25 in provider "iosxe" section:

```
  username = "developer"
  password = "C1sco12345"
```

![terraform_8](images/terraform_8.png)

## 4. Create execution plan (terraform plan)

Run `terraform plan` command to preview changes that Terraform plans to make to your infrastructure.

![terraform_9](images/terraform_9.png)


<br></br>

---

### Congratulations on completing the Docker Introduction lab! You have taken an important step in learning how to use Docker to build, ship, and run applications in a containerized environment.