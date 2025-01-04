def create_notion_json(title, date, url, database_id):
    json_data = {
        'parent': { 'database_id': database_id },
        'properties': {
            'タイトル': {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title,
                            "link": None
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": title,
                        "href": None
                    }
                ]
            },
            '作成日': {
                "date": {
                    "start": date
                }
            },
            'サイトのURL': {
                "url": url
            },
        },
    }
    return json_data