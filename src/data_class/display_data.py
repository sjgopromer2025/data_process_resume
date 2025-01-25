class DisplayInfo:
    def __init__(self, display_name, display_id, year=None, month=None, day=None):
        self.display_name = display_name
        self.display_id = display_id
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return (
            f"DisplayInfo(display_name={self.display_name}, "
            f"display_id={self.display_id}, year={self.year}, "
            f"month={self.month}, day={self.day})"
        )

    def to_dict(self):
        return {
            "display_name": self.display_name,
            "display_id": self.display_id,
            "year": self.year,
            "month": self.month,
            "day": self.day,
        }
