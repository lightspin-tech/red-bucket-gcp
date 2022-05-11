#Use case 1: This terraform creates a bucket with uniform access control, and no public access permissions.

resource "google_storage_bucket" "bucket1" {
  name                        = "gcp-red-bucket-1"
  location                    = "US-EAST1"
  uniform_bucket_level_access = true
}