#
# S3 functions
#

from botocore.exceptions import ClientError
import boto3
import settings
import os
import logFunctions

#
# Creates a AWS pre-signed URL to download (GET) a file from S3
#

def create_presigned_url_get(object_name, download_filename = '', expiration=3600): # Generate a presigned URL to share an S3 object

    if download_filename == '':
        download_filename = object_name

    bucket_name = os.environ.get('BucketName')
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name, 'ResponseContentDisposition': 'attachment; filename ="' + download_filename + '"'},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        logFunctions.log('create_presigned_url failed')
        logFunctions.log(e)
        return ''

#
# Creates a AWS pre-signed URL to upload (PUT) a file to S3
#

def create_presigned_url_put(object_name, expiration=3600): # Generate a presigned URL to upload an S3 object
    bucket_name = os.environ.get('BucketName')
    s3_con = boto3.client('s3')
    url=s3_con.generate_presigned_url('put_object',
        Params={'Bucket': bucket_name,
                'Key': object_name,
                'ContentType': settings.S3_content_type
        },
        ExpiresIn=expiration
    )
    return url

#
# Delete a file from S3
#

def delete(object_name):
    bucket_name = os.environ.get('BucketName')
    client = boto3.client('s3')
    o = client.delete_object(Bucket=bucket_name, Key=object_name)
    return str(o)
