#!/usr/bin/env python3

import os

import requests
from bs4 import BeautifulSoup


def get_row_data(row):
    user, *_, score  = [d.text.strip() for d in row.find_all('td')[1:]]
    return (user, float(score), row.find('a')['href'])


def parse_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    group_info = soup.find("div", attrs={'class':'divider_list-flex'}).find_all('div')
    info = {v[1]: v[2] for v in [d.text.split('\n') for d in group_info][:3]}
    info["Name"] = soup.h1.text
    info["Rank"] = int(info.pop("Rank"))
    info["Score"] = float(info.pop("Score"))
    users = soup.find(id="top_users").find_all('tr')
    info["Users"] = [*map(get_row_data, users[1:])]
    return info


if __name__ == "__main__":
    if not os.path.exists('ualberta.html'):
        r = requests.get("https://open.kattis.com/universities/ualberta.ca")
        with open('ualberta.html', 'wb') as f:
            f.write(r.content)

    with open('ualberta.html', 'r') as f:
        print(parse_page(f.read()))
