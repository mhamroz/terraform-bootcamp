provider "iosxe" {
  username = var.credentials.username
  password = var.credentials.password
  devices  = var.devices
}

resource "iosxe_interface_loopback" "loopback_interface" {
  for_each = { for device in var.devices : device.name => split("-", device.name)[1] }

  name              = var.loopback_interface_number
  description       = "Created by Terraform"
  device            = each.key
  ipv4_address      = "192.168.${each.value}.${var.loopback_interface_number}"
  ipv4_address_mask = "255.255.255.255"
}