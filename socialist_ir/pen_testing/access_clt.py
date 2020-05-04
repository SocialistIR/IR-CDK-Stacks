from socialist_ir.cdk_menu import CdkMenu

import boto3
import botocore.exceptions as be
import time


class AccessClt(CdkMenu):
    def __init__(
            self,
            name: str = "access_clt",
            required_variables: list = [],
    ):
        super().__init__(name=name, required_variables=required_variables)

    def execute(self) -> bool:
        clt = boto3.client('cloudtrail')

        while True:
            try:
                response = clt.lookup_events(
                    LookupAttributes=[
                        {
                            'AttributeKey': 'ReadOnly',
                            'AttributeValue': 'false'
                        },
                    ],
                    MaxResults=10,
                )
                print('EventId of some activity: ' + str(response['Events'][0]['EventId']))
                time.sleep(3)
            except be.ClientError:
                print('Client doesnt have permission to access Cloudtrail. Check IAM policies.')
                return False
                break
            except Exception as ex:
                print(ex)
                return False
                break

        return True
