from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    AzureError
)
import logging
import os
from urllib.parse import parse_qs, urljoin, urlsplit
from django.core.exceptions import SuspiciousOperation

logger = logging.getLogger(__name__)

# Permissions a token handed to browsers may carry: read and list only.
READ_ONLY_PERMISSIONS = set("rl")


class AzureBlobStorageError(Exception):
    pass


@deconstructible
class AzureBlobStorage(Storage):
    def __init__(self):
        try:
            required_settings = {
                'AZURE_ACCOUNT_URL': getattr(settings, 'AZURE_ACCOUNT_URL', None),
                'AZURE_SAS_TOKEN': getattr(settings, 'AZURE_SAS_TOKEN', None),
                'AZURE_CONTAINER': getattr(settings, 'AZURE_CONTAINER', None),
            }

            missing_settings = []
            type_errors = []

            for setting_name, setting_value in required_settings.items():
                if setting_value is None:
                    missing_settings.append(setting_name)
                elif not isinstance(setting_value, str):
                    type_errors.append(f"{setting_name} (type: {type(setting_value).__name__})")
                elif not setting_value.strip():
                    missing_settings.append(f"{setting_name} (empty)")

            if missing_settings or type_errors:
                error_parts = []
                if missing_settings:
                    error_parts.append(f"Missing/empty: {', '.join(missing_settings)}")
                if type_errors:
                    error_parts.append(f"Wrong type: {', '.join(type_errors)}")
                raise AzureBlobStorageError(f"Azure configuration errors - {'; '.join(error_parts)}")

            self.account_url = required_settings['AZURE_ACCOUNT_URL']
            self.sas_token = required_settings['AZURE_SAS_TOKEN']
            self.container = required_settings['AZURE_CONTAINER']
            self.read_sas_token = self._read_only_token(getattr(settings, 'AZURE_READ_SAS_TOKEN', None))

            self.client = BlobServiceClient(
                account_url=self.account_url,
                credential=self.sas_token
            )
            self.container_client = self.client.get_container_client(self.container)

        except AzureBlobStorageError:
            raise
        except (AttributeError, ValueError) as e:
            raise AzureBlobStorageError(f"Azure storage configuration error: {str(e)}")
        except Exception as e:
            raise AzureBlobStorageError(f"Failed to initialize Azure storage: {str(e)}")

    @staticmethod
    def _read_only_token(token):
        """The token for image URLs, which every page viewer can see.

        AZURE_SAS_TOKEN can write and delete, so it must stay on the server. Refuse a
        URL token that grants anything beyond read/list.
        """
        token = (token or "").strip().lstrip("?")
        if not token:
            logger.warning("AZURE_READ_SAS_TOKEN is not set: image URLs are sent without a token")
            return ""
        permissions = parse_qs(token).get("sp", [""])[0]
        if not permissions or not set(permissions) <= READ_ONLY_PERMISSIONS:
            raise AzureBlobStorageError(
                f"AZURE_READ_SAS_TOKEN must be a read-only SAS (sp=r); it has sp={permissions or '(none)'}"
            )
        return token

    def __eq__(self, other):
        if not isinstance(other, AzureBlobStorage):
            return NotImplemented
        return (
            self.account_url == other.account_url and
            self.sas_token == other.sas_token and
            self.container == other.container
        )

    def _save(self, name, content):
        try:
            blob_client = self.container_client.get_blob_client(name)
            content.seek(0)
            blob_client.upload_blob(content, overwrite=True)
            return name
        except ClientAuthenticationError:
            raise AzureBlobStorageError("Azure authentication token has expired")
        except AzureError as e:
            raise AzureBlobStorageError(f"Failed to save file to Azure: {str(e)}")

    def _open(self, name, mode="rb"):
        try:
            blob_client = self.container_client.get_blob_client(name)
            stream = blob_client.download_blob()
            return stream.readall()
        except ResourceNotFoundError:
            return None
        except ClientAuthenticationError:
            raise AzureBlobStorageError("Azure authentication token has expired")
        except AzureError as e:
            raise AzureBlobStorageError(f"Failed to open file from Azure: {str(e)}")

    def delete(self, name):
        try:
            blob_client = self.container_client.get_blob_client(name)
            blob_client.delete_blob()
        except ResourceNotFoundError:
            pass
        except ClientAuthenticationError:
            raise AzureBlobStorageError("Azure authentication token has expired")
        except AzureError as e:
            raise AzureBlobStorageError(f"Failed to delete file from Azure: {str(e)}")

    def exists(self, name):
        try:
            blob_client = self.container_client.get_blob_client(name)
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except ClientAuthenticationError:
            raise AzureBlobStorageError("Azure authentication token has expired")
        except AzureError as e:
            raise AzureBlobStorageError(f"Failed to check file existence in Azure: {str(e)}")

    def url(self, name):
        # The client's URL carries AZURE_SAS_TOKEN (write/delete). Drop it and add the
        # read-only token instead.
        try:
            blob_url = urlsplit(self.container_client.get_blob_client(name).url)._replace(query="").geturl()
            return f"{blob_url}?{self.read_sas_token}" if self.read_sas_token else blob_url
        except ClientAuthenticationError:
            raise AzureBlobStorageError("Azure authentication token has expired")
        except AzureError as e:
            raise AzureBlobStorageError(f"Failed to generate URL: {str(e)}")

    def get_valid_name(self, name):
        return name

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        count = 1
        
        while self.exists(name):
            name = os.path.join(dir_name, f"{file_root}_{count}{file_ext}")
            count += 1
        return name