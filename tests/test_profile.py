"""Verify pagination, scope and failure handling for public GitHub statistics."""
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_profile import fetch_profile


def repo(name, stars, forks, private=False, owner="Aruneshw"):
    return {
        "name": name, "private": private, "owner": {"login": owner},
        "description": None, "language": None, "stargazers_count": stars,
        "forks_count": forks, "html_url": f"https://github.com/{owner}/{name}",
        "pushed_at": None, "archived": False, "fork": False,
    }


def response(data, next_url=None):
    result = MagicMock()
    result.json.return_value = data
    result.links = {"next": {"url": next_url}} if next_url else {}
    return result


class ProfileTests(unittest.TestCase):
    @patch("fetch_profile.github_session")
    def test_paginates_and_counts_only_owned_public_repos(self, factory):
        session = factory.return_value.__enter__.return_value
        session.get.side_effect = [
            response({"login": "Aruneshw", "followers": 6, "following": 3}),
            response([repo("first", 2, 1)], "https://api.github.com/page2"),
            response([
                repo("second", 0, 3),
                repo("private", 100, 100, private=True),
                repo("someone-elses", 100, 100, owner="someone-else"),
            ]),
        ]
        data = fetch_profile()
        self.assertEqual(session.get.call_count, 3)
        self.assertEqual(data["public_repos"], 2)
        self.assertEqual(data["total_stars"], 2)
        self.assertEqual(data["total_forks"], 4)
        self.assertIsNone(data["repositories"]["first"]["description"])
        self.assertEqual(data["repositories"]["second"]["stars"], 0)

    @patch("fetch_profile.github_session")
    def test_api_failure_is_not_published_as_zero(self, factory):
        session = factory.return_value.__enter__.return_value
        failed = response({})
        failed.raise_for_status.side_effect = requests.HTTPError("API unavailable")
        session.get.return_value = failed
        with self.assertRaises(requests.HTTPError):
            fetch_profile()


if __name__ == "__main__":
    unittest.main()
