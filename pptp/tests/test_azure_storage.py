from django.test import SimpleTestCase, override_settings

from ..storage.azure import AzureBlobStorage, AzureBlobStorageError

WRITE_TOKEN = "sv=2022-11-02&sr=c&sp=racwdl&se=2027-01-01T00:00:00Z&sig=WRITESIG"
READ_TOKEN = "sv=2022-11-02&sr=c&sp=r&se=2027-01-01T00:00:00Z&sig=READSIG"


@override_settings(
    AZURE_ACCOUNT_URL="https://example.blob.core.windows.net",
    AZURE_SAS_TOKEN=WRITE_TOKEN,
    AZURE_CONTAINER="datahub",
)
class ImageUrlTests(SimpleTestCase):
    @override_settings(AZURE_READ_SAS_TOKEN=READ_TOKEN)
    def test_url_carries_only_the_read_token(self):
        url = AzureBlobStorage().url("nutritionfacts/IMG_1.jpg")
        assert url == f"https://example.blob.core.windows.net/datahub/nutritionfacts/IMG_1.jpg?{READ_TOKEN}"
        assert "WRITESIG" not in url

    @override_settings(AZURE_READ_SAS_TOKEN="?" + READ_TOKEN)
    def test_leading_question_mark_is_accepted(self):
        assert AzureBlobStorage().url("a.jpg").endswith(f"/datahub/a.jpg?{READ_TOKEN}")

    @override_settings(AZURE_READ_SAS_TOKEN=None)
    def test_without_read_token_no_token_is_sent(self):
        assert AzureBlobStorage().url("a.jpg") == "https://example.blob.core.windows.net/datahub/a.jpg"

    @override_settings(AZURE_READ_SAS_TOKEN=WRITE_TOKEN)
    def test_write_capable_read_token_is_refused(self):
        with self.assertRaises(AzureBlobStorageError):
            AzureBlobStorage()
