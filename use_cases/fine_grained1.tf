#Use case 5: This terraform creates a bucket with fine-grained access control, and public access permissions at the bucket level and at the object level.

resource "google_storage_bucket" "bucket5" {
  name                        = "gcp-red-bucket-5"
  location                    = "US-EAST1"
}


resource "google_storage_bucket_object" "file5" {
  name   = "example.txt"
  bucket = google_storage_bucket.bucket5.name
  source = "example.txt"
}


resource "google_project_iam_custom_role" "bucket5-custom-role" {
  role_id     = "CustomRole5"
  title       = "Custom Role 5"
  permissions = ["storage.buckets.get"]
}


resource "google_storage_bucket_iam_member" "member5" {
  bucket = google_storage_bucket.bucket5.name
  role = google_project_iam_custom_role.custom-role.name
  member = "allUsers"
}

resource "google_storage_object_acl" "file-acl5" {
  bucket = google_storage_bucket.bucket5.name
  object = google_storage_bucket_object.file5.output_name

  role_entity = [
    "READER:allUsers",
  ]
}