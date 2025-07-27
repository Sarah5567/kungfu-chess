# import unittest
# from Score import Score
# from EventBus import Event
#
# class TestScore(unittest.TestCase):
#     def setUp(self):
#         self.score = Score()
#
#     def test_update_score_white(self):
#         event = Event('capture'{'captured_piece': ['Q', 'W'], 'capture_piece': ['Q', 'B']})
#         self.score.update_score(event)
#         self.assertEqual(self.score.score_white, self.score.piece_score['Q'])
#         self.assertEqual(self.score.score_black, 0)
#
#     def test_update_score_black(self):
#         event = Event({'captured_piece': ['R', 'B'], 'capture_piece': ['R', 'B']})
#         self.score.update_score(event)
#         self.assertEqual(self.score.score_black, self.score.piece_score['R'])
#         self.assertEqual(self.score.score_white, 0)
#
#     def test_update_score_multiple(self):
#         event1 = Event({'captured_piece': ['N', 'W'], 'capture_piece': ['N', 'W']})
#         event2 = Event({'captured_piece': ['B', 'B'], 'capture_piece': ['B', 'B']})
#         self.score.update_score(event1)
#         self.score.update_score(event2)
#         self.assertEqual(self.score.score_white, self.score.piece_score['N'])
#         self.assertEqual(self.score.score_black, self.score.piece_score['B'])
#
# if __name__ == "__main__":
#     unittest.main()
#
