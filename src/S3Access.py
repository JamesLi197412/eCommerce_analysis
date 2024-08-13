from io import BytesIO

import boto3
import pandas as pd


class S3Reader:
    def __init__(self, access_key_id, secret_access_key, region_name):
        """
            access_key_id (str): Your AWS access key ID.
            secret_access_key (str): Your AWS secret access key.
            region_name (str): The AWS region where your S3 bucket resides.
        """

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name
        )

    def get_csv_file_keys(self, bucket_name):
        """
          Find all files end with csv in the bucket
        :param bucket_name: the bucket you wish to explroe
        :return: list of filename
        """
        csv_keys = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                if obj['Key'].endswith('.csv'):
                    csv_keys.append(obj['Key'])
        return csv_keys

    def process_csv_files(self, bucket_name):
        csv_keys = self.get_csv_file_keys(bucket_name)
        dict = {}

        for key in csv_keys:
            csv_obj = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            csv_content = csv_obj['Body']  # .read().decode('utf-8')
            df = pd.read_csv(BytesIO(csv_content.read()))

            dict[key] = df

        return csv_keys, dict
