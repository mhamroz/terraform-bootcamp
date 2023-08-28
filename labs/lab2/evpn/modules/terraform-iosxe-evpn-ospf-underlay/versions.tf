terraform {
  required_version = ">= 1.1.0"

  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "= 0.3.3"
    }
  }
}
