import boto3

rds = boto3.client("rds")
ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    # Remove IP from NACL rule
    network_acls = event["network_acls"]
    print(f"NACLs to unban: {network_acls}")

    for network_acl in network_acls:
        nacl_id = network_acl["id"]
        for rule_number in network_acl["rule_numbers"]:
            try:
                ec2.delete_network_acl_entry(
                    Egress=False, NetworkAclId=nacl_id, RuleNumber=rule_number
                )
                print(
                    f"Successfully deleted rule {rule_number} in Network ACL {nacl_id}"
                )
            except Exception as e:
                print(
                    f"Failed to delete rule {rule_number} in Network ACL {nacl_id}.\t{e}"
                )
