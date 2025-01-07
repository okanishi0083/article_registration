from constant.rss_types import RSSTypes


class WordByCheck:
    WORDS = {
        RSSTypes.NIKKEI: ["AI", "Google", "DX", "AWS", "IT"],
        RSSTypes.ITMEDIA: ["AI", "Google", "DX", "AWS", "IT"],
        RSSTypes.MYNABI: ["AI", "Google", "DX", "AWS", "ノーコード", "IT"],
    }

    @classmethod
    def get_keywords(cls, rss_type):
        """Returns the date field for the given RSS type."""
        return cls.WORDS.get(rss_type, [])  # デフォ
