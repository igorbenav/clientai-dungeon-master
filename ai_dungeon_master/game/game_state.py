from typing import Optional

from .character import Character

class GameState:
    def __init__(self, character: Character):
        self.character = character
        self.location = "entrance"
        self.inventory = []
        self.health = 100
        self.experience = 0
        self.quests = []

    def update(self, location: Optional[str] = None, item: Optional[str] = None, health_change: int = 0, exp_gain: int = 0, quest: Optional[str] = None):
        if location:
            self.location = location
        if item:
            self.inventory.append(item)
        self.health = max(0, min(100, self.health + health_change))
        self.experience += exp_gain
        if quest:
            self.quests.append(quest)

    def __str__(self):
        return f"{str(self.character)}\nLocation: {self.location}, Health: {self.health}, XP: {self.experience}, Inventory: {', '.join(self.inventory)}, Quests: {', '.join(self.quests)}"
