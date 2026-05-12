import logging

import boto3
from botocore.exceptions import ClientError

from src.backfill.core.exceptions import S3UploadError

logger = logging.getLogger(__name__)


class S3DataLakeUploader:
    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        self.s3_client = boto3.client("s3", region_name=region_name)
        self._bucket_name = bucket_name

    def upload_json(self, json_data: str, s3_key: str) -> bool:
        """Faz o upload da string JSON para o S3."""
        logger.info(f"Iniciando upload para s3://{self._bucket_name}/{s3_key}")

        try:
            self.s3_client.put_object(
                Bucket=self._bucket_name, Key=s3_key, Body=json_data
            )
            logger.info("Upload concluído com sucesso!")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Erro da AWS no S3 [{error_code}]: {e}")
            raise S3UploadError(f"Falha ao enviar para o S3: {error_code}")

        except Exception as e:
            logger.error(f"Erro inesperado no upload: {e}")
            raise S3UploadError(f"Erro interno no upload: {e}")
