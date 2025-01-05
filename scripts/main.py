import logging
import os

from exceptions import (
    CompareAndUpdate,
    FetchError,
    NotionAPIError,
    ParseError,
    UnexpectedError,
)
from notion_handler import DataHandler
from rss_fetcher import ContentFetcher

# ログ設定
logging.basicConfig(filename="application_errors.log", level=logging.ERROR)


def main():

    if os.getenv("GITHUB_ACTIONS") == "true":
        print("Running in GitHub Actions")
    else:
        from dotenv import load_dotenv

        load_dotenv()

    rss_urls = os.getenv("RSS_URLS").split(",")
    database_id = os.getenv("NOTION_DATABASE_ID")
    notion_api_key = os.getenv("NOTION_API_KEY")

    fetcher = ContentFetcher(rss_urls)
    handler = DataHandler(database_id, notion_api_key)

    try:
        rss_datas = fetcher.fetch_entries()
        rss_entries = fetcher.filter_recent_entries(rss_datas)
    except (FetchError, ParseError, UnexpectedError) as e:
        logging.error(f"RSS processing error: {e}")
        return

    try:
        existing_entries = handler.fetch_existing_entries()
    except NotionAPIError as e:
        logging.error(f"Notion API error: {e}")
        return

    try:
        new_entries, updated_entries = handler.compare_and_update(rss_entries)
    except CompareAndUpdate as e:
        logging.error(f"Notion API error: {e}")
        return

    try:
        for entry in new_entries:
            handler.post_to_notion(entry)
    except NotionAPIError as e:
        logging.error(f"Error posting new entry to Notion: {e}")

        try:
            for entry in updated_entries:
                handler.update_notion_entry(entry)
        except NotionAPIError as e:
            logging.error(f"Error updating entry in Notion: {e}")


if __name__ == "__main__":
    main()
