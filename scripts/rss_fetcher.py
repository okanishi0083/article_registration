import logging
from datetime import datetime, timedelta

import feedparser
import requests
from exceptions import FetchError, ParseError, UnexpectedError

from constant.rss_types import RSSTypes


class ContentFetcher:
    def __init__(self, urls):
        self.urls = urls

    def _determine_rss_type(self, url):
        if RSSTypes.NIKKEI in url:
            return RSSTypes.NIKKEI
        elif RSSTypes.ITMEDIA in url:
            return RSSTypes.ITMEDIA
        # 他の条件を追加可能
        return None

    def fetch_entries(self):
        all_entries = RSSTypes.initialize_entries()
        try:
            for url in self.urls:
                rss_type = self._determine_rss_type(url)
                if not rss_type:
                    logging.warning(f"Unknown RSS type for URL: {url}")
                    continue

                response = requests.get(url)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
                if feed.bozo:
                    raise ParseError(f"Failed to parse feed: {url}")

                for entry in feed.entries:
                    all_entries[rss_type].append(entry)

        except requests.exceptions.RequestException as e:
            raise FetchError(f"Network error fetching RSS feed from {url}: {e}")
        except ParseError as e:
            raise ParseError(
                f"Error processing entry: {entry.title if 'title' in entry else 'Unknown'}: {e}"
            )
        except Exception as e:
            raise UnexpectedError(f"Unexpected error fetching RSS feed from {url}: {e}")

        return all_entries

    def filter_recent_entries(self, entry, date_field, cutoff_date, field_mapping):
        # cutoff_date = datetime.now() - timedelta(days=2)
        try:
            entry_date = datetime(*getattr(entry, date_field)[:6])
            if entry_date >= cutoff_date:
                return {
                    "title": getattr(entry, field_mapping["title"]),
                    "url": getattr(entry, field_mapping["url"]),
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "description": getattr(entry, field_mapping["description"]),
                }
        except Exception as e:
            raise ParseError(
                f"Error processing entry: {entry.title if 'title' in entry else 'Unknown'}: {e}"
            )
        return None
