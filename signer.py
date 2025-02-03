import boto3
from botocore.client import Config

# Initialize an S3 session/client to talk to DigitalOcean Spaces.
session = boto3.session.Session()
client = session.client(
    "s3",
    # configure the region you created the space in.
    region_name="nyc3",
    # configure the region you created the space in.
    endpoint_url="https://nyc3.digitaloceanspaces.com",
    # configure your access key (generate this on the dashboard).
    aws_access_key_id="DO801PLEWTHUFYUEGJKB",
    # configure your secret key (generate this on the dashboard).
    aws_secret_access_key="IjahMgr37gpQ6CFeXNBSoY7Mt1MHQNBu74ltkmV+EUY"
)

signed_get_object_url = client.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': 'elicit',
        'Key': '3rr1sy21kml1r7y6hqsa5x68sgpx',
    },
    ExpiresIn=30
)

# print the pre-signed GET request URL for downloading the object.
# You may redirect the user to this URL when they click a "download" button.
print(signed_get_object_url)
# https://elicit.nyc3.digitaloceanspaces.com/3rr1sy21kml1r7y6hqsa5x68sgpx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=DO801PLEWTHUFYUEGJKB%2F20241230%2Fnyc3%2Fs3%2Faws4_request&X-Amz-Date=20241230T013839Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=f0473b018496a8b507397526c532c576ef2d2051922ebc4d3179754e92f31b4b"
