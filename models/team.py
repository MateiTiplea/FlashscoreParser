import json


class Team:
    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {"name": self.name}

    def __str__(self):
        return f"Team(name={self.name})"
