output "loopback_id" {
  description = "Loopback ID used for OSPF and PIM."
  value       = length([for lo in iosxe_interface_loopback.loopback : lo.name]) > 0 ? [for lo in iosxe_interface_loopback.loopback : lo.name][0] : null
}

output "pim_loopback_id" {
  description = "Loopback ID used for PIM Anycast RP."
  value       = length([for lo in iosxe_interface_loopback.pim_loopback : lo.name]) > 0 ? [for lo in iosxe_interface_loopback.pim_loopback : lo.name][0] : null
}

output "vtep_loopback_id" {
  description = "Loopback ID used for VTEP loopbacks."
  value       = length([for lo in iosxe_interface_loopback.vtep_loopback : lo.name]) > 0 ? [for lo in iosxe_interface_loopback.vtep_loopback : lo.name][0] : null
}

output "loopbacks" {
  description = "List of loopback interfaces, one per device."
  value = [for lo in iosxe_interface_loopback.loopback : {
    device       = lo.device
    ipv4_address = lo.ipv4_address
  }]
}

output "vtep_loopbacks" {
  description = "List of vtep loopback interfaces, one per leaf."
  value = [for lo in iosxe_interface_loopback.vtep_loopback : {
    device       = lo.device
    ipv4_address = lo.ipv4_address
  }]
}
