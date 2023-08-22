terraform {
  required_providers {
    iosxe = {
      source = "CiscoDevNet/iosxe"
      version = "0.3.3"
    }
  }
}

provider "iosxe" {
  username = "developer"
  password = "C1sco12345"
  url      = "https://198.18.1.21"
}

data "iosxe_system" "settings" {
}


resource "iosxe_vlan" "vlan51" {
  vlan_id  = 51
  name     = "Vlan51 modified"
  shutdown = false
}

resource "iosxe_vlan" "vlan52" {
  vlan_id  = 52
  name     = "Vlan52"
  shutdown = false
}