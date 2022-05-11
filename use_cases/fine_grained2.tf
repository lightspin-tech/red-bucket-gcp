#Use case 6: This terraform creates a bucket with fine-grained access control,
#            public access permissions at the bucket level and at the object level, and prevent public access enabled.
#Usage: 1. run the command terraform apply, leaving the comment on the line 10 as is.
#       2. remove the # from line 10, and run terraform apply one more time.

resource "google_storage_bucket" "bucket6" {
  provider = google-beta
  name                        = "gcp-red-bucket-6"
  location                    = "US-EAST1"
  #public_access_prevention    = "enforced"
}


resource "google_storage_bucket_object" "file6" {
  name   = "example.txt"
  bucket = google_storage_bucket.bucket6.name
  source = "example.txt"
}


resource "google_project_iam_custom_role" "bucket6-custom-role" {
  role_id     = "CustomRole6"
  title       = "Custom Role 6"
  permissions = ["storage.buckets.get"]
}


resource "google_storage_bucket_iam_member" "member6" {
  bucket = google_storage_bucket.bucket6.name
  role = google_project_iam_custom_role.custom-role.name
  member = "allUsers"
}

resource "google_storage_object_acl" "file-acl6" {
  bucket = google_storage_bucket.bucket6.name
  object = google_storage_bucket_object.file6.output_name

  role_entity = [
    "READER:allUsers",
  ]
}