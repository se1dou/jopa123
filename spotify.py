import base64
import os

import requests
import time
import pprint
import flask
import datetime

from pprint import pprint

SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'


def get_current_track():
    token = open('tokens.txt', mode='r')
    tokens = token.readlines()
    print(tokens)
    response = requests.get(
        'https://accounts.spotify.com/authorize?client_id=a319572183894ee6b2756d4bf2a37100&response_type=code&redirect_uri=http%3A%2F%2F192.168.1.71%3A5000%2Ffaceit&scope=user-read-currently-playing',
        allow_redirects=True
    )
    print(response.history)
    print(response.cookies)
    print(response.content)
    req = requests.post('https://accounts.spotify.com/api/token',
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        data={
                            "grant_type": "refresh_token",
                            "refresh_token": f"{tokens[1]}",
                            "code": "AQAk6PfHxbO5-yXjCQA-ElXzZX-cp8SSertupz_ZMZG8TE_rcP9aly93vDVPkslKBDF9sKyralTlJPCrPQd3523rUg5N1v7rbEB4Mbcv7puuQpyjBWIOXtw7pgVCX6XxCQNdfB4-gsY77DyJ2wxioMezObz0oSPX18Rtfkv76UIvxXp4bPMcTVrsLM8CX2F83rTCRS9Ew1xfEnCtRMe9Mg",
                            "client_id": "a319572183894ee6b2756d4bf2a37100",
                            "client_secret": "576c02c0a378441689b78588ddfc2831"
                        }

                        )
    print(req.json())
    req = req.json()
    token = open('tokens.txt', mode='w')
    token.write(f"{req['access_token']}\n{tokens[1]}")
    token = open('tokens.txt', mode='r')
    tokens = token.readlines()

    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization": f"Bearer {tokens[0].strip()}"
        }
    )
    json_resp = response.json()
    pprint(json_resp)
    track_id = json_resp['item']['id']
    images = json_resp['item']['album']['images'][0]['url']
    track_name = json_resp['item']['name']
    artists = [artist for artist in json_resp['item']['artists']]

    link = json_resp['item']['external_urls']['spotify']

    artist_names = ', '.join([artist['name'] for artist in artists])

    current_track_info = {
        "id": track_id,
        "track_name": track_name,
        "artists": artist_names,
        "link": link,
        "image": images
    }

    return current_track_info


def main1():
    current_track_id = None
    current_track_info = get_current_track()

    if current_track_info['id'] != current_track_id:
        pprint(
            current_track_info,
            indent=4,
        )
        current_track_id = current_track_info['id']

    return current_track_info


from flask import Flask, render_template, redirect

app = Flask(__name__)


def main2():
    data = {}
    response = requests.get(
        'https://open.faceit.com/data/v4/players?nickname=-SEiDOU&game=csgo&game_player_id=76561199061441656',
        headers={
            "Authorization": f"Bearer 184752d8-a3ca-4e22-97bb-059716e46a61",
            "accept": "application/json"
        })
    response = response.json()
    data['lvl'] = response['games']['csgo']['skill_level']
    data['elo'] = response['games']['csgo']['faceit_elo']
    faceit_id = response['player_id']
    response2 = requests.get(f'https://open.faceit.com/data/v4/players/{faceit_id}/stats/csgo', headers={
        "Authorization": f"Bearer 184752d8-a3ca-4e22-97bb-059716e46a61",
        "accept": "application/json"
    })

    response2 = response2.json()
    #  pprint(response2)
    data['stats'] = response2['lifetime']
    data['stats'].pop('Recent Results', None)
    data['stats'].pop('Longest Win Streak', None)
    data['stats'].pop('Longest Win Streak', None)
    today = time.mktime(datetime.datetime.utcnow().timetuple()) - 24 * 60 * 60
    response3 = requests.get(
        f'https://open.faceit.com/data/v4/players/{faceit_id}/history?game=csgo&from={int(today)}&offset=0&limit=90',
        headers={
            "Authorization": f"Bearer 184752d8-a3ca-4e22-97bb-059716e46a61",
            "accept": "application/json"
        })
    # pprint(response3.json())
    return data


@app.route("/faceit")
def hello_world2():
    info1 = main2()
    return render_template('faceit.html', context=info1)


@app.route("/spotify")
def hello_world():
    info = main1()
    return render_template("spotify.html", context=info)


@app.route("/spotify_auth")
def hello_world3():
    return redirect(
        "https://accounts.spotify.com/authorize?client_id=ae41658499b7406da5d432acfcfd3779&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Ffaceit&scope=user-read-currently-playing",
        code=302)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
