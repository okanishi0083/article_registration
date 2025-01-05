from constant.rss_types import RSSTypes


class DateFields:
    FIELDS = {RSSTypes.NIKKEI: "updated_parsed", RSSTypes.ITMEDIA: "published_parsed"}

    @classmethod
    def get(cls, rss_type):
        """Returns the date field for the given RSS type."""
        return cls.FIELDS.get(rss_type, "published_parsed")  # デフォ
