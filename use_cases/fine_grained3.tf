#Use case 7: This terraform creates a bucket with fine-grained access control that contains two objects.
#            One with public access permissions, and the other without.

resource "google_storage_bucket" "bucket7" {
  name                        = "gcp-red-bucket-7"
  location                    = "US-EAST1"
}


resource "google_storage_bucket_object" "file7" {
  name   = "example.txt"
  bucket = google_storage_bucket.bucket7.name
  source = "example.txt"
}

resource "google_storage_bucket_object" "file7-2" {
  name   = "example2.txt"
  bucket = google_storage_bucket.bucket7.name
  source = "example.txt"
}

resource "google_storage_object_acl" "file-acl7" {
  bucket = google_storage_bucket.bucket7.name
  object = google_storage_bucket_object.file7.output_name

  role_entity = [
    "READER:allUsers",
  ]
}