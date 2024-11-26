class Config:
    def __init__(self, country, league, rounds=1):
        self.country = country
        self.league = league
        self.rounds = rounds

    #  method for printing a config instance
    def __str__(self):
        return f"Country: {self.country}, League: {self.league}, Rounds: {self.rounds}"
