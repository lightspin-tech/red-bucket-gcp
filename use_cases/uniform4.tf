#Use case 4: This terraform creates a bucket with uniform access control, and public permissions that does not apply to storage resources (compute.instances.list).


resource "google_storage_bucket" "bucket4" {
  name                        = "gcp-red-bucket-4"
  location                    = "US-EAST1"
  uniform_bucket_level_access = true
}


resource "google_project_iam_custom_role" "custom-role" {
  role_id     = "CustomRole4"
  title       = "Custom Role 4"
  permissions = ["compute.instances.list"]
}

resource "google_storage_bucket_iam_member" "member4" {
  bucket = google_storage_bucket.bucket4.name
  role = google_project_iam_custom_role.custom-role.name
  member = "allUsers"
}