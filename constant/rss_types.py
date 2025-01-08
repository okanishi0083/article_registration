class RSSTypes:
    NIKKEI = "nikkei"
    ITMEDIA = "itmedia"
    MYNABI = "mynavi"
    ENTERPRISEZINE = "enterprisezine"

    @classmethod
    def initialize_entries(cls):
        """Initializes a dictionary with RSS types as keys and empty lists as values."""
        return {cls.NIKKEI: [], cls.ITMEDIA: [], cls.MYNABI: [], cls.ENTERPRISEZINE: []}

    @classmethod
    def get_all_types(cls):
        """Returns a list of all RSS types."""
        return [cls.NIKKEI, cls.ITMEDIA, cls.MYNABI, cls.ENTERPRISEZINE]
