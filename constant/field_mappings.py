from constant.rss_types import RSSTypes


class FieldMappings:
    MAPPINGS = {
        RSSTypes.NIKKEI: {
            "title": "title",
            "url": "id",
            "description": "summary",
        },
        RSSTypes.ITMEDIA: {
            "title": "title",
            "url": "link",
            "description": "summary",
        },
    }

    @classmethod
    def get(cls, rss_type):
        """Returns the date field for the given RSS type."""
        return cls.MAPPINGS.get(rss_type, "published_parsed")  # デフォ
