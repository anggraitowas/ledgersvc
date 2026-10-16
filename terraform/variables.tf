variable "region" {
  description = "Huawei Cloud region"
  type        = string
  default     = "ap-southeast-3"
}

variable "availability_zone" {
  description = "Availability Zone yang tersedia di region Jakarta"
  type        = string
}

variable "flavor_id" {
  description = "ID flavor ECS yang dipilih di konsol"
  type        = string
}

variable "image_name" {
  description = "ID image Ubuntu yang dipilih di konsol"
  type        = string
}

variable "key_pair" {
  description = "Nama key pair SSH yang sudah dibuat di Huawei Cloud"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "IP publik admin dengan suffix /32"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.ssh_allowed_cidr))
    error_message = "Masukkan CIDR yang valid, misalnya IP publik admin dengan suffix /32."
  }
}

variable "instance_name" {
  description = "Nama ECS"
  type        = string
  default     = "module6-nginx-ecs"
}

variable "system_disk_size" {
  description = "Ukuran disk sistem dalam GiB"
  type        = number
  default     = 20

  validation {
    condition     = var.system_disk_size >= 10
    error_message = "Ukuran disk minimal yang dikonfigurasi adalah 10 GiB; pastikan juga memenuhi batas minimum image."
  }
}
