import csv
import math


# Constants
# FiveThirtyEight's Elo model defauts
HFA = 65.0     # Home field advantage is worth 65 Elo points
K = 20.0       # The speed at which Elo ratings change
REVERT = 1/3.0 # Between seasons, a team retains 2/3 of its previous season's rating

# Reversions for teams that have changed cities or names
# Reversions for teams that have changed cities or names
REVERSIONS = {'CBD1925': 1502.032, 'RAC1926': 1403.384, 'LOU1926': 1307.201, 'CIB1927': 1362.919, 'MNN1929': 1306.702, # Some between-season reversions of unknown origin
              'BFF1929': 1331.943, 'LAR1944': 1373.977, 'PHI1944': 1497.988, 'ARI1945': 1353.939, 'PIT1945': 1353.939, 'CLE1999': 1300.0}

class Forecast:

    @staticmethod
    def forecast(games: list, hfa_value: float=None, k_value: float = None, revert_value: float = None) -> list:
        """ Generates win probabilities in the my_prob1 field for each game based on Elo model """
        revert_value = float(revert_value) if revert_value else REVERT
        hfa_value = hfa_value if hfa_value else HFA
        k_value = k_value if k_value else K

        
        # Initialize team objects to maintain ratings
        teams = {}
        for row in [item for item in csv.DictReader(open("data/initial_elos.csv"))]:
            teams[row['team']] = {
                'name': row['team'],
                'season': None,
                'elo': float(row['elo'])
            }

        for game in games:
            team1, team2 = teams[game['team1']], teams[game['team2']]

            # Revert teams at the start of seasons
            for team in [team1, team2]:
                if team['season'] and game['season'] != team['season']:
                    k = "%s%s" % (team['name'], game['season'])
                    if k in REVERSIONS:
                        team['elo'] = REVERSIONS[k]
                    else:
                        team['elo'] = 1505.0*revert_value + team['elo']*(1-revert_value)
                        team['elo'] = 1505.0*revert_value + team['elo']*(1-revert_value)
                team['season'] = game['season']
            
            # Elo difference includes home field advantage
            if game['is_home'] == 1:
                elo_diff = team1['elo'] - team2['elo'] + (0 if game['neutral'] == 1 else (hfa_value/2))
            else:
                elo_diff = team1['elo'] - team2['elo'] - (0 if game['neutral'] == 1 else (hfa_value/2))

            # This is the most important piece, where we set my_prob1 to our forecasted probability
            if game['elo_prob1'] != None:
                game['my_prob1'] = 1.0 / (math.pow(10.0, (-elo_diff/400.0)) + 1.0)

            # If game was played, maintain team Elo ratings
            if game['score1'] != None:

                # Margin of victory is used as a K multiplier
                pd = abs(game['score1'] - game['score2'])
                mult = math.log(max(pd, 1) + 1.0) * (2.2 / (1.0 if game['result1'] == 0.5 else ((elo_diff if game['result1'] == 1.0 else -elo_diff) * 0.001 + 2.2)))

                # Elo shift based on K and the margin of victory multiplier
                shift = (k_value * mult) * (game['result1'] - game['my_prob1'])
                shift = (k_value * mult) * (game['result1'] - game['my_prob1'])

                # Apply shift
                team1['elo'] += shift
                team2['elo'] -= shift

        return games
