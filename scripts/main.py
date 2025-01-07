import logging
import os

from exceptions import (
    CompareAndUpdate,
    FetchError,
    FetchExistingEntriesError,
    NotionAPIError,
    ParseError,
    UnexpectedError,
)
from notion_handler import DataHandler
from rss_fetcher import ContentFetcher

from constant.date_fields import DateFields
from constant.field_mappings import FieldMappings
from utils.date_utils import format_datetime, get_cutoff_date

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

    # 現在日付から2日前の日付を取得
    cutoff_date = get_cutoff_date()
    # 現在日付
    now_date = get_cutoff_date(0)

    fetcher = ContentFetcher(rss_urls)
    handler = DataHandler(
        database_id,
        notion_api_key,
        format_datetime(cutoff_date),
        format_datetime(now_date),
    )

    try:
        all_entries = fetcher.fetch_entries()

        # 既存のエントリーを取得
        existing_entries = handler.fetch_existing_entries()

        new_entries = []
        updated_entries = []

        for rss_type, entry_list in all_entries.items():
            date_field = DateFields.get(rss_type)  # デフォルトは 'published_parsed'

            field_mapping = FieldMappings.get(rss_type)

            for entry in entry_list:
                update_data = []
                recent_entry = fetcher.filter_recent_entries(
                    entry, date_field, cutoff_date, field_mapping
                )
                if recent_entry:
                    # 新規エントリーと更新エントリーを比較・更新
                    is_new, is_updated = handler.compare_update_or_insert(
                        recent_entry, existing_entries
                    )
                    if is_new:
                        new_entries.append(recent_entry)
                    elif is_updated:
                        update_data = handler.create_update_data(
                            recent_entry, existing_entries
                        )
                        updated_entries.append(update_data)

    except (
        FetchError,
        ParseError,
        UnexpectedError,
        NotionAPIError,
        CompareAndUpdate,
    ) as e:
        logging.error(f"Error: {e}")
        exit()
    except FetchExistingEntriesError as e:
        logging.error(f"FetchExistingEntriesError: {e}")
        exit()
    except Exception as e:
        logging.error(f"Exception: {e}")
        exit()

    try:
        for entry in new_entries:
            handler.post_to_notion(entry)
    except NotionAPIError as e:
        logging.error(f"Error posting new entry to Notion: {e}")

    try:
        for updated_entry in updated_entries:
            handler.update_notion_entry(updated_entry)
    except NotionAPIError as e:
        logging.error(f"Error updating entry in Notion: {e}")


if __name__ == "__main__":
    main()
