import json
from google.cloud import storage
from googleapiclient import discovery
import google.oauth2.credentials
import re
import csv
import argparse
import os


def get_project_buckets(client):
    buckets = client.list_buckets()
    return buckets


def get_bucket_configuration(bucket):
    """
    This function receives a bucket object and creates a dictionary of its access control and prevent public access settings.
    :param bucket: object
    :return: dict
    """
    bucket_configuration = bucket.iam_configuration
    prevent_public_access = False
    if bucket_configuration["publicAccessPrevention"] == "enforced":
        prevent_public_access = True

    uniform_access_control = bucket_configuration["uniformBucketLevelAccess"]["enabled"]
    return {"prevent_public_access": prevent_public_access, "uniform_access_control": uniform_access_control}


def get_objects_amount(bucket):
    """
    This function recieves a bucket object and returns the amount of objects it contains.
    :param bucket: object
    :return: int
    """
    objects = []
    for obj in bucket.list_blobs():
        if not obj.name.endswith("/"):
            objects.append(obj)
    return len(objects)


def get_bucket_status_info(bucket):
    """
    This function recieves a bucket object and calles the get_uniform_status_info/get_fine_grained_status_info functions based on the bucket configuration.
    It returns the output of the called function.
    :param bucket: object
    :return: dict
    """
    bucket_configuration = get_bucket_configuration(bucket)
    if bucket_configuration["uniform_access_control"]:
        bucket_status = get_uniform_status_info(bucket, bucket_configuration["prevent_public_access"])
    else:
        bucket_status = get_fine_grained_status_info(bucket, bucket_configuration["prevent_public_access"])

    return bucket_status


def get_uniform_status_info(bucket, prevent_public_access=False):
    """
    This function recieves a bucket object and a boolean value that represents whether the prevent public access abillity is enabled on this bucket.
    It evaluates the gcp status, our status, the access scope, and the public objects, and returns a dictionary with all the specified information.
    :param bucket: object
    :param prevent_public_access: bool/None
    :return: dict
    """
    status_doc = {
        "access_control_type": "uniform",
        "gcp_status": "Not public",
        "lightspin_status": "Not public",
        "access_scope": [],
        "public_objects": "No public objects"
    }
    if prevent_public_access:
        return status_doc

    public_access_info = get_public_access_info(bucket, "bucket")
    if public_access_info["public_permissions"]:
        status_doc["gcp_status"] = "Public to the internet"

    if public_access_info["is_public"]:
        status_doc["lightspin_status"] = "Public"
        status_doc["access_scope"] = public_access_info["access_scope"]
        bucket_level_object_permissions = [action for action in public_access_info["access_scope"] if
                                           action.find("storage.objects.") != -1]
        if bucket_level_object_permissions:
            status_doc["public_objects"] = "All objects are public"

    return status_doc


def get_fine_grained_status_info(bucket, prevent_public_access=False):
    """
    This function recieves a bucket object and a boolean value that represents whether the prevent public access abillity is enabled on this bucket.
    It evaluates the gcp status, our status, the access scope, and the public objects, and returns a dictionary with all the specified information.
    :param bucket: object
    :param prevent_public_access: bool/None
    :return: dict
    """
    status_doc = {
        "access_control_type": "fine-grained",
        "gcp_status": "Subject to objects ACLs",
        "lightspin_status": "Not public",
        "access_scope": [],
        "public_objects": "No public objects"
    }

    if prevent_public_access:
        status_doc["gcp_status"] = "Not public"
        return status_doc
    else:
        public_access_info = get_public_access_info(bucket, "bucket")
        if public_access_info["public_permissions"]:
            status_doc["gcp_status"] = "Public to the internet"

        if public_access_info["is_public"]:
            status_doc["lightspin_status"] = "Public"
            status_doc["access_scope"] = public_access_info["access_scope"]
            bucket_level_object_permissions = [action for action in public_access_info["access_scope"] if
                                               action.find("storage.objects.") != -1]
            if bucket_level_object_permissions:
                status_doc["public_objects"] = "All objects are public"

    public_objects = get_public_objects(bucket)
    if public_objects:
        status_doc["lightspin_status"] = "Public"
        status_doc["public_objects"] = public_objects

    return status_doc


def get_public_access_info(storage_asset, asset_type):
    """
    This function gets an object/bucket object, and analyze its iam permissions to check for public permissions.
    :param storage_asset: object
    :param asset_type: str
    :return: dict
    """
    public_roles = check_iam(storage_asset)
    public_permissions = []
    public_storage_permissions = []
    for role in public_roles:
        role_permissions = get_role_permissions(role)
        public_permissions += role_permissions
        role_storage_permissions = get_storage_permissions(role_permissions)
        relevant_level_permissions = get_relevant_level_permissions(role_storage_permissions, asset_type)
        public_storage_permissions += relevant_level_permissions

    if public_storage_permissions:
        return {"is_public": True, "access_scope": list(set(public_storage_permissions)),
                "public_permissions": list(set(public_permissions))}

    return {"is_public": False, "access_scope": [], "public_permissions": list(set(public_permissions))}


