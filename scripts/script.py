import requests

NOTION_API_KEY = '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'
DATABASE_ID = '170db76aa9f98037a6b0e8c70800bbd1'

url = 'https://api.notion.com/v1/pages'

headers =  {
    'Notion-Version': '2022-06-28',
    'Authorization': 'Bearer ' + NOTION_API_KEY,
    'Content-Type': 'application/json',
}

json_data = {
    'parent': { 'database_id': DATABASE_ID },
    'properties': {
        'タイトル': {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "A better title for the page",
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
                    "plain_text": "This is also not done",
                    "href": None
                }
            ]
        },
        '作成日':{
            "date": {
                "start": "2023-02-23"
            }
        },
        'サイトのURL':{
            "url": "https://developers.notion.com/"
        },
    },
}

response = requests.post(url, headers=headers, json=json_data)
print(response)