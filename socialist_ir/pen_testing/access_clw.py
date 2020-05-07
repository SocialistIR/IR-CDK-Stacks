from socialist_ir.cdk_menu import CdkMenu

import boto3
import botocore.exceptions as be
import time


class AccessClw(CdkMenu):
    def __init__(
            self,
            name: str = "access_clw",
            required_variables: list = [],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def execute(self) -> bool:
        #creating cloudwatch log group. The unauthorized user should be revoked access.
        clw = boto3.client('logs')

        for i in range(3):
            try:
                response = clw.create_log_group(
                    logGroupName='/testingclw/test'
                )

                #print('EventId of some activity: ' + str(response['Events'][0]['EventId']))
                time.sleep(20)
            except be.ClientError:
                print('Client doesnt have permission to access Cloudwatch. Check IAM policies.')
                return False
                break
            except Exception as ex:
                print(ex)
                return False
                break

        return True
