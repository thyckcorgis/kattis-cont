#!/usr/bin/env python3

from functools import reduce

import os

import polars as pl
import requests
from bs4 import BeautifulSoup

KATTIS = 'https://open.kattis.com'
URLS = {
    "unis": "/ranklist/universities",
    "uofa": "/universities/ualberta.ca",
    "ca": "/countries/CAN",
    "ph": "/countries/PHL",
}


def urljoin(*args):
    return reduce(lambda a, b: a.rstrip('/') + '/' + b.lstrip('/'), args) if args else ''


def get_page(path: str, skip_cache=False):
    url = urljoin(KATTIS, path)
    file_path = url.replace(KATTIS, 'html') + '.html'
    dirname = os.path.dirname(file_path)
    if skip_cache or not os.path.exists(file_path):
        r = requests.get(url)
        os.makedirs(dirname, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(r.content)

    with open(file_path, 'r') as f:
        return f.read()


def get_row_data(row):
    user, *_, score = [d.text.strip() for d in row.find_all('td')[1:]]
    return (user, float(score), row.find('a')['href'])


def get_group_df(path, skip_cache=False):
    p = parse_page(get_page(path, skip_cache))
    return (
        pl.DataFrame(
            [(k, *v) for k, v in enumerate(p['Top_Users'])],
            schema=['Rank', 'Name', 'Score', 'URL'],
        )
        .with_columns((0.2 * (0.8**pl.col('Rank')) * pl.col('Score')).alias('Contributed'))
    )


def parse_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    group_info = (
        soup.find("div", attrs={'class': 'divider_list-flex'})
        .find_all('div')  # type: ignore
    )
    info = {v[1]: v[2] for v in [d.text.split('\n') for d in group_info][:3]}
    info["Name"] = soup.h1.text  # type: ignore
    info["Rank"] = int(info.pop("Rank"))
    info["Score"] = float(info.pop("Score"))
    users = soup.find(id="top_users").find_all('tr')  # type: ignore
    info["Top_Users"] = [*map(get_row_data, users[1:])]
    return info


def parse_uni_row_data(row):
    tds = row.find_all('td')
    rank, uni, country, sub, users, score = map(lambda x: x.text.strip(), tds)
    return (
        int(rank),
        uni,
        tds[1].a['href'],
        country,
        tds[2].a['href'],
        sub,
        tds[3].a['href'] if sub else '',
        int(users),
        float(score),
    )


def get_universities():
    page = get_page(URLS['unis'])
    soup = BeautifulSoup(page, 'html.parser')
    unis = soup.find(id="top_universities").find_all('tr')[1:]  # type: ignore
    return (
        pl.DataFrame(
            [parse_uni_row_data(r) for r in unis],
            schema=[
                'Rank',
                'University',
                'University URL',
                'Country',
                'Country URL',
                'Subdivision',
                'Subdivision URL',
                'Users',
                'Score'
            ],
        )
        .with_columns(
            pl.when(pl.col(pl.Utf8).str.lengths() == 0)
            .then(pl.lit(None))
            .otherwise(pl.col(pl.Utf8))
            .keep_name()
        )
    )


if __name__ == "__main__":
    pl.Config.set_fmt_str_lengths(100)
    pl.Config.set_tbl_rows(50)
    # print(get_group_df('/countries/PHL'))
    # print(get_group_df('/countries/CAN'))
    # print(get_group_df('/countries/CAN/AB'))
    print(get_group_df(URLS['uofa']))
