# rss_filter_proxy.py
import os
import re
import http.server
import socketserver
import feedparser
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from email.utils import formatdate
import time
from dotenv import load_dotenv

load_dotenv()

FEED_URL = os.getenv("FEED_URL", "").strip()
HOST = os.getenv("HOST", "0.0.0.0").strip()
PORT = int(os.getenv("PORT", "8080"))

# Comma-separated lists
INCLUDE_TAGS_RAW = os.getenv("INCLUDE_TAGS", "").strip()
EXCLUDE_PATTERNS_RAW = os.getenv("EXCLUDE_PATTERNS", "").strip()
EXCLUDE_USE_REGEX = os.getenv("EXCLUDE_USE_REGEX", "false").strip().lower() == "true"

def parse_list(value: str):
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]

INCLUDE_TAGS = parse_list(INCLUDE_TAGS_RAW)
EXCLUDE_PATTERNS = parse_list(EXCLUDE_PATTERNS_RAW)

# Precompile regexes if enabled
if EXCLUDE_USE_REGEX:
    EXCLUDE_REGEXES = [re.compile(p, re.IGNORECASE) for p in EXCLUDE_PATTERNS]
else:
    EXCLUDE_REGEXES = []

def matches_filters(title: str) -> bool:
    # Include filter: title must contain at least one of INCLUDE_TAGS
    if INCLUDE_TAGS:
        if not any(tag in title for tag in INCLUDE_TAGS):
            return False

    # Exclude filter
    if EXCLUDE_USE_REGEX:
        for rx in EXCLUDE_REGEXES:
            if rx.search(title):
                return False
    else:
        for pat in EXCLUDE_PATTERNS:
            if pat in title:
                return False

    return True

def build_filtered_rss(original_feed):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    if original_feed.feed.get("title"):
        t = SubElement(channel, "title")
        t.text = original_feed.feed.title + " (filtered)"
    if original_feed.feed.get("link"):
        l = SubElement(channel, "link")
        l.text = original_feed.feed.link
    if original_feed.feed.get("description"):
        d = SubElement(channel, "description")
        d.text = original_feed.feed.description

    for entry in original_feed.entries:
        title = entry.get("title", "")
        if not matches_filters(title):
            continue

        item = SubElement(channel, "item")
        t = SubElement(item, "title")
        t.text = title

        if entry.get("link"):
            l = SubElement(item, "link")
            l.text = entry.link

        if entry.get("id"):
            guid = SubElement(item, "guid")
            guid.text = entry.id

        ts = entry.get("published_parsed") or entry.get("updated_parsed")
        if ts:
            pub = SubElement(item, "pubDate")
            pub.text = formatdate(time.mktime(ts))

        if entry.get("description"):
            d = SubElement(item, "description")
            d.text = entry.description

    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        feed = feedparser.parse(FEED_URL)
        data = build_filtered_rss(feed)

        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    if not FEED_URL:
        raise RuntimeError("FEED_URL must be set in .env")

    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"Serving filtered RSS on http://{HOST}:{PORT}")
        httpd.serve_forever()