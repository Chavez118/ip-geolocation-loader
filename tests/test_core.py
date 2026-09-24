"""Tests for the IP geolocation loader."""

import csv
import ipaddress
import tempfile
import unittest
from pathlib import Path

from ip_geolocation_loader import IPGeolocationLoader


class TestIPGeolocationLoader(unittest.TestCase):
    """Test cases for IPGeolocationLoader."""

    def _write_csv(self, rows):
        """Write rows to a temporary CSV file and return its path."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
        )
        with tmp:
            writer = csv.writer(tmp)
            writer.writerows(rows)
        return Path(tmp.name)

    def test_lookup_exact_start(self):
        rows = [
            ["1.0.0.0", "US"],
            ["2.0.0.0", "GB"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(loader.lookup("1.0.0.0"), "US")
        finally:
            path.unlink()

    def test_lookup_between_starts(self):
        rows = [
            ["1.0.0.0", "US"],
            ["2.0.0.0", "GB"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            # 1.0.0.1 is between the two start addresses, so should map to US
            self.assertEqual(loader.lookup("1.0.0.1"), "US")
        finally:
            path.unlink()

    def test_lookup_before_first_start(self):
        rows = [
            ["2.0.0.0", "GB"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertIsNone(loader.lookup("1.255.255.255"))
        finally:
            path.unlink()

    def test_lookup_last_range(self):
        rows = [
            ["1.0.0.0", "US"],
            ["2.0.0.0", "GB"],
            ["3.0.0.0", "DE"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(loader.lookup("4.0.0.1"), "DE")
        finally:
            path.unlink()

    def test_lookup_ipv6(self):
        rows = [
            ["2001:db8::", "US"],
            ["2001:db8:1::", "GB"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(loader.lookup("2001:db8::1"), "US")
            self.assertEqual(loader.lookup("2001:db8:1::1"), "GB")
        finally:
            path.unlink()

    def test_lookup_invalid_ip_raises(self):
        rows = [["1.0.0.0", "US"]]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            with self.assertRaises(ValueError):
                loader.lookup("not-an-ip")
        finally:
            path.unlink()

    def test_empty_file(self):
        path = self._write_csv([])
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(len(loader), 0)
            self.assertIsNone(loader.lookup("1.2.3.4"))
        finally:
            path.unlink()

    def test_row_with_missing_column_raises(self):
        rows = [["1.0.0.0"]]
        path = self._write_csv(rows)
        try:
            with self.assertRaises(ValueError):
                IPGeolocationLoader(path)
        finally:
            path.unlink()

    def test_invalid_start_ip_raises(self):
        rows = [["not-an-ip", "US"]]
        path = self._write_csv(rows)
        try:
            with self.assertRaises(ValueError):
                IPGeolocationLoader(path)
        finally:
            path.unlink()

    def test_starts_and_countries_properties(self):
        rows = [
            ["1.0.0.0", "US"],
            ["2.0.0.0", "GB"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(
                loader.starts,
                (int(ipaddress.ip_address("1.0.0.0")), int(ipaddress.ip_address("2.0.0.0"))),
            )
            self.assertEqual(loader.countries, ("US", "GB"))
        finally:
            path.unlink()

    def test_len(self):
        rows = [
            ["1.0.0.0", "US"],
            ["2.0.0.0", "GB"],
            ["3.0.0.0", "DE"],
        ]
        path = self._write_csv(rows)
        try:
            loader = IPGeolocationLoader(path)
            self.assertEqual(len(loader), 3)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
