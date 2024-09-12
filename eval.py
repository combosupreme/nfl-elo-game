import argparse
import argparse
from util import *
from forecast import *
from fractions import Fraction

def main():
    parser = argparse.ArgumentParser(description='NFL Elo Ratings')
    parser.add_argument('-u', '--get_updates', help='Update the CSV File for the most recent games', action='store_true', required=False)
    parser.add_argument('-k', '--k_value', help='Set the K value for the forecast', required=False)
    parser.add_argument('-hfa', '--hfa_value', help='Set the HFA value for the forecast', required=False)
    parser.add_argument('-r', '--revert_value', help='Set the revert value for the forecast in float or fraction type. Example is .33 or 1/3', required=False)
    parser.add_argument('-c', '--condensed_version', help='Show a condensed version of the predictions', action='store_true', required=False)
    parser.add_argument('-ds', '--dont_show_this_weeks_games', help='Dont show the predictions, only the Brier Score', action='store_false', required=False)
    args = parser.parse_args()
    
    # if the user wants to add values for k, hfa, and revert to the forecast, get them from args and pass them to the forecast function, then set user_forecast_values to True
    if args.k_value:
        args.k_value = float(args.k_value)
    if args.hfa_value:
        args.hfa_value = float(args.hfa_value)
    if args.revert_value:
        try:
            args.revert_value = float(args.revert_value)
        except ValueError:
            args.revert_value = Fraction(args.revert_value)
    if args.k_value or args.hfa_value or args.revert_value:
        user_forecast_values = True
    else:
        user_forecast_values = False
    

    # Read historical games from CSV
    games = Util.read_games(args.get_updates)
    # Read historical games from CSV
    games = Util.read_games(args.get_updates)

    # Forecast every game
    Forecast.forecast(games, args.hfa_value, args.k_value,)

    # Evaluate our forecasts against Elo
    Util.evaluate_forecasts(games)
    
    if args.dont_show_this_weeks_games:
        Util.show_this_weeks_games(games, user_forecast_values, args.condensed_version)

if __name__ == '__main__':
    main()