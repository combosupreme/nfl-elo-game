import argparse
from .util import *
from .forecast import *
from fractions import Fraction


def call_predictor(get_updates: bool, k_value: float, hfa_value: float, revert_value: float, condensed_version: bool, dont_show_this_weeks_games: bool) -> dict:
    # Read historical games from CSV
    games = Util.read_games(get_updates)

    # Forecast every game
    forecasted_games = Forecast.forecast(games, hfa_value, k_value,)

    # Evaluate our forecasts against Elo
    my_points_by_season, elo_points_by_season = Util.evaluate_forecasts(forecasted_games)
    
    
    upcoming_games = Util.get_upcoming_games(forecasted_games)
            
    return_dict = {
        "forecasted_games": forecasted_games,
        "my_points_by_season": my_points_by_season,
        "elo_points_by_season": elo_points_by_season,
        "upcoming_games": upcoming_games,
        }
        
    return return_dict
    
def main():
    parser = argparse.ArgumentParser(description='NFL Elo Ratings')
    parser.add_argument('-u', '--get_updates', help='Update the CSV File for the most recent games', action='store_true', required=False)
    parser.add_argument('-k', '--k_value', help='Set the K value for the forecast', required=False)
    parser.add_argument('-hfa', '--hfa_value', help='Set the HFA value for the forecast', required=False)
    parser.add_argument('-r', '--revert_value', help='Set the revert value for the forecast in float or fraction type. Example is .33 or 1/3', required=False)
    parser.add_argument('-c', '--condensed_version', help='Show a condensed version of the predictions', action='store_true', required=False)
    parser.add_argument('-ds', '--dont_show_this_weeks_games', help='Dont show the predictions, only the Brier Score', action='store_true', required=False)
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
    result_dict = call_predictor(args.get_updates, args.k_value, args.hfa_value, args.revert_value, args.condensed_version, args.dont_show_this_weeks_games)
    
    # Print the results
    forecasted_games = result_dict['forecasted_games']
    
    if not args.dont_show_this_weeks_games:
        results_str = Util.show_this_weeks_games(forecasted_games, user_forecast_values, args.condensed_version)

if __name__ == '__main__':
    main()