def get_public_objects(bucket):
    """
    This function recieves a bucket object and returns the public objects it contains.
    :param bucket: object
    :return: list
    """
    public_objects = []
    bucket_objects = bucket.list_blobs()
    for obj in bucket_objects:
        public_access_info = get_public_access_info(obj, "object")
        if public_access_info["is_public"]:
            public_objects.append(obj.name)
    return public_objects


def check_iam(bucket):
    """
    This function recieves a bucket object and returns the roles that are assigned to allUsers/allAuthenticatedUsers groups.
    :param bucket: object
    :return: list
    """
    public_roles = []
    policy = bucket.get_iam_policy()
    for pb in policy.bindings:
        if "allUsers" in pb['members'] or "allAuthenticatedUsers" in pb['members']:
            public_roles.append(pb["role"])

    return public_roles


def is_custom_role(role):
    """
    This function recieves a role name and returns if it is a custom role or not.
    :param role: str
    :return: bool
    """
    custom_role_regex = "^projects/[^/]+/roles/[^/]+$"
    pattern = re.compile(custom_role_regex)
    if pattern.match(role):
        return True

    return False


def get_role_permissions(role):
    """
    This function returns the included permissions of a role given role.
    :param role: str
    :return: list
    """
    if is_custom_role(role):
        request = service.projects().roles().get(name=role)
    else:
        request = service.roles().get(name=role)

    response = request.execute()
    return response["includedPermissions"]


def get_storage_permissions(role_permissions):
    """
    This function recieves a list of permissions and returns only storage permissions.
    :param role_permissions: list
    :return: list
    """
    storage_permissions = []
    pattern = re.compile("^storage\..*$")
    for perm in role_permissions:
        if pattern.match(perm):
            storage_permissions.append(perm)

    return storage_permissions


def get_relevant_level_permissions(storage_permissions, level):
    """
    This function recieves a list of storage permission and checks which of them are relevant when given at a certin level.
    For instance, the storage.buckets.create will be irrelevant when given at the object level.
    :param storage_permissions: list
    :param level: str
    :return: list
    """
    relevant_permissions = []
    if level == "project":
        relevant_permissions = storage_permissions
    elif level == "bucket":
        for sp in storage_permissions:
            if sp.find(".hmacKeys.") == -1 and sp not in ["storage.buckets.create", "storage.buckets.list"]:
                relevant_permissions.append(sp)
    else:
        for sp in storage_permissions:
            if sp.find(".objects.") != -1 and sp not in ["storage.objects.create", "storage.objects.list"]:
                relevant_permissions.append(sp)

    return relevant_permissions


def to_csv(buckets_list):
    """
    This function writes all the bucket information to a csv file.
    :param buckets_list: list
    :return: None
    """
    csv_path = os.path.join(args.output_path, "results.csv")
    with open(csv_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["bucket", "objects amount", "access control type", "gcp status", "lightspin status", "access scope",
             "public objects"])
        for bucket in buckets_list:
            w = csv.DictWriter(file, bucket.keys())
            w.writerow(bucket)


def to_json(buckets_list):
    """
    This function writes all the bucket information to a json file.
    :param buckets_list: list
    :return: None
    """
    csv_path = os.path.join(args.output_path, "results.json")
    with open(csv_path, 'w') as outfile:
        json.dump(buckets_list, outfile)


def main():
    project_buckets = get_project_buckets(storage_client)
    buckets_list = []
    for bucket in project_buckets:
        try:
            bucket_full_info = {"name": bucket.name}
            bucket_objects_amount = get_objects_amount(bucket)
            status_info = get_bucket_status_info(bucket)
            bucket_full_info["object_count"] = bucket_objects_amount
            bucket_full_info.update(status_info)
            buckets_list.append(bucket_full_info)
        except Exception as e:
            print("could not get bucket information" + str(e))
    if args.output_type == "CSV":
        to_csv(buckets_list)
    else:
        to_json(buckets_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', help='Enter your GCP project id', required=True)
    parser.add_argument('--access_token', help='Enter your GCP access token', required=True)
    parser.add_argument('--output_path', help='Path to save the results', default="")
    parser.add_argument('--output_type', choices=["JSON", "CSV"], default="JSON",
                        help='Choose output option between "CSV" and "JSON"')

    args = parser.parse_args()
    try:
        credentials = google.oauth2.credentials.Credentials(args.access_token)
        storage_client = storage.Client(project=args.project_id, credentials=credentials)
        service = discovery.build('iam', 'v1', credentials=credentials)
        main()
    except Exception as e:
        print(f"Invalid credentials: {e}")
