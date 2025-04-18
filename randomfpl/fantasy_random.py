import asyncio
import aiohttp
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from fpl import FPL
from datetime import date
import argparse
import pandas as pd


def main():
    """`main` function for RandomFPL module"""
    args = parse_args()
    asyncio.run(generate_team(args))


def parse_args():
    """'parse_args' returns parser.parse_args()"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--show_average",
        required=False,
        action="store_true",
        help="Show average stats of PL players",
    )
    parser.add_argument(
        "--show_toprank",
        required=False,
        action="store_true",
        help="Show top rank PL players",
    )
    parser.add_argument(
        "--show_ext_info",
        required=False,
        action="store_true",
        help="Show more player info in table",
    )
    parser.add_argument(
        "--max_expense",
        required=False,
        default=100,
        type=float,
        help="Available budget",
    )
    parser.add_argument(
        "--veto_player",
        required=False,
        type=str,
        help="Specify SURNAME of one player vetoed from entering the team",
    )
    parser.add_argument(
        "--veto_teams",
        required=False,
        nargs="+",
        type=int,
        help="List of teams you want to veto (for blank GWs)",
    )

    args = parser.parse_args()
    return args


async def generate_team(args):
    """`generate_team` Read PL players from website and gives you a random team"""

    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()

    df = pandas_df_players(players)
    df = select_only_active(args, df)
    max_minutes = max(df["Minutes"])
    df = df[df["Minutes"] > max_minutes * 0.5]
    df.to_csv("Output.csv", index=False)

    av_g_f, av_a_m, av_g_c = print_average_quantities(df, args.show_average)
    random_team = get_random_team(df, True, df, av_g_f, av_a_m, av_g_c)
    random_team = maximise_expense(args, random_team, df, av_g_f, av_a_m, av_g_c)

    print(f"Team generated on {date.today()}\n")
    print(
        f"Total expense is {sum(random_team['Price'])} out of a total budget of {args.max_expense}\n"
    )
    if args.veto_player:
        print(f"Vetoed player is: {args.veto_player}\n")
    if args.veto_teams:
        print(f"Vetoed teams are: {args.veto_teams}\n")

    print_pretty_table(args, random_team)

    to_plot = {
        "GP90": "Number of goals scored per 90mins played",
        "AP90": "Number of assists per 90mins played",
        "GCP90": "Number of goals conceded per 90mins played",
    }
    for plot, title in to_plot.items():
        fig, ax = plt.subplots()
        max_val = float(max(df[plot]))
        min_val = float(min(df[plot]))
        number_of_bins = 10
        if plot == "GCP90":
            number_of_bins = 20
        edges = (max_val - min_val) / number_of_bins
        bins = []
        i = 0
        while i <= number_of_bins:
            bins.append(min_val + i * edges)
            i = i + 1
        # plt.hist(df[plot], histtype='step', label="All players", density=True, bins=bins)
        forwards = df[df["Position"] == 4]
        if plot != "GCP90":
            plt.hist(
                forwards[plot],
                histtype="step",
                label="Forwards",
                density=True,
                bins=bins,
            )
        midfields = df[df["Position"] == 3]
        if plot != "GCP90":
            plt.hist(
                midfields[plot],
                histtype="step",
                label="Midfielders",
                density=True,
                bins=bins,
            )
        defenders = df[df["Position"] == 2]
        if plot == "GCP90":
            plt.hist(
                defenders[plot],
                histtype="step",
                label="Defenders",
                density=True,
                bins=bins,
            )
        plt.hist(
            random_team[plot],
            histtype="step",
            label="Random Penguins",
            density=False,
            bins=bins,
        )
        ax.legend()
        plt.xlabel(to_plot[plot])
        plt.savefig(plot + ".png")
    df_maxgoals = df.loc[df["GP90"].idxmax()]
    df_maxassists = df.loc[df["AP90"].idxmax()]
    df_mingoalscon = df.loc[df["GCP90"].idxmin()]
    if args.show_toprank:
        print(
            "\n Max number of goals\n",
            df_maxgoals,
            "\nMax number of assists\n",
            df_maxassists,
            "\nMin number of goals conceded\n",
            df_mingoalscon,
        )

    return random_team


def print_average_quantities(df, show):
    """`print_average_quantities` prints average goals and assists"""
    forwards = df[df["Position"] == 4]
    midfielders = df[df["Position"] == 3]
    defender = df[df["Position"] == 2]
    av_g_f = sum(forwards["GP90"]) / len(forwards)
    av_g_m = sum(midfielders["GP90"]) / len(midfielders)
    av_a_f = sum(forwards["AP90"]) / len(forwards)
    av_a_m = sum(midfielders["AP90"]) / len(midfielders)
    av_g_c = sum(defender["GCP90"]) / len(defender)
    if show is True:
        print("==========================")
        print("90/mins rescaled")
        print("Average Goals Forwards", av_g_f)
        print("Average Goals Midfielders", av_g_m)
        print("Average Assists Forwards", av_a_f)
        print("Average Assists Midfielders", av_a_m)
        print("Average Goals conceded defenders", av_g_c)
        print("==========================\n")

    return av_g_f, av_a_m, av_g_c


def select_only_active(args, df):
    """`select_only_active` removes injured and suspended players"""
    df = df[df["Status"] == "a"]
    df = df[df["Minutes"] != 0]
    if args.veto_player:
        df = df[df["Name"] != args.veto_player]
    if args.veto_teams:
        df = df[~df["Team"].isin(args.veto_teams)]
    return df


def pandas_df_players(players):
    """`pandas_df_players` creates pandas dataframe of players"""

    names = []
    price = []
    position = []
    status = []
    minutes = []
    goals = []
    gp90 = []
    assist = []
    ap90 = []
    goals_conc = []
    gcp90 = []
    team = []
    for player in players:
        names.append(player.web_name)
        price.append(float(player.now_cost / 10))
        position.append(int(player.element_type))
        status.append((player.status))
        minutes.append(int(player.minutes))
        goals.append(int(player.goals_scored))
        goals_conc.append(int(player.goals_conceded))
        assist.append(int(player.assists))
        team.append(player.team)
        if int(player.minutes) > 0:
            gp90.append(round(int(player.goals_scored) * 90 / int(player.minutes), 2))
            ap90.append(round(int(player.assists) * 90 / int(player.minutes), 2))
            gcp90.append(
                round(int(player.goals_conceded) * 90 / int(player.minutes), 2)
            )
        else:
            gp90.append(-99)
            ap90.append(-99)
            gcp90.append(-99)

    df = pd.DataFrame(
        {
            "Name": names,
            "Price": price,
            "Position": position,
            "Team": team,
            "Status": status,
            "Minutes": minutes,
            "Goals": goals,
            "GP90": gp90,
            "Assists": assist,
            "AP90": ap90,
            "Goals Conceded": goals_conc,
            "GCP90": gcp90,
        }
    )

    return df


def get_random_team(df, isFirstAttempt, random_team, av_g_f, av_a_m, av_g_c):
    """`get_random_team` generates a random team from pandasDF"""

    goal_keepers = df[df["Position"] == 1]
    defenders = df[df["Position"] == 2]
    midfielders = df[df["Position"] == 3]
    forwards = df[df["Position"] == 4]

    if isFirstAttempt is True:
        random_GKPs = goal_keepers.sample(2)
        random_DEF = defenders.sample(5)
        random_MID = midfielders.sample(5)
        random_FWD = forwards.sample(3)
        random_team = pd.concat([random_GKPs, random_DEF, random_MID, random_FWD])
    else:
        removed_player, new_member = substituion(
            random_team, df, av_g_f, av_a_m, av_g_c
        )
        player_loc = removed_player.head().index.values
        random_team = random_team.drop(index=player_loc, axis=1)
        random_team = pd.concat([random_team, new_member])

    return random_team


def select_new_candidates(random_team, df, av_g_f, av_a_m, av_g_c):
    """`select_new_candidates`removes one player randomly from team and substitues
    with a player of same position but more expensive"""

    extracted_player = random_team.sample(1)
    removed_position = int(extracted_player.iloc[0]["Position"])
    removed_price = float(extracted_player.iloc[0]["Price"])
    removed_gp90 = float(extracted_player.iloc[0]["GP90"])
    removed_ap90 = float(extracted_player.iloc[0]["AP90"])
    removed_gcp90 = float(extracted_player.iloc[0]["GCP90"])
    new_candidates = df[df["Position"] == removed_position]
    new_candidates = new_candidates[new_candidates["Price"] != removed_price]
    new_candidates = new_candidates[new_candidates["Price"] > removed_price]
    if new_candidates.empty:
        return extracted_player, extracted_player
    if removed_position == 4:
        new_candidates = new_candidates[new_candidates["GP90"] > removed_gp90]
        new_candidates = new_candidates[new_candidates["GP90"] > av_g_f]
        new_candidates = new_candidates[new_candidates["AP90"] > removed_ap90]
        new_candidates = new_candidates[new_candidates["AP90"] > av_a_m]
    elif removed_position == 3:
        new_candidates = new_candidates[new_candidates["GCP90"] < removed_gcp90]
        new_candidates = new_candidates[new_candidates["GCP90"] < av_g_c]
        new_candidates = new_candidates[new_candidates["AP90"] > removed_ap90]
        new_candidates = new_candidates[new_candidates["AP90"] > av_a_m]
    elif removed_position == 2:
        new_candidates = new_candidates[new_candidates["GCP90"] < removed_gcp90]
        new_candidates = new_candidates[new_candidates["GCP90"] < av_g_c]
        new_candidates = new_candidates[new_candidates["AP90"] > removed_ap90]
        new_candidates = new_candidates[new_candidates["AP90"] > av_a_m]

    return extracted_player, new_candidates


def substituion(random_team, df, av_g_f, av_a_m, av_g_c):
    """`substituion` there might be sometimes no candidate to make substitution
    select a new player to remove"""

    extracted_player, new_candidates = select_new_candidates(
        random_team, df, av_g_f, av_a_m, av_g_c
    )
    while new_candidates.empty:
        extracted_player, new_candidates = select_new_candidates(
            random_team, df, av_g_f, av_a_m, av_g_c
        )

    new_member = new_candidates.sample(1)

    return extracted_player, new_member


def maximise_expense(args, random_team, df, av_g_f, av_a_m, av_g_c):
    """`maximise_expense` keeps removing one player and replacing it until
    all money are spent (cap up to 50 iterations)"""

    expense = sum(random_team["Price"])
    iterations = 0
    duplicate = random_team[random_team.duplicated()]
    while expense < args.max_expense:
        if iterations > 100:
            break
        iterations += 1
        new_random_team = get_random_team(
            df, False, random_team, av_g_f, av_a_m, av_g_c
        )
        new_expense = sum(new_random_team["Price"])
        duplicate, same_team_players, i = find_duplicates(new_random_team)
        while duplicate.empty is False or i >= 3:
            new_random_team = get_random_team(
                df, False, random_team, av_g_f, av_a_m, av_g_c
            )
            new_expense = sum(new_random_team["Price"])
            duplicate, same_team_players, i = find_duplicates(new_random_team)
        if new_expense > expense and new_expense < args.max_expense:
            random_team = new_random_team
            expense = new_expense

    return random_team


def find_duplicates(team_DF):
    """`find_duplicates` finds player if added twice to the team
    finds players and same team and number of
    players in the same team-1"""

    duplicate = team_DF[team_DF.duplicated()]
    same_team_players = team_DF[team_DF.duplicated(subset="Team")]
    i = 0
    while same_team_players.empty is False:
        same_team_players = same_team_players[
            same_team_players.duplicated(subset="Team")
        ]
        i += 1
    return duplicate, same_team_players, i


def print_pretty_table(args, random_team):
    """`print_pretty_table` makes a pretty table of your random team"""
    player_table = PrettyTable(junction_char="|")

    field_names = [
        "Player",
        "Price",
        "Goals",
        "Goals/90mins",
        "Assists",
        "Assists/90mins",
        "Goals Conceded",
        "Goals Conc/90mins",
    ]

    if args.show_ext_info:
        field_names.append("Element Type")
        field_names.append("Team")
        field_names.append("Status")
        field_names.append("Minutes")

    player_table.field_names = field_names

    for index, player in random_team.iterrows():
        row = [
            player["Name"],
            player["Price"],
            player["Goals"],
            player["GP90"],
            player["Assists"],
            player["AP90"],
            player["Goals Conceded"],
            player["GCP90"],
        ]

        if args.show_ext_info:
            row.append(player["Position"])
            row.append(player["Team"])
            row.append(player["Status"])
            row.append(player["Minutes"])
        player_table.add_row(row)

    player_table.align["Player"] = "l"

    print(player_table)


if __name__ == "__main__":
    """`main`"""
    main()
