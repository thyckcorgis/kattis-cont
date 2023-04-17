#!/usr/bin/env python3

from collections import namedtuple
import polars as pl

from kattis import URLS, get_group_df


def get_sum(df: pl.DataFrame, score: float, user: str):
    v = df.sort(by=['Score'], descending=True).with_columns(
        (0.2 * (0.8**pl.col('Rank')) * pl.col('Score')).alias('Contributed'))

    def process(u: dict):
        if u['URL'] == user:
            u['Score'] = score
        return u

    def add_index(k, i):
        k['Rank'] = i
        return k

    return (
        pl.DataFrame([
            add_index(k, i)
            for i, k in enumerate(
                sorted(
                    [process(u) for u in v.to_dicts()],
                    key=lambda x: x['Score'],
                    reverse=True
                )
            )
        ])
        .with_columns((0.2 * (0.8**pl.col('Rank')) * pl.col('Score')).alias('Contributed'))
        ['Contributed']
        .sum()
    )


Goal = namedtuple('Goal', 'i_goal i_curr req tot_goal tot_curr')


def find_goal(df: pl.DataFrame, goal: float, user: str):
    rows = df.filter(pl.col('URL') == user)['Score'].to_list()
    if not rows:
        msg = f'user {user} not found in top 50. git gud'
        return msg
        # raise ValueError(msg)
    original = rows[0]
    orig_total = df['Contributed'].sum()
    if orig_total >= goal:
        msg = 'goal already passed'
        return msg
        # raise ValueError(msg)
    # We can only go up
    low = original
    # This is assuming you're alone and carrying the whole group
    high = goal * 5
    iters = []
    while low <= high:
        mid = (low+high) / 2
        total = get_sum(df, mid, user)
        iters.append(total)
        if 0 <= total - goal <= 0.1:
            return Goal(
                i_goal=f'{mid:0.1f}',
                i_curr=f'{original:0.1f}',
                req=f'{mid-original:0.1f}',
                tot_goal=f'{total:0.1f}',
                tot_curr=f'{orig_total:0.1f}',
            )
        elif total < goal:
            low = mid + 0.1
        else:
            high = mid - 0.1
    msg = f'Goal score not found: f{iters}'
    return msg
    # raise ValueError(msg)


def main():
    df = get_group_df(URLS['uofa'])
    user = input('Username: ')
    if not user:
        msg = 'User not entered'
        return msg
        # raise ValueError(msg)
    user = f'/users/{user}'
    goal = input('Group Score goal: ')
    if not goal:
        msg = 'Goal not entered'
        return msg
        # raise ValueError(msg)
    goal = float(goal)
    return find_goal(df, goal, user)


if __name__ == "__main__":
    res = main()
    print()
    if type(res) == Goal:
        print('Results:')
        print()
        print('Individual Score goal:', res.i_goal)
        print('Current Individual Score:', res.i_curr)
        print('Required additional score to achieve Group Score goal:', res.req)
        print()
        print('Group Score goal:', res.tot_goal)
        print('Current Group Score:', res.tot_curr)
    else:
        print(res)
