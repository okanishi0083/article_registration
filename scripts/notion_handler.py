import logging

import requests
from exceptions import (
    CompareAndUpdate,
    FetchError,
    FetchExistingEntriesError,
    NotionAPIError,
    ParseError,
)

logging.basicConfig(filename="notion_api_errors.log", level=logging.ERROR)


class DataHandler:
    def __init__(
        self, database_id, tag_database_id, notion_api_key, cutoff_date, now_date
    ):
        self.database_id = database_id
        self.tag_database_id = tag_database_id
        self.notion_api_key = notion_api_key
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        # リクエストのデータ (フィルター条件)
        self.get_api_data = {
            "filter": {
                "property": "作成日",
                "date": {"on_or_after": cutoff_date, "on_or_before": now_date},
            }
        }

    def fetch_existing_entries(self):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        try:
            response = requests.post(url, headers=self.headers, json=self.get_api_data)
            response.raise_for_status()
            entries = response.json()["results"]

            # URLをキー、ID、タイトル、内容を値とする辞書を作成
            url_info_map = {
                entry["properties"]["サイトのURL"]["url"]: {
                    "id": entry["id"],
                    "title": (
                        entry["properties"]["タイトル"]["title"][0]["plain_text"]
                        if entry["properties"]["タイトル"]["title"]
                        else ""
                    ),
                    "content": (
                        entry["properties"]["内容"]["rich_text"][0]["plain_text"]
                        if entry["properties"]["内容"]["rich_text"]
                        else ""
                    ),
                }
                for entry in entries
                if "サイトのURL" in entry["properties"]
                and "url" in entry["properties"]["サイトのURL"]
            }

            return url_info_map
            # return response.json()["results"]
        except requests.exceptions.RequestException as e:
            raise FetchExistingEntriesError(f"Failed to fetch existing entries: {e}")

    def compare_update_or_insert(self, rss_entry, existing_entries):
        try:
            is_new = False
            is_updated = False

            url = rss_entry["url"]
            existing_entry = existing_entries.get(url)

            if not existing_entry:
                is_new = True
                return is_new, is_updated

            if existing_entry:
                # Check if title and content are the same
                if (
                    rss_entry["title"] != existing_entry["title"]
                    or rss_entry["description"] != existing_entry["content"]
                ):
                    is_updated = True
                    # Perform update logic here
                    print(f"Update required for URL: {url}")
                    return is_new, is_updated
            # else:
            #     is_new = True
            #     # Perform insert logic here
            #     print(f"New entry for URL: {url}")
            return is_new, is_updated
        except:
            raise ConnectionAbortedError(f"Failed to fetch existing entries: {e}")

    def create_update_data(self, rss_entry, existing_entries):
        update_data = {}

        url = rss_entry["url"]
        existing_entry = existing_entries.get(url)

        if existing_entry:
            # Use the existing entry's ID as the key
            entry_id = existing_entry["id"]
            update_data[entry_id] = {
                "properties": {
                    "作成日": {
                        "date": {
                            "start": rss_entry[
                                "date"
                            ],  # Assuming rss_entry has a 'date' field
                            "end": None,
                        }
                    },
                    "サイトのURL": {"url": rss_entry["url"]},
                    "内容": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": rss_entry["description"],
                                    "link": None,
                                },
                            }
                        ]
                    },
                    "タイトル": {
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": rss_entry["title"], "link": None},
                            }
                        ]
                    },
                }
            }

        return update_data

    def post_to_notion(self, entry):
        url = "https://api.notion.com/v1/pages"
        try:
            json_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "タイトル": {"title": [{"text": {"content": entry["title"]}}]},
                    "作成日": {"date": {"start": entry["date"]}},
                    "サイトのURL": {"url": entry["url"]},
                    "内容": {
                        "rich_text": [{"text": {"content": entry["description"]}}]
                    },
                    "タグ": {"relation": entry["tag"]},
                },
            }
            response = requests.post(url, headers=self.headers, json=json_data)
            response.raise_for_status()
            print(f"Successfully posted: {entry['title']}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to post data: {json_data}\nError: {e}")
            print(f"Error occurred: {e}")

    def update_notion_entry(self, updated_entry):
        # Implement the update logic here
        try:
            # Assume updated_entry is a dictionary with a single key-value pair
            entry_id, entry_data = next(iter(updated_entry.items()))

            # Use the entry_id to construct the URL for updating the page
            url = f"https://api.notion.com/v1/pages/{entry_id}"

            response = requests.patch(url, headers=self.headers, json=entry_data)
            response.raise_for_status()
            print(f"Successfully updated entry with ID: {entry_id}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to update entry with ID: {entry_id}\nError: {e}")
            print(f"Error occurred while updating entry with ID: {entry_id}: {e}")

    def fetch_tags(self):

        url = f"https://api.notion.com/v1/databases/{self.tag_database_id}/query"

        # APIリクエストを送信
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return {}

    def extract_relation_ids(self, response):
        """
        Notion APIのレスポンスから名前をキー、関連ページのIDを値とする辞書を生成します。
        戻り値形式: { "名前": [{"id": "関連するページのID"}] }
        """
        results = response.get("results", [])
        relation_dict = {}

        for result in results:
            # 名前を取得
            title_property = result.get("properties", {}).get("名前", {})
            title_content = title_property.get("title", [])
            name = "".join([t.get("plain_text", "") for t in title_content])

            # 関連するページのIDを追加
            if name:
                if name not in relation_dict:
                    relation_dict[name] = []
                relation_dict[name] = result["id"]

        return relation_dict

    def extract_names_as_string(self, relation_dict, delimiter=", "):
        """
        名前をキーにした辞書から、名前部分だけを抽出し、文字列に変換します。
        :param relation_dict: 名前をキー、関連ページIDを値とした辞書
        :param delimiter: 名前を結合する際の区切り文字（デフォルト: カンマ+スペース）
        :return: 名前を結合した文字列
        """
        # relation_dictのキー（名前）を抽出して結合
        return delimiter.join(relation_dict.keys())

    def filtered_relation_ids_by_api_result(
        self, gpt_result_array, extract_relation_ids
    ):
        """
        GPTの結果配列と辞書をもとに、関連するページのIDを配列形式で返す。
        戻り値形式: [{ "id": "値1" }, { "id": "値2" }, ...]
        """
        result = []  # 最終的な結果を格納するリスト
        # dataをループしてextract_relation_idsから対応する値を取得
        for value in gpt_result_array:
            if (
                isinstance(value, str) and value in extract_relation_ids
            ):  # キーが文字列か確認
                result.append({"id": extract_relation_ids[value]})
        return result

        # # レスポンスのステータスコードを確認
        # if response.status_code != 200:
        #     print(f"Error: {response.status_code}, {response.text}")
        #     return []

        # # JSONレスポンスを取得
        # data = response.json()

        # # タグ情報を取得
        # tags = []
        # for result in data.get("results", []):
        #     # 「名前」フィールドからタイトルを抽出
        #     title_property = result.get("properties", {}).get("名前", {})
        #     title_content = title_property.get("title", [])

        #     # 各テキスト要素を結合して完全なタイトルを作成
        #     tag_name = "".join([t.get("plain_text", "") for t in title_content])
        #     if tag_name:  # 空でない場合のみ追加
        #         tags.append(tag_name)

        # return tags
