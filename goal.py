#!/usr/bin/env python3

from typing import List
from collections import namedtuple
import polars as pl

from kattis import URLS, get_group_df


def get_sum(df: pl.DataFrame, score: float, user: List[str]):
    v = df.sort(by=['Score'], descending=True).with_columns(
        (0.2 * (0.8**pl.col('Rank')) * pl.col('Score')).alias('Contributed'))

    def process(u: dict):
        if u['URL'] in user:
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
        .select(C=(0.2 * (0.8**pl.col('Rank')) * pl.col('Score')))
        ['C']
        .sum()
    )


Goal = namedtuple('Goal', 'i_goal i_curr req tot_goal tot_curr')


def find_goal(df: pl.DataFrame, goal: float, user: List[str]):
    rows = df.filter(pl.col('URL').apply(lambda x: x in user)).to_dicts()
    if not rows:
        msg = f'user {user} not found in top 50. git gud'
        return msg
        # raise ValueError(msg)
    originals = {o['URL']: o['Score'] for o in rows}
    orig_total = df['Contributed'].sum()
    if orig_total >= goal:
        msg = 'goal already passed'
        return msg
        # raise ValueError(msg)
    # We can only go up
    low = min(r['Score'] for r in rows)
    # This is assuming you're alone and carrying the whole group
    high = goal * 5
    iters = []
    while low <= high:
        mid = (low+high) / 2
        total = get_sum(df, mid, user)
        iters.append(total)
        if 0 <= total - goal <= 0.1:
            return Goal(
                i_goal=mid,
                i_curr=originals,
                req={k: mid-v for k, v in originals.items()},
                tot_goal=total,
                tot_curr=orig_total,
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
    users: List[str] = []
    while (user := input('Username(s) (input empty to finish): ')):
        users.append(user)
    if not users:
        msg = 'User not entered'
        return msg
        # raise ValueError(msg)
    users = [f'/users/{u}' for u in users]
    goal = input('Group Score goal: ')
    if not goal:
        msg = 'Goal not entered'
        return msg
        # raise ValueError(msg)
    goal = float(goal)
    return find_goal(df, goal, users)


if __name__ == "__main__":
    print('Polars version:', pl.__version__)
    res = main()
    print()
    if isinstance(res, Goal):
        pl.Config.set_fmt_str_lengths(100)
        pl.Config.set_tbl_rows(50)
        pl.Config.set_tbl_hide_column_data_types(True)
        pl.Config.set_tbl_hide_column_names(True)
        pl.Config.set_tbl_hide_dataframe_shape(True)
        rows = [
            ['Results', ''],
            ['Individual Score goal', res.i_goal],
            ['Current Individual Score', ''],
            *[[k, v] for k, v in res.i_curr.items()],
            ['Required additional score', ''],
            *[[k, v] for k, v in res.req.items()],
            ['Group Score goal', res.tot_goal],
            ['Current Group Score', res.tot_curr]
        ]
        print(pl.DataFrame(rows, schema=[
              ('Col', pl.Utf8), ('Score', pl.Utf8)]))
    else:
        print(res)
