# Use Cases

### Description
Use these terraform files in this folder to test our tool.
In the beginning of each file, you can find a short description of the case.

| File          | Use Case                                                                                                                        | Expected Result                                                                                          |
|---------------|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| uniform1      | uniform + prevent public access disabled + no public access permissions at the bucket level                                     | <ul><li>GCP's evaluations - Not public</li><li>Lightspin's evaluations - Not public</li></ul>            |
| uniform2      | uniform + prevent public access disabled + public access permissions at the bucket level                                        | <ul><li>GCP's evaluations - Public</li><li>Lightspin's evaluations - Public</li></ul>                    |
| uniform3      | uniform + prevent public access enabled + public access permissions at the bucket level                                         | <ul><li>GCP's evaluations - Not public</li><li>Lightspin's evaluations - Not public</li></ul>            |
| uniform4      | uniform + prevent public access disabled + public permissions that does not apply to storage resources (compute.instances.list) | <ul><li>GCP's evaluations - Public</li><li>Lightspin's evaluations - Not public</li></ul>                |
| fine_grained1 | fine-grained + prevent public access disabled + public access permissions at the bucket and object levels                       | <ul><li>GCP's evaluations - Public</li><li>Lightspin's evaluations - Public</li></ul>                    |
| fine_grained2 | fine-grained + prevent public access enabled + public access permissions at the bucket and object level                         | <ul><li>GCP's evaluations - Not Public</li><li>Lightspin's evaluations - Not Public</li></ul>            |
| fine_grained3 | fine-grained + prevent public access disabled +  two objects, only one with public access permissions                           | <ul><li>GCP's evaluations - Subject to object ACLs	</li><li>Lightspin's evaluations - Public</li></ul>   |

### Usage
edit the setting.tf file and put your project id.

```bash
cd use_cases
terraform init
terraform apply -var="project-id={PROJECT-ID}"
```

remove the comments from the following files:
1. uniform3 - line 8
2. fine_grained2 - line 10

This will enable the "prevent public access" ability for use cases 3 and 6

To apply the changes:
```bash
terraform apply -var="project-id={PROJECT-ID}"
```

to delete all use cases from the GCP project run:
```bash
cd use_cases
terraform destroy -var="project-id={PROJECT-ID}"
```

