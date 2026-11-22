"""Shared HTTP client for fresh GitHub data, with bounded transient retries."""
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def github_session(authenticated=True):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Aruneshw-profile-art",
        "Accept": "application/vnd.github+json",
    })
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if authenticated and token:
        session.headers["Authorization"] = f"Bearer {token}"
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session
