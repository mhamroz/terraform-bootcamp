terraform {
  required_version = ">= 1.5.0"

  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "0.3.3"
    }
  }
}