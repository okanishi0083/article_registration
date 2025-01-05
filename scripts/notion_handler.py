import logging

import requests
from exceptions import CompareAndUpdate, FetchError, NotionAPIError, ParseError

logging.basicConfig(filename="notion_api_errors.log", level=logging.ERROR)


class DataHandler:
    def __init__(self, database_id, notion_api_key):
        self.database_id = database_id
        self.notion_api_key = notion_api_key
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def fetch_existing_entries(self):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            raise FetchError(f"Failed to fetch existing entries: {e}")

    def compare_and_update(self, rss_entries, existing_entries):
        try:
            existing_entries_dict = {
                entry["properties"]["サイトのURL"]["url"]: entry
                for entry in existing_entries
            }
            new_entries = []
            updated_entries = []

            for rss_entry in rss_entries:
                existing = existing_entries_dict.get(rss_entry["url"])

                if existing:
                    existing_title = existing["properties"]["タイトル"]["title"][0][
                        "plain_text"
                    ]
                    existing_description = existing["properties"]["内容"]["rich_text"][
                        0
                    ]["plain_text"]

                    if (
                        rss_entry["title"] != existing_title
                        or rss_entry["description"] != existing_description
                    ):
                        updated_entries.append(rss_entry)
                else:
                    new_entries.append(rss_entry)

            return new_entries, updated_entries
        except:
            raise ConnectionAbortedError(f"Failed to fetch existing entries: {e}")

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
                },
            }
            response = requests.post(url, headers=self.headers, json=json_data)
            response.raise_for_status()
            print(f"Successfully posted: {entry['title']}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to post data: {json_data}\nError: {e}")
            print(f"Error occurred: {e}")

    def update_notion_entry(self, entry):
        # Implement the update logic here
        pass
