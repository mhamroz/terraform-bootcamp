output "created_loopback_interfaces" {
  description = "List of created loopback interface resource ids"
  value       = [for intf in iosxe_interface_loopback.loopback_interface : intf.id]
}