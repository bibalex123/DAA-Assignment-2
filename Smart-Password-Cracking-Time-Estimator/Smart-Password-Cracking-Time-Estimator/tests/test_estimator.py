import unittest
from main import analyze_password, format_duration


class PasswordEstimatorTests(unittest.TestCase):
    def test_empty_password_rejected(self):
        with self.assertRaises(ValueError):
            analyze_password("")

    def test_lowercase_pool(self):
        result = analyze_password("abcd", 100)
        self.assertEqual(result["pool"], 26)
        self.assertTrue(result["categories"]["Lowercase letters"])
        self.assertFalse(result["categories"]["Digits"])

    def test_mixed_character_pool(self):
        result = analyze_password("Ab3!", 1000)
        self.assertEqual(result["pool"], 26 + 26 + 10 + 32)

    def test_rate_must_be_positive(self):
        with self.assertRaises(ValueError):
            analyze_password("abc", 0)

    def test_longer_password_has_more_entropy(self):
        short = analyze_password("abcd")
        long = analyze_password("abcdefgh")
        self.assertGreater(long["entropy_bits"], short["entropy_bits"])

    def test_duration_format(self):
        self.assertIn("second", format_duration(1))


if __name__ == "__main__":
    unittest.main()
