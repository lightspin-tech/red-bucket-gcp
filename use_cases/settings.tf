variable "project-id" {
  type = string
}

provider "google" {
  project = var.project-id
}

provider "google-beta" {
  project = var.project-id
}