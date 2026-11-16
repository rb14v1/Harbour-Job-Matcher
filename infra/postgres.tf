terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

variable "resource_group_name" {
  type        = string
  description = "Resource group holding the PostgreSQL server."
}

variable "location" {
  type        = string
  description = "Primary region of the PostgreSQL server."
}

variable "administrator_login" {
  type        = string
  description = "PostgreSQL administrator login."
}

variable "administrator_password" {
  type        = string
  sensitive   = true
  description = "PostgreSQL administrator password."
}

# PITR is built into Flexible Server and covers the retention window.
# Geo-redundant backups are stored in the paired region, separate from the primary.
resource "azurerm_postgresql_flexible_server" "psql_job_matcher" {
  name                         = "psql-job-matcher"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = "16"
  sku_name                     = "GP_Standard_D2s_v3"
  storage_mb                   = 32768
  administrator_login          = var.administrator_login
  administrator_password       = var.administrator_password
  backup_retention_days        = 30
  geo_redundant_backup_enabled = true
}
