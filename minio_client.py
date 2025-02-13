from minio import Minio

minio_client=Minio(
    "127.0.0.1:9050",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)