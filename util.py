import csv
from datetime import datetime, timedelta
from urllib.request import urlretrieve

# Constants
DATE_FORMAT = '%Y-%m-%d'
WEEKDAY_THRESHOLD = 0  # Monday
CURRENT_SEASON_YEAR = datetime.now().year if datetime.now().month > 2 else datetime.now().year - 1
THIS_NFL_WEEK = datetime.now().isocalendar()[1] if datetime.now().weekday() > WEEKDAY_THRESHOLD else datetime.now().isocalendar()[1] - 1
SENDER_EMAIL_ADDRESS = None
SMTP_SERVER_URL = None
from datetime import datetime, timedelta
from urllib.request import urlretrieve

# Constants
DATE_FORMAT = '%Y-%m-%d'
WEEKDAY_THRESHOLD = 0  # Monday
CURRENT_SEASON_YEAR = datetime.now().year if datetime.now().month > 2 else datetime.now().year - 1
THIS_NFL_WEEK = datetime.now().isocalendar()[1] if datetime.now().weekday() > WEEKDAY_THRESHOLD else datetime.now().isocalendar()[1] - 1
SENDER_EMAIL_ADDRESS = None
SMTP_SERVER_URL = None

class Util:
    @staticmethod
    def is_game_in_this_week(game_date_str: str) -> bool:
        game_date = datetime.strptime(game_date_str, DATE_FORMAT)
        game_date_week = game_date.isocalendar()[1]
        game_date_weekday = game_date.weekday()
        
        if game_date_weekday <= WEEKDAY_THRESHOLD:
            game_date_week -= 1

        return game_date_week == THIS_NFL_WEEK

    @staticmethod
    def group_predictions_by_matchup(predictions: list) -> dict:
        # Initialize a dictionary to store games by matchup
        matchups = {}
        for game in predictions:
            # Store the game in the matchups dictionary
            matchup_key = f"{game['team1']} vs. {game['team2']} - {game['date']}"
            reversed_matchup_key = f"{game['team2']} vs. {game['team1']} - {game['date']}"
            
            
            if (matchup_key not in matchups) and (reversed_matchup_key not in matchups):
                matchups[matchup_key] = [game]
            # Verify if the matchup is already in the dictionary
            elif reversed_matchup_key in matchups:
                matchups[reversed_matchup_key].append(game)
        return matchups
            
    @staticmethod
    def is_game_in_this_week(game_date_str: str) -> bool:
        game_date = datetime.strptime(game_date_str, DATE_FORMAT)
        game_date_week = game_date.isocalendar()[1]
        game_date_weekday = game_date.weekday()
        
        if game_date_weekday <= WEEKDAY_THRESHOLD:
            game_date_week -= 1

        return game_date_week == THIS_NFL_WEEK

    @staticmethod
    def group_predictions_by_matchup(predictions: list) -> dict:
        # Initialize a dictionary to store games by matchup
        matchups = {}
        for game in predictions:
            # Store the game in the matchups dictionary
            matchup_key = f"{game['team1']} vs. {game['team2']} - {game['date']}"
            reversed_matchup_key = f"{game['team2']} vs. {game['team1']} - {game['date']}"
            
            
            if (matchup_key not in matchups) and (reversed_matchup_key not in matchups):
                matchups[matchup_key] = [game]
            # Verify if the matchup is already in the dictionary
            elif reversed_matchup_key in matchups:
                matchups[reversed_matchup_key].append(game)
        return matchups
            
    @staticmethod
    def read_games(get_updates: bool) -> list:
    def read_games(get_updates: bool) -> list:
        """ Initializes game objects from csv """
        current_season_year = datetime.now().year if datetime.now().month > 2 else datetime.now().year - 1
        file = f"NP_data/nfl_games_{current_season_year}.csv"
        if get_updates:
            print("Updating the CSV file for the most recent games...")
            urlretrieve("https://raw.githubusercontent.com/Neil-Paine-1/NFL-elo-ratings/main/NFL-elo-ratings.csv", file)
        games = [item for item in csv.DictReader(open(file))]
        file = f"NP_data/nfl_games_{current_season_year}.csv"
        if get_updates:
            print("Updating the CSV file for the most recent games...")
            urlretrieve("https://raw.githubusercontent.com/Neil-Paine-1/NFL-elo-ratings/main/NFL-elo-ratings.csv", file)
        games = [item for item in csv.DictReader(open(file))]

        for game in games:
            game['season'], game['neutral'], game['playoff'] = int(game['season']), int(game['neutral']), str(game['playoff'])
            game['score1'], game['score2'] = int(game['score1']) if game['score1'] != 'NA' else None, int(game['score2']) if game['score2'] != 'NA' else None
            game['elo_prob1'] = float(game['elo_prob1']) if game['elo_prob1'] != 'NA' else None
            game['result1'] = float(game['is_win']) if game['is_win'] != 'NA' else None
            
            
        return games

    @staticmethod
    def evaluate_forecasts(games: list, filter_to_home_team: bool = False) -> dict:
    def evaluate_forecasts(games: list, filter_to_home_team: bool = False) -> dict:
        """ Evaluates and scores forecasts in the my_prob1 field against those in the elo_prob1 field for each game """
        my_points_by_season, elo_points_by_season = {}, {}

        # # Filter games to exclude the line if the team is away
        if filter_to_home_team:
            games = [game for game in games if game['is_home'] == '1']
        # # Filter games to exclude the line if the team is away
        if filter_to_home_team:
            games = [game for game in games if game['is_home'] == '1']
        forecasted_games = [g for g in games if g['result1'] != None]

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

        # Show overall performance
        my_avg = sum(my_points_by_season.values())/len(my_points_by_season.values())
        elo_avg = sum(elo_points_by_season.values())/len(elo_points_by_season.values())
        print("\nOn average, the adjusted forecasts had a Brier Score of %s points per season. Elo got %s points per season.\n" % (round(my_avg, 2), round(elo_avg, 2)))
        return my_points_by_season, elo_points_by_season
        print("\nOn average, the adjusted forecasts had a Brier Score of %s points per season. Elo got %s points per season.\n" % (round(my_avg, 2), round(elo_avg, 2)))
        return my_points_by_season, elo_points_by_season

    @staticmethod
    def show_this_weeks_games(games: list[dict], user_forecast_values: bool = False, condensed_version:bool = False, skip_print:bool = False) -> str:
        """ Prints forecasts for upcoming games and returns the same as a string """
        result_str = ""
        upcoming_games = [g for g in games if g['result1'] is None and 'my_prob1' in g]
    @staticmethod
    def show_this_weeks_games(games: list[dict], user_forecast_values: bool = False, condensed_version:bool = False, skip_print:bool = False) -> str:
        """ Prints forecasts for upcoming games and returns the same as a string """
        result_str = ""
        upcoming_games = [g for g in games if g['result1'] is None and 'my_prob1' in g]
        if len(upcoming_games) > 0:
            if user_forecast_values:
                my_prob_label = "You"
            else:
                my_prob_label = "FiveThirtyEight"
            matchups = Util.group_predictions_by_matchup(games)
            if len(matchups) > 0:
                result_str += f'Forecasting Matchups in week {int(THIS_NFL_WEEK) - 35} of the {CURRENT_SEASON_YEAR} NFL season...\n'
                header = f'Matchup\t\tDate\t\tHome\tElo Prediction\t{"Your" if user_forecast_values else "FiveThirtyEight"} Prediction\t\tAway\tElo Prediction\t{"Your" if user_forecast_values else "FiveThirtyEight"} Prediction\n'
                result_str += f'{header}'
                game_dates = Util.this_nfl_week_dates()
                for date in game_dates:
                    for matchup in matchups.keys():
                        if date in matchup:
                            if not condensed_version:
                                result_str += f"\n\t\t\t{matchup}\n"
                                result_str += f"\t\t\t{'-'*len(matchup)}\n"
                                
                            if condensed_version:
                                current_year_str = f'- {CURRENT_SEASON_YEAR}'
                                matchup_str = str(matchup).replace('vs.', '\t@').replace(current_year_str, f'\t{CURRENT_SEASON_YEAR}')
                                home_team = matchups[matchup][0]['team1'] if matchups[matchup][0]['is_home'] == '1' else matchups[matchup][0]['team2']
                                away_team = matchups[matchup][0]['team1'] if matchups[matchup][0]['is_home'] != '1' else matchups[matchup][0]['team2']
                                home_elo_prob = int(round(100*matchups[matchup][0]['elo_prob1'])) if matchups[matchup][0]['is_home'] == '1' else int(round(100*matchups[matchup][1]['elo_prob1']))
                                away_elo_prob = int(round(100*matchups[matchup][0]['elo_prob1'])) if matchups[matchup][0]['is_home'] != '1' else int(round(100*matchups[matchup][1]['elo_prob1']))
                                home_my_prob = int(round(100*matchups[matchup][0]['my_prob1'])) if matchups[matchup][0]['is_home'] == '1' else int(round(100*matchups[matchup][1]['my_prob1']))
                                away_my_prob = int(round(100*matchups[matchup][0]['my_prob1'])) if matchups[matchup][0]['is_home'] != '1' else int(round(100*matchups[matchup][1]['my_prob1']))
                                result_str += f"{matchup_str}\t{home_team}:\t{home_elo_prob}% (Elo)\t{home_my_prob}% ({my_prob_label})\t\t|\t{away_team}:\t{away_elo_prob}% (Elo)\t{away_my_prob}% ({my_prob_label})\n"
                            else:
                                for prediction in matchups[matchup]:
                                    result_str += f"{prediction['date']}\t{prediction['team1']}\t\t{int(round(100*prediction['elo_prob1']))}% (Elo)\t\t{int(round(100*prediction['my_prob1']))}% ({my_prob_label})\n"
        else:
            result_str += "No upcoming games to forecast\n"
        
        if not skip_print:
            print(result_str)
        return result_str
            
    @staticmethod
    def email_this_weeks_games(games: list[dict], email_address:str, filter_to_home_team: bool = False, user_forecast_values: bool = False):
        if not SMTP_SERVER_URL:
            print("SMTP_SERVER_URL is not set. Please set it to the URL of your SMTP server.")
            return
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Copy the show_this_weeks_games function and modify it to return a string instead of printing
        def get_this_weeks_games(games: list[dict], filter_to_home_team: bool = False, user_forecast_values: bool = False) -> str:
            upcoming_games = [g for g in games if g['result1'] == None and 'my_prob1' in g]
            if len(upcoming_games) > 0:
                if user_forecast_values:
                    my_prob_label = "You"
                else:
                    my_prob_label = "FiveThirtyEight"
                matchups = Util.group_predictions_by_matchup(games)
                if len(matchups) > 0:
                    games_str = f'Forcasting for games in week {int(THIS_NFL_WEEK) - 35} of the {CURRENT_SEASON_YEAR} NFL season...\n'
                    games_str += f'Date\t\tTeam\t\tElo Prediction\t\t{"Your" if user_forecast_values else "FiveThirtyEight"} Prediction\n'
                    if filter_to_home_team:
                        games_str += 'Only showing forecasts for home teams\n'
                    game_dates = Util.this_nfl_week_dates()
                    for date in game_dates:
                        for matchup in matchups.keys():
                            if date in matchup:
                                games_str += f"\n\t\t\t{matchup}\n"
                                games_str += f"\t\t\t{'-'*len(matchup)}\n"
                                for prediction in matchups[matchup]:
                                    if filter_to_home_team and prediction['is_home'] != '1':
                                        continue
                                    games_str += f"{prediction['date']}\t{prediction['team1']}\t\t{int(round(100*prediction['elo_prob1']))}% (Elo)\t\t{int(round(100*prediction['my_prob1']))}% ({my_prob_label})\n"
                    return games_str
            else:
                return "No upcoming games to forecast"
        
        games_str = get_this_weeks_games(games, filter_to_home_team, user_forecast_values)
        
        # Email the games
        # Send from the SENDER_EMAIL_ADDRESS if it is set, otherwise send from the email_address the user entered
        sender_email = SENDER_EMAIL_ADDRESS if SENDER_EMAIL_ADDRESS else email_address
        receiver_email = email_address
        
        # Create the email content
        subject = "This Week's NFL Games Forecast"
        body = games_str

        # Create the MIME structure
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
            with smtplib.SMTP(SMTP_SERVER_URL, 587) as server:  # Replace 'smtp.example.com' with your SMTP server
                server.starttls()
                server.login(sender_email, 'your_password')  # Replace 'your_password' with the actual password
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print(f"Email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")       
    
    @staticmethod
    def this_nfl_week_dates() -> list:
        """ Returns the dates of the current NFL week """
        start_date = datetime.strptime(f"{CURRENT_SEASON_YEAR}-W{THIS_NFL_WEEK}-1", "%Y-W%W-%w") + timedelta(days=1)
        return [(start_date + timedelta(n)).strftime('%Y-%m-%d') for n in range(7)]
            
        