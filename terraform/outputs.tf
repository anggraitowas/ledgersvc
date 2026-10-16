output "ecs_id" {
  description = "ID ECS yang dibuat"
  value       = huaweicloud_compute_instance.web.id
}

output "eip_address" {
  description = "IP publik ECS"
  value       = huaweicloud_vpc_eip.web.publicip[0].ip_address
}

output "web_url" {
  description = "URL halaman web ECS"
  value       = "http://${huaweicloud_vpc_eip.web.publicip[0].ip_address}"
}
