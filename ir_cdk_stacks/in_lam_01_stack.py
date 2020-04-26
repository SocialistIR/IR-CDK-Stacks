from aws_cdk import (
    core,
    aws_events as cw_event,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_iam as iam,
)
import os
import logging
import datetime

logger = logging.getLogger(__name__)


class InLam01Stack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        SLACK_WEBHOOK_URL = self.node.try_get_context("webhook_url")

        if not SLACK_WEBHOOK_URL:
            logger.error(f"Required context variables for {id} were not provided!")
        else:
            # Create explicit deny iam
            deny_iam = iam.ManagedPolicy(self,
                f"InLam01DenyPolicy",
                managed_policy_name = "lambdaDeny",
                statements=[
                    iam.PolicyStatement(
                        effect = iam.Effect.DENY,
                        actions = [
                            "iam:UpdateAssumeRolePolicy",
                            "iam:DeactivateMFADevice",
                            "iam:CreateServiceSpecificCredential",
                            "iam:DeleteAccessKey",
                            "iam:ListRoleTags",
                            "iam:DeleteGroup",
                            "iam:UpdateOpenIDConnectProviderThumbprint",
                            "iam:RemoveRoleFromInstanceProfile",
                            "iam:UpdateGroup",
                            "iam:CreateRole",
                            "iam:AttachRolePolicy",
                            "iam:ListServiceSpecificCredentials",
                            "iam:PutRolePolicy",
                            "iam:ListSigningCertificates",
                            "iam:AddRoleToInstanceProfile",
                            "iam:CreateLoginProfile",
                            "iam:ListSSHPublicKeys",
                            "iam:DetachRolePolicy",
                            "iam:ListAttachedRolePolicies",
                            "iam:DeleteServerCertificate",
                            "iam:UploadSSHPublicKey",
                            "iam:DetachGroupPolicy",
                            "iam:ListRolePolicies",
                            "iam:DetachUserPolicy",
                            "iam:DeleteOpenIDConnectProvider",
                            "iam:ChangePassword",
                            "iam:PutGroupPolicy",
                            "iam:UpdateLoginProfile",
                            "iam:UpdateServiceSpecificCredential",
                            "iam:CreateGroup",
                            "iam:RemoveClientIDFromOpenIDConnectProvider",
                            "iam:UpdateUser",
                            "iam:ListEntitiesForPolicy",
                            "iam:DeleteUserPolicy",
                            "iam:AttachUserPolicy",
                            "iam:DeleteRole",
                            "iam:UpdateRoleDescription",
                            "iam:UpdateAccessKey",
                            "iam:UpdateSSHPublicKey",
                            "iam:UpdateServerCertificate",
                            "iam:DeleteSigningCertificate",
                            "iam:ListGroupsForUser",
                            "iam:DeleteServiceLinkedRole",
                            "iam:CreateInstanceProfile",
                            "iam:PutRolePermissionsBoundary",
                            "iam:ResetServiceSpecificCredential",
                            "iam:DeletePolicy",
                            "iam:DeleteSSHPublicKey",
                            "iam:CreateVirtualMFADevice",
                            "iam:CreateSAMLProvider",
                            "iam:ListMFADevices",
                            "iam:DeleteRolePermissionsBoundary",
                            "iam:CreateUser",
                            "iam:CreateAccessKey",
                            "iam:ListInstanceProfilesForRole",
                            "iam:PassRole",
                            "iam:AddUserToGroup",
                            "iam:RemoveUserFromGroup",
                            "iam:DeleteRolePolicy",
                            "iam:EnableMFADevice",
                            "iam:ResyncMFADevice",
                            "iam:ListAttachedUserPolicies",
                            "iam:ListAttachedGroupPolicies",
                            "iam:CreatePolicyVersion",
                            "iam:UpdateSAMLProvider",
                            "iam:DeleteLoginProfile",
                            "iam:ListAccessKeys",
                            "iam:DeleteInstanceProfile",
                            "iam:UploadSigningCertificate",
                            "iam:ListGroupPolicies",
                            "iam:PutUserPermissionsBoundary",
                            "iam:DeleteUser",
                            "iam:DeleteUserPermissionsBoundary",
                            "iam:ListUserPolicies",
                            "iam:ListInstanceProfiles",
                            "iam:CreateOpenIDConnectProvider",
                            "iam:UploadServerCertificate",
                            "iam:CreatePolicy",
                            "iam:CreateServiceLinkedRole",
                            "iam:ListPolicyVersions",
                            "iam:DeleteVirtualMFADevice",
                            "iam:AttachGroupPolicy",
                            "iam:PutUserPolicy",
                            "iam:UpdateRole",
                            "iam:UpdateSigningCertificate",
                            "iam:DeleteGroupPolicy",
                            "iam:AddClientIDToOpenIDConnectProvider",
                            "iam:DeleteServiceSpecificCredential",
                            "iam:GetLoginProfile",
                            "iam:DeletePolicyVersion",
                            "iam:SetDefaultPolicyVersion",
                            "iam:ListUserTags",
                            "iam:DeleteSAMLProvider"
                        ],
                        resources = [
                            "arn:aws:iam::*:saml-provider/*",
                            "arn:aws:iam::*:policy/*",
                            "arn:aws:iam::*:oidc-provider/*",
                            "arn:aws:iam::*:instance-profile/*",
                            "arn:aws:iam::*:user/*",
                            "arn:aws:iam::*:role/*",
                            "arn:aws:iam::*:server-certificate/*",
                            "arn:aws:iam::*:sms-mfa/*",
                            "arn:aws:iam::*:group/*",
                            "arn:aws:iam::*:mfa/*/*"
                        ]
                    ),
                    iam.PolicyStatement(
                        effect = iam.Effect.DENY,
                        actions = [
                            "iam:ListPolicies",
                            "iam:DeleteAccountPasswordPolicy",
                            "iam:ListSAMLProviders",
                            "lambda:ListFunctions",
                            "iam:ListServerCertificates",
                            "iam:ListPoliciesGrantingServiceAccess",
                            "iam:ListRoles",
                            "lambda:GetAccountSettings",
                            "lambda:CreateEventSourceMapping",
                            "iam:ListVirtualMFADevices",
                            "iam:SetSecurityTokenServicePreferences",
                            "iam:ListOpenIDConnectProviders",
                            "iam:UpdateAccountPasswordPolicy",
                            "iam:CreateAccountAlias",
                            "lambda:ListEventSourceMappings",
                            "iam:ListAccountAliases",
                            "iam:ListUsers",
                            "lambda:ListLayerVersions",
                            "lambda:ListLayers",
                            "iam:ListGroups",
                            "iam:DeleteAccountAlias",
                            "iam:GetAccountSummary"
                        ],
                        resources = [
                            "*"
                        ]
                    ),
                    iam.PolicyStatement(
                        effect = iam.Effect.DENY,
                        actions = [
                            "lambda:*"
                        ],
                        resources = [
                            "arn:aws:lambda:*:*:function:*",
                            "arn:aws:lambda:*:*:layer:*",
                            "arn:aws:lambda:*:*:event-source-mapping:*",
                            "arn:aws:lambda:*:*:function:*:*",
                        ]
                    ),
                ]
            )

            # Create lambda that attaches explicit deny
            lambda_dir_path = os.path.join(os.getcwd(), "ir_cdk_stacks", "in_lam_01")
            lockdown_lambda = _lambda.Function(
                self,
                "InLam01LockdownFunction",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="response_lambda.lambda_handler",
                code=_lambda.Code.from_asset(lambda_dir_path),
                environment={
                    "webhook_url": SLACK_WEBHOOK_URL,
                    "lambdaDenyIAM" : deny_iam.managed_policy_arn
                }
            )
            
            lockdown_lambda.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["iam:AttachUserPolicy",],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                )
            )

            # set up cloudwatch event for lambda invokes
            cw_hook = cw_event.Rule(self,
                f"InLam01Event",
                description = "Monitor Lambda Invokes",
                event_pattern=cw_event.EventPattern(
                    source=["aws.lambda"]
                ),
                rule_name = "lambdaMonitor",
                targets=[
                    targets.LambdaFunction(handler=lockdown_lambda)
                ]
            )

            

            
