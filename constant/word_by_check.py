from constant.rss_types import RSSTypes


class WordByCheck:
    WORDS = {
        RSSTypes.NIKKEI: ["AI", "Google", "DX", "AWS"],
        RSSTypes.ITMEDIA: ["AI", "Google", "DX", "AWS"],
        RSSTypes.MYNABI: ["AI", "Google", "DX", "AWS"],
    }

    @classmethod
    def get_keywords(cls, rss_type):
        """Returns the date field for the given RSS type."""
        return cls.WORDS.get(rss_type, [])  # デフォ
