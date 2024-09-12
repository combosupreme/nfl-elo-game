import argparse
from util import *
from forecast import *


def main():
    parser = argparse.ArgumentParser(description='NFL Elo Ratings')
    parser.add_argument('-u', '--get_updates', help='Update the CSV File for the most recent games', action='store_true', required=False)
    parser.add_argument('-s', '--show_this_weeks_games', help='Show the predictions for the upcoming games for the week', action='store_true', required=False)
    parser.add_argument('-k', '--k_value', help='Set the K value for the forecast', required=False)
    parser.add_argument('-hfa', '--hfa_value', help='Set the HFA value for the forecast', required=False)
    parser.add_argument('-r', '--revert_value', help='Set the revert value for the forecast', required=False)
    parser.add_argument('-c', '--condensed_version', help='Show a condensed version of the predictions', action='store_true', required=False)
    args = parser.parse_args()
    
    # if the user wants to add values for k, hfa, and revert to the forecast, get them from args and pass them to the forecast function, then set user_forecast_values to True
    user_forecast_values = False

    # Read historical games from CSV
    games = Util.read_games(args.get_updates)

    # Forecast every game
    Forecast.forecast(games, args.hfa_value, args.k_value, args.revert_value)

    # Evaluate our forecasts against Elo
    Util.evaluate_forecasts(games)
    
    if args.show_this_weeks_games:
        Util.show_this_weeks_games(games, user_forecast_values, args.condensed_version)

if __name__ == '__main__':
    main()