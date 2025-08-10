from django.conf import settings
from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Custom storage class that extends WhiteNoise to handle static files properly
    """
    pass