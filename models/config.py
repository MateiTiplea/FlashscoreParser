class Config:
    def __init__(self, country, league, league_url, rounds=1):
        self.country = country
        self.league = league
        self.league_url = league_url
        self.rounds = rounds

    #  method for printing a config instance
    def __str__(self):
        return f"Country: {self.country}, League: {self.league}, Rounds: {self.rounds}"
