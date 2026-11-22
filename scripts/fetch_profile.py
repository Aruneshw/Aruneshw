#!/usr/bin/env python3
"""Fetch public profile and repository metadata directly from GitHub's REST API."""
import datetime
import json
import os
from pathlib import Path

from github_data import github_session

USERNAME = os.environ.get("GH_PROFILE_USER", "Aruneshw")
OUT = Path(__file__).resolve().parent.parent / "data/profile.json"


def fetch_profile():
    with github_session() as session:
        response = session.get(f"https://api.github.com/users/{USERNAME}", timeout=30)
        response.raise_for_status()
        user = response.json()
        if user["login"].lower() != USERNAME.lower():
            raise ValueError("GitHub returned a different profile")

        repos = []
        url = f"https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100"
        while url:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            repos.extend(response.json())
            url = response.links.get("next", {}).get("url")

    public = [
        repo for repo in repos
        if not repo["private"] and repo["owner"]["login"].lower() == USERNAME.lower()
    ]
    return {
        "username": user["login"],
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": f"https://api.github.com/users/{USERNAME}",
        "public_repos": len(public),
        "followers": user["followers"],
        "following": user["following"],
        "total_stars": sum(repo["stargazers_count"] for repo in public),
        "total_forks": sum(repo["forks_count"] for repo in public),
        "repositories": {
            repo["name"]: {
                "name": repo["name"],
                "description": repo["description"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "url": repo["html_url"],
                "pushed_at": repo["pushed_at"],
                "archived": repo["archived"],
                "fork": repo["fork"],
            }
            for repo in sorted(public, key=lambda repo: repo["name"].lower())
        },
    }


if __name__ == "__main__":
    data = fetch_profile()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Fetched {data['public_repos']} public repositories, "
          f"{data['followers']} followers, {data['total_stars']} stars.")
