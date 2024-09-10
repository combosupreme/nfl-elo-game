import csv
from datetime import datetime
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

class Util:

    @staticmethod
    def read_games(file):
        """ Initializes game objects from csv """
        games = [item for item in csv.DictReader(open(file))]
        current_season_year = datetime.now().year if datetime.now().month > 2 else datetime.now().year - 1
        file_latest = file.replace(".", f"_{current_season_year}.")

        # Uncommenting these two lines will grab the latest game results for this season, update team ratings accordingly, and make forecasts for upcoming games
        urlretrieve("https://raw.githubusercontent.com/Neil-Paine-1/NFL-elo-ratings/main/NFL-elo-ratings.csv", file_latest)
        games += [item for item in csv.DictReader(open(file_latest))]

        for game in games:
            game['season'], game['neutral'], game['playoff'] = int(game['season']), int(game['neutral']), str(game['playoff'])
            game['score1'], game['score2'] = int(game['score1']) if game['score1'] != 'NA' else None, int(game['score2']) if game['score2'] != 'NA' else None
            game['elo_prob1'] = float(game['elo_prob1']) if game['elo_prob1'] != 'NA' else None
            game['result1'] = float(game['is_win']) if game['is_win'] != 'NA' else None
        return games

    @staticmethod
    def evaluate_forecasts(games):
        """ Evaluates and scores forecasts in the my_prob1 field against those in the elo_prob1 field for each game """
        my_points_by_season, elo_points_by_season = {}, {}

        forecasted_games = [g for g in games if g['result1'] != None]
        upcoming_games = [g for g in games if g['result1'] == None and 'my_prob1' in g]

        # Evaluate forecasts and group by season
        for game in forecasted_games:

            # Skip unplayed games and ties
            if game['result1'] == None:
                continue

            if game['season'] not in elo_points_by_season:
                elo_points_by_season[game['season']] = 0.0
                my_points_by_season[game['season']] = 0.0

            # Calculate elo's points for game
            rounded_elo_prob = round(game['elo_prob1'], 2)
            elo_brier = (rounded_elo_prob - game['result1']) * (rounded_elo_prob - game['result1'])
            elo_points = 25 - (100 * elo_brier)
            elo_points = round(elo_points + 0.001 if elo_points < 0 else elo_points, 1) # Round half up
            if game['playoff'] not in ('NA', 0): #Changed from if game['playoff'] == 1: because the new data format uses 'NA' instead of 0 (Not a Playoff Game), and some other identifiers that dont fit this logic if it was a playoff game. 
                elo_points *= 2
            elo_points_by_season[game['season']] += elo_points

            # Calculate my points for game
            rounded_my_prob = round(game['my_prob1'], 2)
            my_brier = (rounded_my_prob - game['result1']) * (rounded_my_prob - game['result1'])
            my_points = 25 - (100 * my_brier)
            my_points = round(my_points + 0.001 if my_points < 0 else my_points, 1) # Round half up
            if game['playoff'] not in ('NA', 0):
                my_points *= 2
            my_points_by_season[game['season']] += my_points

        # Print individual seasons
        for season in my_points_by_season:
            print("In %s, your forecasts would have gotten %s points. Elo got %s points." % (season, round(my_points_by_season[season], 2), round(elo_points_by_season[season], 2)))

        # Show overall performance
        my_avg = sum(my_points_by_season.values())/len(my_points_by_season.values())
        elo_avg = sum(elo_points_by_season.values())/len(elo_points_by_season.values())
        print("\nOn average, your forecasts would have gotten %s points per season. Elo got %s points per season.\n" % (round(my_avg, 2), round(elo_avg, 2)))

        # Print forecasts for upcoming games
        if len(upcoming_games) > 0:
            print("Forecasts for this weeks upcoming games:")
            current_season_year = datetime.now().year if datetime.now().month > 2 else datetime.now().year - 1
            # Create a variable that looks for the current week, or next upcoming week if there are no games this week, ending Tuesday
            this_week = datetime.now().isocalendar()[1] if datetime.now().weekday() < 2 else datetime.now().isocalendar()[1] + 1
            print(f'Forcasting for games in week {int(this_week) - 35} of the {current_season_year} NFL season')
            
            for game in upcoming_games:
                if game['season'] == current_season_year:
                    #check if the matchup is before next monday
                    if datetime.strptime(game['date'], '%Y-%m-%d').isocalendar()[1] == this_week:
                        print("%s\t%s vs. %s\t\t%s%% (Elo)\t\t%s%% (You)" % (game['date'], game['team1'], game['team2'], int(round(100*game['elo_prob1'])), int(round(100*game['my_prob1']))))
                    #print("%s\t%s vs. %s\t\t%s%% (Elo)\t\t%s%% (You)" % (game['date'], game['team1'], game['team2'], int(round(100*game['elo_prob1'])), int(round(100*game['my_prob1']))))
            print("")
