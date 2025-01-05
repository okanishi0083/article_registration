class RSSTypes:
    NIKKEI = "nikkei"
    ITMEDIA = "itmedia"

    @classmethod
    def initialize_entries(cls):
        """Initializes a dictionary with RSS types as keys and empty lists as values."""
        return {cls.NIKKEI: [], cls.ITMEDIA: []}
