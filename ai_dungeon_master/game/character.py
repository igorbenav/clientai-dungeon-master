class Character:
    def __init__(self, name: str, race: str, class_type: str, background: str, stats: dict):
        self.name = name
        self.race = race
        self.class_type = class_type
        self.background = background
        self.stats = stats

    def __str__(self):
        return f"Name: {self.name}, Race: {self.race}, Class: {self.class_type}, Background: {self.background}, Stats: {self.stats}"
    