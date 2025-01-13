import json
import logging
import os

from chat_gpt import CustomGPTClient
from create_chat_gpt_param import (
    edit_user_input,
    system_message_generator,
    temperature_generator,
)
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
from constant.word_by_check import WordByCheck
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
    tag_database_id = os.getenv("NOTION_TAG_DATABASE_ID")
    notion_api_key = os.getenv("NOTION_API_KEY")

    # 現在日付から2日前の日付を取得
    cutoff_date = get_cutoff_date()
    # 現在日付
    now_date = get_cutoff_date(0)

    fetcher = ContentFetcher(rss_urls)

    custom_gpt_client = CustomGPTClient(
        api_key=os.getenv("CHAT_GPT_KEY"),
        custom_gpt_id=os.getenv("CUSTOM_GPT_ID"),
        system_message_generator=system_message_generator,
        edit_user_input=edit_user_input,
        temperature_generator=temperature_generator,
    )
    handler = DataHandler(
        database_id,
        tag_database_id,
        notion_api_key,
        format_datetime(cutoff_date),
        format_datetime(now_date),
    )

    try:
        all_entries = fetcher.fetch_entries()

        # 既存のエントリーを取得
        existing_entries = handler.fetch_existing_entries()

        # タグデータ取得
        fetch_tags = handler.fetch_tags()
        extract_relation_ids = handler.extract_relation_ids(fetch_tags)
        extract_names_as_string = handler.extract_names_as_string(extract_relation_ids)

        new_entries = []
        updated_entries = []

        for rss_type, entry_list in all_entries.items():
            date_field = DateFields.get(rss_type)  # デフォルトは 'published_parsed'

            field_mapping = FieldMappings.get(rss_type)

            for entry in entry_list:

                # タイトル、本文に含まれているかチェックする単語の配列
                keywords = WordByCheck.get_keywords(rss_type)

                # タイトルに指定の文字が含まれてないない、かつ、本文にも含まれていなければ処理対象外
                if not fetcher.contains_any_keyword(
                    entry, field_mapping["title"], keywords
                ) and not fetcher.contains_any_keyword(
                    entry, field_mapping["description"], keywords
                ):
                    continue

                update_data = []
                recent_entry = fetcher.filter_recent_entries(
                    entry, date_field, cutoff_date, field_mapping
                )
                if recent_entry:
                    # TODO ここでchatgptapi呼び出し
                    # gpt_result = custom_gpt_client.send_message(
                    #     tag_data=extract_names_as_string, entry=entry
                    # )
                    # # 取得した文字列を配列に変換
                    # gpt_result_array = json.loads(gpt_result)
                    # filtered_relation_ids_by_api_result = (
                    #     handler.filtered_relation_ids_by_api_result(
                    #         gpt_result_array, extract_relation_ids
                    #     )
                    # )

                    # entry = fetcher.add_tag_data(
                    #     recent_entry, filtered_relation_ids_by_api_result
                    # )

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
