"""IP Geolocation Loader.

Load IP-to-country CSV data and provide fast range lookup using binary
search on sorted start addresses.
"""

from .core import IPGeolocationLoader

__all__ = ["IPGeolocationLoader"]
