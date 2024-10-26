import boto3

def get_client():

    s3_client = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="datalake",
        aws_secret_access_key="datalake",
    )

    return s3_client