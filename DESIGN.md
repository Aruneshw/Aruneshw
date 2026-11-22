# Profile artwork

The layout and SVG renderer are adapted from
[Avi Vashishta's profile](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29),
reference commit `1cbb26eb40198d6164b7ccf34521e18bd7156da3`.
The supplied portrait, identity, project descriptions, links and contribution
data belong to Aruneshw's profile.

The design deliberately follows that reference: light paper panels, Instrument
Serif headings, blue contribution cells, animated blue/red/yellow tiles and
three linked repository cards. It uses GitHub-compatible standalone SVG images.

## Update

```sh
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
python scripts/fetch_profile.py
python scripts/render_portrait.py
python scripts/render_readme_cards.py
```

GitHub Actions requests a refresh every 15 minutes (minutes 7, 22, 37 and 52),
on generator changes, manually, or through a `profile-refresh`
repository-dispatch event. GitHub scheduling and image caching can delay
visibility; this is near-live rather than a streaming interface.
Contribution values are taken from GitHub's public contribution calendar;
they include contributions, not just commits. Current and longest streaks are
calculated within the returned rolling-year calendar using UTC dates.
All calendar months, including the partial boundary months, appear in the
activity chart so its bars sum to the yearly total.

Public repository counts, followers, stars, forks, project descriptions and
languages come from GitHub's REST API. Repository totals include owned public
forks. Null descriptions and languages are labeled rather than invented.
Static biography, portfolio and education text remain editorial content.
The graph shows when contribution data was successfully fetched in UTC.

No extra secret is needed: the workflow uses its built-in `github.token` for
API requests. Failed fetches or validation stop publication, retaining the
last successful cards; missing data is never replaced with made-up zeroes.
GitHub can disable scheduled workflows after 60 days of repository inactivity;
check the Actions tab and re-enable the workflow if this happens.

- Edit the name, introduction, feature tiles and repositories in
  `scripts/render_readme_cards.py`.
- Replace `assets/profile.png` to change the hero's ASCII portrait.
- Edit card links and accessible image descriptions in `README.md`.
- Font information is in `fonts/README.md`.
- Updating the hero portrait does not update the GitHub account avatar.
  That separate image can be uploaded in GitHub Settings → Public profile.
