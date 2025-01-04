import json
from scraper import ITMediaBusinessScraper, ITMediaEnterpriseScraper
from notion import create_notion_json

DATABASE_ID = 'your_database_id_here'

def main():
    business_scraper = ITMediaBusinessScraper(
        url="https://www.itmedia.co.jp/business/subtop/digitalgovernment/",
        date_format="%Y年%m月%d日"
    )
    enterprise_scraper = ITMediaEnterpriseScraper(
        url="https://www.itmedia.co.jp/enterprise/subtop/archive/",
        date_format="%Y年%m月%d日",
        keywords=["IT", "LLM", "DX", "AI"]
    )

    for scraper in [business_scraper, enterprise_scraper]:
        soup = scraper.fetch_articles()
        if soup:
            articles = scraper.parse_articles(soup)
            filtered_articles = scraper.filter_articles(articles)
            for article in filtered_articles:
                notion_json = create_notion_json(article['title'], article['date'], article['url'], DATABASE_ID)
                print(json.dumps(notion_json, ensure_ascii=False, indent=2))
                # Here you would send the JSON to Notion API
                # response = requests.post(notion_url, headers=headers, json=notion_json)
                # print(response.status_code, response.json())

if __name__ == "__main__":
    main()