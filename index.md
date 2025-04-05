---
layout: default
---

This code generates a pseudo-random team for the Fantasy Premier League
It makes use of the [FPL API](https://fpl.readthedocs.io/en/latest/) to generate a team removing all the players who are injured or suspended and mazimising the total amount of money spent.

In the latest version it also allows to remove specific players, for example I found useful to see the algorithm response applying a veto on Haaland at the end of the 2023-2024 season, when it was considered a big risk!

# Generate FPL team locally

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
```

## Run

```bash
randomfpl
```

{% include team-of-the-day.md %}
