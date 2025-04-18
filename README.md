<img src="https://videos.openai.com/vg-assets/assets%2Ftask_01js4rq9gvfg4r3mmjtdb0dtkt%2Fimg_0.webp?st=2025-04-18T14%3A23%3A14Z&se=2025-04-24T15%3A23%3A14Z&sks=b&skt=2025-04-18T14%3A23%3A14Z&ske=2025-04-24T15%3A23%3A14Z&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skoid=3d249c53-07fa-4ba4-9b65-0bf8eb4ea46a&skv=2019-02-02&sv=2018-11-09&sr=b&sp=r&spr=https%2Chttp&sig=sJbMtxdr6fPE5nGwEjn8tMu%2BL2FP2F2B4hctsePivIQ%3D&az=oaivgprodscus" alt="logo" width="120"/>

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/bualust/RandomFPL/branch/main/graph/badge.svg)](https://codecov.io/gh/bualust/RandomFPL)
![PageDeployment](https://github.com/bualust/RandomFPL/actions/workflows/jekyll-gh-pages.yml/badge.svg)

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
