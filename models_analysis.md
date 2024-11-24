1. `Match` (Base Class) - DONE

- match_id (unique identifier)
- match_url (Flashscore URL)
- country
- competition
- match_date
- round
- home_team (relationship to Team)
- away_team (relationship to Team)
- status

2. `FixtureMatch` (extends Match) - DONE

- home_team_form (relationship to TeamForm)
- away_team_form (relationship to TeamForm)
- head_to_head (relationship to HeadToHead)

3. `PlayedMatch` (extends Match) - DONE

- final_score
- match_statistics (relationship to MatchStatistics)

4. `Team` - DONE

- team_id
- name
- country
- team_url (Flashscore URL)

5. `TeamForm` - DONE

- team (relationship to Team)
- last_k_matches (list of PlayedMatch references)
- period (timestamp range)

6. `HeadToHead` - DONE

- team_a (reference to Team)
- team_b (reference to Team)
- last_k_matches (list of PlayedMatch references)

7. `MatchStatistics` - DONE

- match_id (reference to PlayedMatch)
- possession
- shots_on_target
- shots_off_target
- corners
- fouls
- yellow_cards
- red_cards
- offsides
- other statistics as needed

Key Relationships:

1. Match -> Team (2 relationships: home and away)
2. FixtureMatch -> TeamForm (2 relationships: home and away)
3. FixtureMatch -> HeadToHead (1 relationship)
4. PlayedMatch -> MatchStatistics (1 relationship)
5. TeamForm -> Team (1 relationship)
6. TeamForm -> PlayedMatch (multiple: last k matches)
7. HeadToHead -> Team (2 relationships: team a and b)
8. HeadToHead -> PlayedMatch (multiple: last k matches)
