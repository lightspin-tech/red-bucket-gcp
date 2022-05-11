#Use case 3: This terraform creates a bucket with uniform access control, public access permissions, and prevent public access enabled.
#Usage: 1. run the command terraform apply, leaving the comment on the line 8 as is.
#       2. remove the # from line 8, and run terraform apply one more time.

resource "google_storage_bucket" "bucket3" {
  provider                    = google-beta
  name                        = "gcp-red-bucket-3"
  location                    = "US-EAST1"
  #public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
}


resource "google_storage_bucket_iam_member" "member3" {
  bucket = google_storage_bucket.bucket3.name
  role = "roles/storage.objectViewer"
  member = "allUsers"
}

