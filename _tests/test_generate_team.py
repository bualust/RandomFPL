from randomfpl.fantasy_random import generate_team
import argparse
import asyncio


def test_generate_team():
    args = argparse.Namespace(
        max_expense=100,
        show_average=False,
        show_toprank=False,
        show_ext_info=False,
        veto_player=False,
        veto_teams=False,
    )
    team = asyncio.run(generate_team(args))
    assert team is not None
