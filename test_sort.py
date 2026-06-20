import unittest
from sort import sort_v1


class TestSortV1(unittest.TestCase):

    def test_typical(self):
        data = [3, 4, 1, 5]
        sort_v1(data)
        self.assertEqual(data, [1, 3, 4, 5])

    def test_already_sorted(self):
        data = [1, 2, 3, 4]
        sort_v1(data)
        self.assertEqual(data, [1, 2, 3, 4])

    def test_reverse_sorted(self):
        data = [5, 4, 3, 2, 1]
        sort_v1(data)
        self.assertEqual(data, [1, 2, 3, 4, 5])

    def test_duplicates(self):
        data = [3, 1, 2, 1, 3]
        sort_v1(data)
        self.assertEqual(data, [1, 1, 2, 3, 3])

    def test_single_element(self):
        data = [42]
        sort_v1(data)
        self.assertEqual(data, [42])

    def test_empty(self):
        data = []
        sort_v1(data)
        self.assertEqual(data, [])

    def test_negative_numbers(self):
        data = [0, -1, 3, -5, 2]
        sort_v1(data)
        self.assertEqual(data, [-5, -1, 0, 2, 3])

    def test_key_function(self):
        data = [["3", "alice"], ["1", "bob"], ["2", "carol"]]
        sort_v1(data, key=lambda row: int(row[0]))
        self.assertEqual(data, [["1", "bob"], ["2", "carol"], ["3", "alice"]])

    def test_key_reverse_string(self):
        data = ["banana", "apple", "cherry"]
        sort_v1(data, key=lambda s: s[-1])  # sort by last character
        self.assertEqual(data, ["banana", "apple", "cherry"])

    def test_key_duplicate_keys(self):
        data = [["2", "alice"], ["1", "bob"], ["2", "carol"], ["1", "dave"]]
        sort_v1(data, key=lambda row: int(row[0]))
        keys = [int(row[0]) for row in data]
        self.assertEqual(keys, [1, 1, 2, 2])

    def test_key_already_sorted(self):
        data = [["1", "alice"], ["2", "bob"], ["3", "carol"]]
        sort_v1(data, key=lambda row: int(row[0]))
        self.assertEqual(data, [["1", "alice"], ["2", "bob"], ["3", "carol"]])

    def test_key_reverse_sorted(self):
        data = [["3", "alice"], ["2", "bob"], ["1", "carol"]]
        sort_v1(data, key=lambda row: int(row[0]))
        self.assertEqual(data, [["1", "carol"], ["2", "bob"], ["3", "alice"]])


if __name__ == "__main__":
    unittest.main()
