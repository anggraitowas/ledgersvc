terraform {
  required_version = ">= 1.15.0"

  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.60.0"
    }
  }
}

provider "huaweicloud" {
  region = var.region
}
