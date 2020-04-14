import boto3
import os

waf = boto3.client("wafv2")
rds = boto3.client("rds")
ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    # Remove IP from WAF IPSet
    ips = event["ips"]
    print(f"WAF IPs to unban: {ips}")

    blacklist = waf.get_ip_set(
        Name=os.environ["waf_name"],
        Scope=os.environ["waf_scope"],
        Id=os.environ["waf_id"],
    )
    updated = set(blacklist["IPSet"]["Addresses"]).difference(set(ips))

    try:
        waf.update_ip_set(
            Name=blacklist["IPSet"]["Name"],
            Scope=os.environ["waf_scope"],
            Id=blacklist["IPSet"]["Id"],
            Addresses=list(updated),
            LockToken=blacklist["LockToken"],
        )
        print("Successfully unbanned IPs from WAF")
    except Exception as e:
        print(f"Failed to unban IPs from WAF\t{e}")

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
                print(f"Failed to delete rule {rule_number} in Network ACL {nacl_id}.\t{e}")
