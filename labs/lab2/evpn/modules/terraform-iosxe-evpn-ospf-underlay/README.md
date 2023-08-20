<!-- BEGIN_TF_DOCS -->
[![Tests](https://github.com/netascode/terraform-iosxe-evpn-ospf-underlay/actions/workflows/test.yml/badge.svg)](https://github.com/netascode/terraform-iosxe-evpn-ospf-underlay/actions/workflows/test.yml)

# Terraform IOS-XE EVPN OSPF Underlay Module

This module can manage a Catalyst 9000 EVPN fabric underlay network based on OSPF.

The following assumptions have been made:

- IP unnumbered is used on all fabric links
- OSPF area 0 is used for all interfaces
- PIM sparse mode is enabled on all interfaces
- A system MTU of 9198 is configured on all devices
- All spines act as a PIM RP (Anycast with MSDP)
- Each leaf is connected to each spine with a single link
- The same consecutive range of interfaces is used on all leafs for fabric links
- The same consecutive range of interfaces is used on all spines for fabric links

## Examples

```hcl
module "iosxe_evpn_ospf_underlay" {
  source  = "netascode/evpn-ospf-underlay/iosxe"
  version = ">= 0.1.0"

  leafs           = ["LEAF-1", "LEAF-2"]
  spines          = ["SPINE-1", "SPINE-2"]
  loopback_id     = 0
  pim_loopback_id = 100

  loopbacks = [
    {
      device       = "SPINE-1",
      ipv4_address = "10.1.100.1"
    },
    {
      device       = "SPINE-2",
      ipv4_address = "10.1.100.2"
    },
    {
      device       = "LEAF-1",
      ipv4_address = "10.1.100.3"
    },
    {
      device       = "LEAF-2",
      ipv4_address = "10.1.100.4"
    }
  ]

  vtep_loopback_id = 1

  vtep_loopbacks = [
    {
      device       = "LEAF-1",
      ipv4_address = "10.1.200.1"
    },
    {
      device       = "LEAF-2",
      ipv4_address = "10.1.200.2"
    }
  ]

  fabric_interface_type         = "GigabitEthernet"
  leaf_fabric_interface_prefix  = "1/0/"
  leaf_fabric_interface_offset  = "1"
  spine_fabric_interface_prefix = "1/0/"
  spine_fabric_interface_offset = "1"
  anycast_rp_ipv4_address       = "10.1.101.1"
}
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.0 |
| <a name="requirement_iosxe"></a> [iosxe](#requirement\_iosxe) | >= 0.3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_iosxe"></a> [iosxe](#provider\_iosxe) | >= 0.3.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_leafs"></a> [leafs](#input\_leafs) | List of leaf device names. This list of devices must also be added to the provider configuration. | `set(string)` | `[]` | no |
| <a name="input_spines"></a> [spines](#input\_spines) | List of spine device names. This list of devices must also be added to the provider configuration. | `set(string)` | `[]` | no |
| <a name="input_loopback_id"></a> [loopback\_id](#input\_loopback\_id) | Loopback ID used for OSPF and PIM. | `number` | `0` | no |
| <a name="input_pim_loopback_id"></a> [pim\_loopback\_id](#input\_pim\_loopback\_id) | Loopback ID used for PIM Anycast RP. | `number` | `100` | no |
| <a name="input_loopbacks"></a> [loopbacks](#input\_loopbacks) | List of loopback interfaces, one per device. | <pre>list(object({<br>    device       = string<br>    ipv4_address = string<br>  }))</pre> | `[]` | no |
| <a name="input_vtep_loopback_id"></a> [vtep\_loopback\_id](#input\_vtep\_loopback\_id) | Loopback ID used for VTEP loopbacks. | `number` | `1` | no |
| <a name="input_vtep_loopbacks"></a> [vtep\_loopbacks](#input\_vtep\_loopbacks) | List of vtep loopback interfaces, one per leaf. | <pre>list(object({<br>    device       = string<br>    ipv4_address = string<br>  }))</pre> | `[]` | no |
| <a name="input_fabric_interface_type"></a> [fabric\_interface\_type](#input\_fabric\_interface\_type) | Interface type of fabric interfaces. Choices: `GigabitEthernet`, `TwoGigabitEthernet`, `FiveGigabitEthernet`, `TenGigabitEthernet`, `TwentyFiveGigE`, `FortyGigabitEthernet`, `HundredGigE`, `TwoHundredGigE`, `FourHundredGigE`. | `string` | `"GigabitEthernet"` | no |
| <a name="input_leaf_fabric_interface_prefix"></a> [leaf\_fabric\_interface\_prefix](#input\_leaf\_fabric\_interface\_prefix) | Interface prefix for leaf interfaces, eg. `1/0/`. | `string` | n/a | yes |
| <a name="input_spine_fabric_interface_prefix"></a> [spine\_fabric\_interface\_prefix](#input\_spine\_fabric\_interface\_prefix) | Interface prefix for spine interfaces, eg. `1/0/`. | `string` | n/a | yes |
| <a name="input_leaf_fabric_interface_offset"></a> [leaf\_fabric\_interface\_offset](#input\_leaf\_fabric\_interface\_offset) | Leaf interface index offset for fabric interfaces. | `string` | `1` | no |
| <a name="input_spine_fabric_interface_offset"></a> [spine\_fabric\_interface\_offset](#input\_spine\_fabric\_interface\_offset) | Spine interface index offset for fabric interfaces. | `string` | `1` | no |
| <a name="input_anycast_rp_ipv4_address"></a> [anycast\_rp\_ipv4\_address](#input\_anycast\_rp\_ipv4\_address) | IPv4 address of PIM RP loopback interface (Anycast). | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_loopback_id"></a> [loopback\_id](#output\_loopback\_id) | Loopback ID used for OSPF and PIM. |
| <a name="output_pim_loopback_id"></a> [pim\_loopback\_id](#output\_pim\_loopback\_id) | Loopback ID used for PIM Anycast RP. |
| <a name="output_vtep_loopback_id"></a> [vtep\_loopback\_id](#output\_vtep\_loopback\_id) | Loopback ID used for VTEP loopbacks. |
| <a name="output_loopbacks"></a> [loopbacks](#output\_loopbacks) | List of loopback interfaces, one per device. |
| <a name="output_vtep_loopbacks"></a> [vtep\_loopbacks](#output\_vtep\_loopbacks) | List of vtep loopback interfaces, one per leaf. |

## Resources

| Name | Type |
|------|------|
| [iosxe_interface_ethernet.leaf_fabric_interface](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ethernet) | resource |
| [iosxe_interface_ethernet.spine_fabric_interface](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ethernet) | resource |
| [iosxe_interface_loopback.loopback](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_loopback) | resource |
| [iosxe_interface_loopback.pim_loopback](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_loopback) | resource |
| [iosxe_interface_loopback.vtep_loopback](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_loopback) | resource |
| [iosxe_interface_ospf.leaf_interface_ospf](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf) | resource |
| [iosxe_interface_ospf.spine_interface_ospf](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf) | resource |
| [iosxe_interface_ospf_process.leaf_interface_ospf_process](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf_process) | resource |
| [iosxe_interface_ospf_process.loopback_interface_ospf_process](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf_process) | resource |
| [iosxe_interface_ospf_process.pim_loopback_interface_ospf_process](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf_process) | resource |
| [iosxe_interface_ospf_process.spine_interface_ospf_process](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf_process) | resource |
| [iosxe_interface_ospf_process.vtep_loopback_interface_ospf_process](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_ospf_process) | resource |
| [iosxe_interface_pim.leaf_interface_pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_pim) | resource |
| [iosxe_interface_pim.loopback_interface_pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_pim) | resource |
| [iosxe_interface_pim.pim_loopback_interface_pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_pim) | resource |
| [iosxe_interface_pim.spine_interface_pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_pim) | resource |
| [iosxe_interface_pim.vtep_loopback_interface_pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/interface_pim) | resource |
| [iosxe_msdp.msdp](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/msdp) | resource |
| [iosxe_ospf.ospf](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/ospf) | resource |
| [iosxe_pim.pim](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/pim) | resource |
| [iosxe_system.system](https://registry.terraform.io/providers/CiscoDevNet/iosxe/latest/docs/resources/system) | resource |
<!-- END_TF_DOCS -->