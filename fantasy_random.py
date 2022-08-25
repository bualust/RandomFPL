import asyncio
import aiohttp
from prettytable import PrettyTable
from fpl import FPL
import pandas as pd

async def main():
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()

    df = pandas_df_players(players)
    df = select_only_active(df)
    random_team = get_random_team(df, True, df)
    random_team = maximise_expense(random_team, df)
    print_pretty_table(random_team)
    print('Congratulations! You spent ', sum(random_team['Price']))

def select_only_active(df):
    df = df[df['Status']=='a']
    return df

def pandas_df_players(players):

    names = []
    price = []
    position = []
    news = []
    status = []
    for player in players:
        names.append(player.web_name)
        price.append(float(player.now_cost / 10))
        position.append(int(player.element_type))
        news.append((player.news))
        status.append((player.status))

    df = pd.DataFrame(
        {
            "Name" : names,
            "Price" : price,
            "Position": position,
            "News": news,
            "Status": status,
        }
    )
    return df

def get_random_team(df, isFirstAttempt, random_team):

    goal_keepers = df[df["Position"]==1]
    defenders    = df[df["Position"]==2]
    midfielders  = df[df["Position"]==3]
    forwards     = df[df["Position"]==4]

    if isFirstAttempt==True:
        print('Generating first random team')
        random_GKPs = goal_keepers.sample(2)
        random_DEF  = defenders.sample(5)
        random_MID  = midfielders.sample(5)
        random_FWD  = forwards.sample(3)
        random_team = pd.concat([random_GKPs, random_DEF, random_MID, random_FWD])
    else:
        removed_player, new_member = substituion(random_team, df)
        print('Please say goodbye to --- ')
        print(removed_player)
        player_loc  = removed_player.head().index.values
        random_team = random_team.drop(index=player_loc, axis=1)
        print('--- and welcome out new team member')
        print(new_member)
        random_team = pd.concat([random_team, new_member])

    return random_team

def select_new_candidates(random_team, df):

    extracted_player  = random_team.sample(1)
    removed_position = int(extracted_player.iloc[0]['Position'])
    removed_price    = float(extracted_player.iloc[0]['Price'])
    new_candidates   = df[df["Position"]==removed_position]
    new_candidates   = new_candidates[new_candidates['Price']!=removed_price]
    new_candidates   = new_candidates[new_candidates['Price']>removed_price]

    return extracted_player, new_candidates

def substituion(random_team, df):

    extracted_player, new_candidates = select_new_candidates(random_team, df)
    while new_candidates.empty:
        extracted_player, new_candidates = select_new_candidates(random_team, df)

    new_member       = new_candidates.sample(1)

    return extracted_player, new_member

def maximise_expense(random_team, df):

    expense = sum(random_team['Price'])
    iterations = 0
    while expense < 100.0:
        if iterations > 50: break
        iterations += 1
        print('We have money to use, lets generate another team')
        new_random_team = get_random_team(df, False, random_team)
        new_expense = sum(new_random_team['Price'])
        if new_expense > expense and new_expense < 100.0:
            random_team = new_random_team
            expense = new_expense
        else:
            print('Confirming team for total expense of == ',expense)

    return random_team


def print_pretty_table(random_team):
    player_table = PrettyTable()
    player_table.field_names = ["Player", "Price", "Element Type",
                                "News", "Status"]
    player_table.align["Player"] = "l"
    for index, player in random_team.iterrows():
        player_table.add_row([player['Name'], player['Price'],
                            player['Position'],player['News'], player['Status']])

    print(player_table)

if __name__ == "__main__":
    asyncio.run(main())
