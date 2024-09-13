import unittest
from datetime import datetime, timedelta
from util import Util

class UtilTests(unittest.TestCase):
    def test_is_game_in_this_week(self):
        # Test case 1: Game date is in the current week and after the weekday threshold
        game_date_str = datetime.now().strftime('%Y-%m-%d')
        self.assertTrue(Util.is_game_in_this_week(game_date_str))

        # Test case 2: Game date is in the current week but before the weekday threshold
        today_day_of_week = datetime.now().weekday()
        days_to_subtract = today_day_of_week + 1
        game_date_str = (datetime.now() - timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')
        self.assertFalse(Util.is_game_in_this_week(game_date_str))

        # Test case 3: Game date is in the next week and before the weekday threshold
        today_day_of_week = datetime.now().weekday()
        days_to_add = 7 - today_day_of_week
        game_date_str = (datetime.now() + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
        print(game_date_str)
        self.assertTrue(Util.is_game_in_this_week(game_date_str))

        # Test case 4: Game date is in the next week but after the weekday threshold
        game_date_str = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        self.assertFalse(Util.is_game_in_this_week(game_date_str))

    def test_read_games(self):
        # Test case 1: Reading games from CSV file
        games = Util.read_games(get_updates=False)
        self.assertIsInstance(games, list)
        self.assertGreater(len(games), 0)
        

if __name__ == '__main__':
    unittest.main()