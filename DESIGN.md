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
python scripts/render_portrait.py
python scripts/render_readme_cards.py
```

GitHub Actions refreshes artwork daily and can also be run manually.
Contribution values are taken from GitHub's public contribution calendar;
they include contributions, not just commits.

- Edit the name, introduction, feature tiles and repositories in
  `scripts/render_readme_cards.py`.
- Replace `assets/profile.png` to change the hero's ASCII portrait.
- Edit card links and accessible image descriptions in `README.md`.
- Font information is in `fonts/README.md`.
- Updating the hero portrait does not update the GitHub account avatar.
  That separate image can be uploaded in GitHub Settings → Public profile.
