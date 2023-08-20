locals {
  all                     = setunion(var.leafs, var.spines)
  leaf_interface_indexes  = { for ls in setproduct(var.leafs, range(length(var.spines))) : "${ls[0]}/${ls[1]}" => ls }
  spine_interface_indexes = { for sl in setproduct(var.spines, range(length(var.leafs))) : "${sl[0]}/${sl[1]}" => sl }
}

resource "iosxe_system" "system" {
  for_each = local.all

  device                   = each.value
  #hostname                 = each.value
  ip_routing               = true
  ipv6_unicast_routing     = true
  multicast_routing_switch = true
  #mtu                      = 9198
}

resource "iosxe_interface_loopback" "loopback" {
  for_each = local.all

  device            = each.value
  name              = var.loopback_id
  ipv4_address      = [for l in var.loopbacks : l.ipv4_address if l.device == each.value][0]
  ipv4_address_mask = "255.255.255.255"

  depends_on = [iosxe_system.system]
}

resource "iosxe_interface_loopback" "pim_loopback" {
  for_each = var.spines

  device            = each.value
  name              = var.pim_loopback_id
  description       = "Anycast RP"
  ipv4_address      = var.anycast_rp_ipv4_address
  ipv4_address_mask = "255.255.255.255"

  depends_on = [iosxe_system.system]
}

resource "iosxe_interface_loopback" "vtep_loopback" {
  for_each = var.leafs

  device            = each.value
  name              = var.vtep_loopback_id
  ipv4_address      = [for l in var.vtep_loopbacks : l.ipv4_address if l.device == each.value][0]
  ipv4_address_mask = "255.255.255.255"

  depends_on = [iosxe_system.system]
}

resource "iosxe_interface_ethernet" "leaf_fabric_interface" {
  for_each = local.leaf_interface_indexes

  device     = each.value[0]
  type       = var.fabric_interface_type
  name       = "${var.leaf_fabric_interface_prefix}${var.leaf_fabric_interface_offset + each.value[1]}"
  shutdown   = false
  switchport = false
  unnumbered = "Loopback${var.loopback_id}"

  depends_on = [iosxe_interface_loopback.loopback]
}

resource "iosxe_interface_ethernet" "spine_fabric_interface" {
  for_each = local.spine_interface_indexes

  device     = each.value[0]
  type       = var.fabric_interface_type
  name       = "${var.spine_fabric_interface_prefix}${var.spine_fabric_interface_offset + each.value[1]}"
  shutdown   = false
  switchport = false
  unnumbered = "Loopback${var.loopback_id}"

  depends_on = [iosxe_interface_loopback.loopback]
}

resource "iosxe_ospf" "ospf" {
  for_each = local.all

  device     = each.value
  process_id = 1
  router_id  = [for l in var.loopbacks : l.ipv4_address if l.device == each.value][0]

  depends_on = [iosxe_system.system]
}

resource "iosxe_interface_ospf" "leaf_interface_ospf" {
  for_each = local.leaf_interface_indexes

  device                      = each.value[0]
  type                        = var.fabric_interface_type
  name                        = iosxe_interface_ethernet.leaf_fabric_interface[each.key].name
  network_type_point_to_point = true
}

resource "iosxe_interface_ospf" "spine_interface_ospf" {
  for_each = local.spine_interface_indexes

  device                      = each.value[0]
  type                        = var.fabric_interface_type
  name                        = iosxe_interface_ethernet.spine_fabric_interface[each.key].name
  network_type_point_to_point = true
}

resource "iosxe_interface_ospf_process" "leaf_interface_ospf_process" {
  for_each = local.leaf_interface_indexes

  device     = each.value[0]
  type       = var.fabric_interface_type
  name       = iosxe_interface_ospf.leaf_interface_ospf[each.key].name
  process_id = iosxe_ospf.ospf[each.value[0]].process_id
  area = [{
    area_id = "0"
  }]
}

resource "iosxe_interface_ospf_process" "spine_interface_ospf_process" {
  for_each = local.spine_interface_indexes

  device     = each.value[0]
  type       = var.fabric_interface_type
  name       = iosxe_interface_ospf.spine_interface_ospf[each.key].name
  process_id = iosxe_ospf.ospf[each.value[0]].process_id
  area = [{
    area_id = "0"
  }]
}

resource "iosxe_interface_ospf_process" "loopback_interface_ospf_process" {
  for_each = local.all

  device     = each.value
  type       = "Loopback"
  name       = iosxe_interface_loopback.loopback[each.value].name
  process_id = iosxe_ospf.ospf[each.value].process_id
  area = [{
    area_id = "0"
  }]
}

resource "iosxe_interface_ospf_process" "pim_loopback_interface_ospf_process" {
  for_each = var.spines

  device     = each.value
  type       = "Loopback"
  name       = iosxe_interface_loopback.pim_loopback[each.value].name
  process_id = iosxe_ospf.ospf[each.value].process_id
  area = [{
    area_id = "0"
  }]
}

resource "iosxe_interface_ospf_process" "vtep_loopback_interface_ospf_process" {
  for_each = var.leafs

  device     = each.value
  type       = "Loopback"
  name       = iosxe_interface_loopback.vtep_loopback[each.value].name
  process_id = iosxe_ospf.ospf[each.value].process_id
  area = [{
    area_id = "0"
  }]
}

resource "iosxe_interface_pim" "leaf_interface_pim" {
  for_each = local.leaf_interface_indexes

  device      = each.value[0]
  type        = var.fabric_interface_type
  name        = iosxe_interface_ethernet.leaf_fabric_interface[each.key].name
  sparse_mode = true
}

resource "iosxe_interface_pim" "spine_interface_pim" {
  for_each = local.spine_interface_indexes

  device      = each.value[0]
  type        = var.fabric_interface_type
  name        = iosxe_interface_ethernet.spine_fabric_interface[each.key].name
  sparse_mode = true
}

resource "iosxe_interface_pim" "loopback_interface_pim" {
  for_each = local.all

  device      = each.value
  type        = "Loopback"
  name        = iosxe_interface_loopback.loopback[each.value].name
  sparse_mode = true
}

resource "iosxe_interface_pim" "pim_loopback_interface_pim" {
  for_each = var.spines

  device      = each.value
  type        = "Loopback"
  name        = iosxe_interface_loopback.pim_loopback[each.value].name
  sparse_mode = true
}

resource "iosxe_interface_pim" "vtep_loopback_interface_pim" {
  for_each = var.leafs

  device      = each.value
  type        = "Loopback"
  name        = iosxe_interface_loopback.vtep_loopback[each.value].name
  sparse_mode = true
}

resource "iosxe_pim" "pim" {
  for_each = local.all

  device      = each.value
  ssm_default = true
  rp_address  = var.anycast_rp_ipv4_address

  depends_on = [iosxe_system.system]
}

resource "iosxe_msdp" "msdp" {
  for_each = var.spines

  device        = each.value
  originator_id = "Loopback${var.loopback_id}"

  peers = [for spine in var.spines : {
    addr                    = [for l in var.loopbacks : l.ipv4_address if l.device == spine][0]
    connect_source_loopback = var.loopback_id
  } if spine != each.value]

  depends_on = [iosxe_interface_loopback.loopback]
}
