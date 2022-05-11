#Use case 2: This terraform creates a bucket with uniform access control, and public access permissions.

resource "google_storage_bucket" "bucket2" {
  name                        = "gcp-red-bucket-2"
  location                    = "US-EAST1"
  uniform_bucket_level_access = true
}


resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.bucket2.name
  role = "roles/storage.objectViewer"
  member = "allUsers"
}