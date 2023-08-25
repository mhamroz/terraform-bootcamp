variable "devices" {
  description = "List of device details"
  type = list(object({
    name = string
    url  = string
  }))
}

variable "credentials" {
  description = "Credentials"
  type = object({
    username = string
    password = string
  })
}

variable "loopback_interface_number" {
  description = "Loopback interface number"
  type        = number
}