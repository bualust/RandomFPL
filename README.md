[![codecov](https://codecov.io/gh/bualust/RandomFPL/branch/main/graph/badge.svg)](https://codecov.io/gh/bualust/RandomFPL)

# RandomFPL

A quick script to generate a pseudo-random Fantasy Premier League team.
Check the team of the day [here](https://bualust.github.io/RandomFPL/)

## Setup and Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
```
## Run
```bash
randomfpl
```

## Test website locally

Create a dummy team-of-day.md

```bash
mkdir _includes
echo "#This is where the team of the day will be!" > _includes/team-of-the-day.md
```

build website with bundle

```bash
bundle exec jekyll serve --port 4001
```

## Test actions locally

Using [act](https://nektosact.com/introduction.html)

Make sure Docker is running then simply
```bash
act
```
If you want to run it on one of the actions simply
```bash
act -W .github/workflows/action.yml
```
