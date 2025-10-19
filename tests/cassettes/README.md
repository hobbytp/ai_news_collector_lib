# VCR Cassettes

This directory contains VCR cassette files for recording and replaying HTTP requests during tests.

## About Cassette Portability

The cassettes in this directory were originally recorded through a localhost proxy endpoint (`https://localhost:33210/`). However, the VCR configuration has been updated to normalize matching:

- **Old matcher**: `match_on=["method", "scheme", "host", "port", "path", "query"]` (binds to localhost:33210)
- **New matcher**: `match_on=["method", "path", "query"]` (ignores scheme/host/port differences)

This change ensures cassettes remain portable across different recording environments and network configurations. During replay, VCR will match requests based only on HTTP method, URL path, and query parameters, allowing cassettes to work regardless of whether the actual requests go to `localhost:33210`, `https://news.ycombinator.com`, or other upstream hosts.

## Recording New Cassettes

To record new cassettes against real upstream services:

```bash
# First time recording (or update existing)
ALLOW_NETWORK=1 UPDATE_CASSETTES=1 python -m pytest -m network -v
```

Newly recorded cassettes will be stored in this directory and can be reused for offline testing.

## References

- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- Related PR comments on cassette portability
