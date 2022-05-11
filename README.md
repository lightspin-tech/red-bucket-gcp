# GCP-Red-Bucket
## Lightspin's Google Cloud Storage Bucket Scanner


### Description
Scan your GCP Buckets for public access.

The tool analyzes the following:
- Bucket's prevent public access
- Bucket's access control type
- Bucket policy and ACL
- Object policy and ACL

You can use the use_cases folder, that contains terraform files of several interesting cases to test our tool.


### Our Research
[Link to the full security research blog]()


### Requirements
GCP-Red-Bucket is built with Python 3 and google clients.

The tool requires:
- Access token of a user/service account
- [Sufficient permissions on the project to run the scanner](required_permissions.txt) - you can create a custom role using [this guide](https://cloud.google.com/iam/docs/creating-custom-roles#creating_a_custom_role). 
- Python 3 and pip3 installed

### Installation
```bash
git clone https://github.com/lightspin-tech/red-bucket-gcp.git
cd red-bucket-gcp
pip3 install -r requirements.txt
```

### Usage
```bash
python3 main.py --project_id PROJECT_ID --access_token ACCESS_TOKEN [--output_path OUTPUT_PATH] [--output_type {JSON,CSV}]
```

**Note:** The output_path parameter should be the directory path you want the results file to be created in.
### Contact Us
This research was held by Lightspin's Security Research Team.
For more information, contact us at support@lightspin.io.

### License
