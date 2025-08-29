import os
import asyncio
from uuid import uuid4
from typing import Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.configs.settings import settings
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class DOSpace:
    def __init__(self):
        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            region_name=settings.do_spaces_region,
            endpoint_url=settings.do_spaces_endpoint,
            aws_access_key_id=settings.do_spaces_key,
            aws_secret_access_key=settings.do_spaces_secret,
            config=Config(s3={'addressing_style': 'virtual'})
        )
        self.bucket = settings.do_spaces_bucket

    async def upload_file(self, file_content: bytes, file_ext: str) -> str:
        """
        Async upload a file to Digital Ocean Spaces and return its public URL.
        """
        temp_file = f"/tmp/{uuid4()}.{file_ext}"
        try:
            # 1) write file off the event loop
            await asyncio.to_thread(self._write_temp, temp_file, file_content)

            # 2) generate storage key
            key = self._generate_key(file_ext)

            # 3) upload off the event loop
            await asyncio.to_thread(
                self.client.upload_file,
                temp_file,
                self.bucket,
                key,
                ExtraArgs={'ACL': 'public-read'}
            )

            return self._get_public_url(key)

        except Exception as e:
            logger.exception("Failed to upload file to DO Spaces")
            raise Exception("Failed to upload file") from e

        finally:
            if os.path.exists(temp_file):
                # cleanup off the event loop
                await asyncio.to_thread(os.remove, temp_file)

    def _write_temp(self, path: str, content: bytes):
        with open(path, "wb") as f:
            f.write(content)

    def _generate_key(self, file_ext: str) -> str:
        return f"uploads/{uuid4()}.{file_ext}"

    def _get_public_url(self, key: str) -> str:
        return f"{settings.do_spaces_endpoint}/{self.bucket}/{key}"

    def get_file(self, key: str) -> Optional[bytes]:
        """
        Get a file from Digital Ocean Spaces.
        
        Args:
            key (str): The key of the file to get
            
        Returns:
            Optional[bytes]: The file content if found, None otherwise
            
        Raises:
            Exception: If the retrieval fails
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.exception("Failed to get file")
            raise Exception("Failed to get file") from e

    def delete_file(self, key: str) -> bool:
        """
        Delete a file from Digital Ocean Spaces.
        
        Args:
            key (str): The key of the file to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If the deletion fails
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except Exception as e:
            logger.exception("Failed to delete file")
            raise Exception("Failed to delete file") from e

    def get_file_url(self, key: str) -> Optional[str]:
        """
        Get the public URL of an existing file.
        
        Args:
            key (str): The key of the file
            
        Returns:
            Optional[str]: The public URL if the file exists, None otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return self._get_public_url(key)
        except:
            return None


do_space = DOSpace()