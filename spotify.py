import requests
from values_adapter import ValuesAdapter
import inspect

# temporary token for testing
TOKEN = 'BQBwnAQ0d7aBMaG2YxkACLnh-mb1tFzSGfb5dPCchtbFmNB23sFhpSVZruGxydaydUMjFQq-eU0NO5lg92Vv6kfYDjEP1m_kVqTxIWrYWC1Ud8cJYqBa7fL-vN-74wU9X_vGbFiGFSuaP69Q7aZbe0p0zeN8phsLQj6FYpV1Zkl3nwX-Vu36tf9GJvPPKLc'


def request_aux(url):
    print(f'{inspect.stack()[1].function} is making a request')

    ValuesAdapter.increament('requests', 1)
    return requests.get(url, headers={'Authorization': f'Bearer {TOKEN}'})


def __del__markets(list):
    for item in list:
        if 'available_markets' in item:
            del item['available_markets']


# 1- Get artist ID
# 2- Get artist albums
# 3- Match albums

def get_artist(artist_name):
    '''
    Returns the most popular artist ID for the given artist name
    '''
    # response = requests.get(f'https://api.spotify.com/v1/search?q={artist_name}&type=artist',
    #                         headers={'Authorization': f'Bearer {TOKEN}'})

    response = request_aux(
        f'https://api.spotify.com/v1/search?q={artist_name}&type=artist')

    # Return the most popular artist
    raw_results = response.json()['artists']['items']
    return raw_results[0]['id']


def search(query, type='artist'):
    '''
    Returns the most popular artist ID for the given artist name
    '''

    query = ''.join([c for c in query if c.isalpha()
                    or c.isdigit() or c == ' ']).rstrip()
    query = query.replace(' ', '%20')

    # response = requests.get(f'https://api.spotify.com/v1/search?q={query}&type={type}&limit=20',
    #                         headers={'Authorization': f'Bearer {TOKEN}'})

    response = request_aux(
        f'https://api.spotify.com/v1/search?q={query}&type={type}&limit=20')

    res = response.json()[f'{type}s']['items']
    __del__markets(res)

    return res


def get_artist_albums(artist_id, include_groups=['album', 'single', 'compilation']):
    '''
    Returns a list of albums IDs for the given artist ID
    '''

    # Keeps seeking albums and updating offset (max limit 40)

    limit = 50
    offset = 0

    prev_ids = []
    curr_ids = []
    total_ids = []

    while True:
        filter = '%2C'.join(include_groups)
        # response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums?limit={limit}&offset={offset}&include_groups={filter}',
        #                         headers={'Authorization': f'Bearer {TOKEN}'})

        response = request_aux(
            f'https://api.spotify.com/v1/artists/{artist_id}/albums?limit={limit}&offset={offset}&include_groups={filter}')

        prev_ids = curr_ids
        curr_ids = [album['id'] for album in response.json()['items']]

        if curr_ids == prev_ids:
            break

        offset += limit
        total_ids += curr_ids

    return total_ids


def get_album(album_id):
    '''
    Returns a dictionary of the album's info for the given album ID
    '''

    # response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}',
    #                         headers={'Authorization': f'Bearer {TOKEN}'})

    response = request_aux(f'https://api.spotify.com/v1/albums/{album_id}')

    raw = response.json()

    desired_keys = ['name', 'release_date', 'genres', 'total_tracks',
                    'tracks', 'id', 'images', 'artists']

    res = {}
    for key in desired_keys:
        res[key] = raw[key]

    __del__markets(res['tracks']['items'])

    return res


def get_album_tracks(album):
    '''
    Returns a list of track IDs for the given album
    '''

    album_id = album['id']

    limit = 50
    offset = 0

    total_tracks = []
    if album['total_tracks'] < limit and album.get('tracks'):
        total_tracks = album['tracks']['items']
    else:
        # Keeps seeking albums and updating offset (max limit 50)

        prev_tracks = []
        curr_tracks = []

        while True:
            # response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}',
            #                         headers={'Authorization': f'Bearer {TOKEN}'})

            response = request_aux(
                f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}')

            prev_tracks = curr_tracks
            curr_tracks = response.json()['items']

            if curr_tracks == prev_tracks:
                break

            offset += limit
            total_tracks += curr_tracks

    __del__markets(total_tracks)
    return total_tracks
