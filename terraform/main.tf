resource "huaweicloud_vpc" "main" {
  name = "module6-vpc"
  cidr = "10.20.0.0/16"
}

resource "huaweicloud_vpc_subnet" "public" {
  name       = "module6-public-subnet"
  cidr       = "10.20.1.0/24"
  gateway_ip = "10.20.1.1"
  vpc_id     = huaweicloud_vpc.main.id

  dns_list = ["100.125.1.250", "100.125.21.250"]
}

resource "huaweicloud_networking_secgroup_v2" "web" {
  name        = "module6-web-sg"
  description = "Allow SSH from admin IP and HTTP from internet"
}

resource "huaweicloud_networking_secgroup_rule_v2" "ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  ports             = "22"
  remote_ip_prefix  = var.ssh_allowed_cidr
  security_group_id = huaweicloud_networking_secgroup_v2.web.id
  description       = "SSH from administrator only"
}

resource "huaweicloud_networking_secgroup_rule_v2" "http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  ports             = "80"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.web.id
  description       = "Public HTTP"
}

resource "huaweicloud_vpc_eip" "web" {
  name = "module6-web-eip"

  publicip {
    type = "5_bgp"
  }

  bandwidth {
    name        = "module6-web-bandwidth"
    share_type  = "PER"
    size        = 1
    charge_mode = "traffic"
  }
}

resource "huaweicloud_compute_instance" "web" {
  name              = var.instance_name
  flavor_id         = var.flavor_id
  image_name        = var.image_name
  availability_zone = var.availability_zone
  key_pair          = var.key_pair

  system_disk_type = "SAS"
  system_disk_size = var.system_disk_size

  security_group_ids = [
    huaweicloud_networking_secgroup_v2.web.id
  ]

  network {
    uuid = huaweicloud_vpc_subnet.public.id
  }

  eip_id = huaweicloud_vpc_eip.web.id

  delete_disks_on_termination = true
  delete_eip_on_termination   = true

  user_data = <<-USERDATA
    #!/bin/bash
    set -eux
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y nginx
    systemctl enable --now nginx
    cat > /var/www/html/index.html <<'HTML'
    <!doctype html>
    <html>
      <head><title>LedgerSvc Module 6</title></head>
      <body>
        <h1>LedgerSvc - Huawei Cloud ECS</h1>
        <p>Nginx is running successfully.</p>
      </body>
    </html>
    HTML
  USERDATA

  depends_on = [
    huaweicloud_networking_secgroup_rule_v2.ssh,
    huaweicloud_networking_secgroup_rule_v2.http
  ]
}
