# RSS Filter Proxy

A lightweight, configurable HTTP proxy that serves a filtered RSS feed.  
Fetches an upstream RSS/Atom feed, filters entries by title, and exposes a new RSS feed over HTTP.

Designed to be generic and reusable via a `.env` file, so you can adapt it to different feeds and filtering rules without changing code.

***

## Features

- Fetches any public RSS/Atom feed
- Filters entries by title using:
  - **Include tags**: keep only items whose title contains at least one of these substrings
  - **Exclude patterns**: drop items whose title matches any of these patterns (plain text or regex)
- Serves the filtered feed over HTTP as `application/rss+xml`
- Fully configured via `.env`:
  - Change feed URL, host, port, and filter rules without touching code
- Easy to reuse for multiple feeds (run multiple instances on different ports or with different `.env` files)

Typical use case: plug this between an RSS source (e.g. Reddit, blogs, news sites) and tools like `rss-bridge-ntfy`, Home Assistant, Feedly, etc., to pre-filter content.

***

## Requirements

- Python 3.8+
- `pip`

Dependencies:

- `feedparser`
- `python-dotenv`

***

## Installation

1. Clone or copy the files into a directory, e.g.:

   ```text
   rss-filter-proxy/
     .env
     filter.py
     requirements.txt
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

***

## Configuration (.env)

Create a `.env` file in the same directory as `filter.py`.

### Example: FreeGameFindings (keep only games, exclude PS/Xbox)

```env
# Upstream RSS/Atom feed URL
FEED_URL=https://www.reddit.com/r/FreeGameFindings.rss

# HTTP server binding
HOST=0.0.0.0
PORT=8080

# Title filters
# Comma-separated list; spaces around values are trimmed
# Leave INCLUDE_TAGS empty to disable include filtering (keep all by default)
INCLUDE_TAGS=(Game)

# Exclude patterns: drop items whose title contains any of these
EXCLUDE_PATTERNS=[PlayStation],[PS],[Xbox]

# Use regex for exclude patterns? true/false
# If true, each pattern in EXCLUDE_PATTERNS is treated as a regex (case-insensitive)
EXCLUDE_USE_REGEX=false
```

### Example: Another feed (patch notes, exclude beta)

```env
FEED_URL=https://example.com/some-feed.rss
HOST=0.0.0.0
PORT=8081

# Keep only titles containing "Patch" or "Update"
INCLUDE_TAGS=Patch,Update

# Exclude titles containing "[Beta]"
EXCLUDE_PATTERNS=\[Beta\]

# Enable regex for exclude patterns
EXCLUDE_USE_REGEX=true
```

### Environment variables

| Variable            | Required | Default      | Description                                                                 |
|---------------------|----------|--------------|-----------------------------------------------------------------------------|
| `FEED_URL`          | yes      | –            | URL of the upstream RSS/Atom feed                                          |
| `HOST`              | no       | `0.0.0.0`    | HTTP bind address                                                          |
| `PORT`              | no       | `8080`       | HTTP port                                                                  |
| `INCLUDE_TAGS`      | no       | (empty)      | Comma-separated substrings; title must contain at least one to be kept     |
| `EXCLUDE_PATTERNS`  | no       | (empty)      | Comma-separated patterns; title matching any is dropped                    |
| `EXCLUDE_USE_REGEX` | no       | `false`      | If `true`, treat `EXCLUDE_PATTERNS` as case-insensitive regex patterns     |

**Notes:**

- If `INCLUDE_TAGS` is empty, no include filtering is applied (all titles pass this check).
- If `EXCLUDE_PATTERNS` is empty, no exclude filtering is applied.
- For regex mode, patterns are compiled with `re.IGNORECASE`.

***

## Usage

1. Configure `.env` as described above.
2. Run the proxy:

   ```bash
   python filter.py
   ```

3. Access the filtered feed at:

   ```text
   http://<host>:<port>/
   ```

   Example:

   ```text
   http://localhost:8080/
   ```

4. Use this URL as the RSS source in your downstream tool (e.g. `rss-bridge-ntfy`).

***

## Running multiple instances

To serve multiple filtered feeds:

- Copy the directory (or reuse the same code with different `.env` files)
- Set different `FEED_URL`, `PORT`, and filter rules in each `.env`
- Run one instance per configuration:

  ```bash
  # Instance 1
  cd rss-filter-proxy-fgf
  python filter.py

  # Instance 2
  cd rss-filter-proxy-patches
  python filter.py
  ```

Each will listen on its own port and serve its own filtered feed.

***

## Docker (optional)

Build and run:

```bash
docker build -t rss-filter-proxy .
docker run --rm -p 8080:8080 --env-file .env rss-filter-proxy
```

Adjust `PORT` in `.env` and the `-p` mapping as needed.

***
