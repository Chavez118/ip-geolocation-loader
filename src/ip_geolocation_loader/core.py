"""Core implementation of the IP geolocation loader.

This module contains the IPGeolocationLoader class which loads IP range to
country CSV data and provides a lookup method using binary search.
"""

from __future__ import annotations

import csv
import ipaddress
from bisect import bisect_right
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union


class IPGeolocationLoader:
    """Load and query IP-to-country range data.

    The loader expects CSV data where each row contains at least two columns:
    the start IP address of a range and the country code associated with that
    range. Rows may contain additional columns; they are ignored. The input
    must be sorted by ascending start IP address. This requirement is not
    checked; if the data is unsorted the lookup results are undefined.

    The loader stores the start addresses as integers for efficient binary
    search using the standard library's bisect module.
    """

    def __init__(self, csv_path: Union[str, Path]) -> None:
        """Create a loader from a CSV file path.

        Args:
            csv_path: Path to the CSV file. The file must be readable and
                contain at least the two required columns per row.

        Raises:
            FileNotFoundError: If the path does not exist.
            csv.Error: If the file is not valid CSV.
            ValueError: If a start IP address is invalid or if a row has
                fewer than two columns.
        """
        self._starts: List[int] = []
        self._countries: List[str] = []
        self._load(Path(csv_path))

    def _load(self, path: Path) -> None:
        """Load CSV data into sorted start address and country lists.

        The CSV file is opened with newline='' to handle platform-specific
        line endings correctly. The csv.reader is used in default mode, which
        means the first row is treated as data, not as a header. If the file
        has a header row, the caller must skip it before passing the file to
        this class, or provide a file without a header.

        Args:
            path: Path to the CSV file.

        Raises:
            FileNotFoundError: If the file does not exist.
            csv.Error: If the CSV parsing fails.
            ValueError: If a start IP address is invalid or a row has fewer
                than two columns.
        """
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    raise ValueError(
                        f"CSV row has {len(row)} columns; expected at least 2"
                    )
                start_str = row[0].strip()
                country = row[1].strip()
                try:
                    start_int = int(ipaddress.ip_address(start_str))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid IP address: {start_str!r}"
                    ) from exc
                self._starts.append(start_int)
                self._countries.append(country)

    def lookup(self, ip: str) -> Optional[str]:
        """Return the country code for the given IP address.

        The lookup uses binary search to find the rightmost start address that
        is less than or equal to the query IP. This corresponds to the most
        specific range that contains the IP when ranges are contiguous and
        sorted by start address.

        Args:
            ip: A string containing an IPv4 or IPv6 address.

        Returns:
            The country code associated with the containing range, or None if
            the IP is below the first start address.

        Raises:
            ValueError: If the IP string is not a valid IP address.
        """
        try:
            ip_int = int(ipaddress.ip_address(ip))
        except ValueError as exc:
            raise ValueError(f"Invalid IP address: {ip!r}") from exc

        if not self._starts:
            return None

        # bisect_right returns the insertion point after any existing entries
        # equal to ip_int. We want the index of the last start address <= ip_int.
        idx = bisect_right(self._starts, ip_int) - 1
        if idx < 0:
            return None
        return self._countries[idx]

    def __len__(self) -> int:
        """Return the number of loaded ranges."""
        return len(self._starts)

    @property
    def starts(self) -> Tuple[int, ...]:
        """Return a tuple of start addresses as integers.

        This is primarily useful for testing and debugging.
        """
        return tuple(self._starts)

    @property
    def countries(self) -> Tuple[str, ...]:
        """Return a tuple of country codes in the same order as starts."""
        return tuple(self._countries)
