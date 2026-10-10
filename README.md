# IP Geolocation Loader

Load IP-to-country CSV data and perform fast range lookups using binary search on sorted start addresses.

## Usage

```python
import csv
import tempfile
from pathlib import Path

from ip_geolocation_loader import IPGeolocationLoader

# Create a temporary CSV file with IP-to-country data
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
) as tmp:
    writer = csv.writer(tmp)
    writer.writerows([
        ["1.0.0.0", "US"],
        ["2.0.0.0", "GB"],
    ])
    csv_path = Path(tmp.name)

loader = IPGeolocationLoader(csv_path)
country = loader.lookup("8.8.8.8")
print(country)  # "US"

csv_path.unlink()
```

The CSV file must contain at least two columns per row: the start IP address and the country code. Additional columns are ignored. The rows must be sorted by ascending start IP address. The first row is treated as data, not as a header.

## Why this library exists

IP-to-country datasets are often distributed as CSV files with IP ranges. To resolve an IP address to a country, you need to find the range that contains it. A naive linear scan is too slow for large datasets; this library uses the `bisect` module from the standard library to perform a binary search over the start addresses, reducing lookup time to O(log n) after an O(n) load. The trade-off is that the input data must already be sorted by start address, and the loader does not verify this.

## Edge cases

- If the query IP is below the first start address, `lookup` returns `None`.
- Invalid IP addresses raise `ValueError`.
- An empty CSV file produces a loader with zero ranges; `lookup` returns `None` for any IP.
- Rows with fewer than two columns raise `ValueError` during loading.

The exported names are `IPGeolocationLoader` and its methods `lookup`, `__len__`, and the properties `starts` and `countries`.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

