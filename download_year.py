import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import time
import fire
import os
from tqdm import tqdm
import requests
import utils


def start_download(place='london'):
    latlong = utils.read_latlong()
    if place not in latlong:
        print(f'{place} not in {latlong.keys()}')
        return

    data_dir = utils.setup_dir(place)
    key = utils.read_key()
    lat, long = latlong[place]

    start = pd.to_datetime('2019 01 01')
    stop = pd.to_datetime('2020 01 01')
    date_range = pd.date_range(start, stop)

    for day in tqdm(date_range):
        day_str = day.strftime('%Y%m%d')
        day_path = f'{data_dir}/{day_str}.csv'
        if os.path.exists(day_path):
            continue
        url = utils.construct_url(key, lat, long, day)
        response = requests.get(url)
        if response.status_code != 200:
            print(response.text)
            return
        df = utils.response_to_df(response)
        df.to_csv(day_path,index=False)

if __name__ == '__main__':
    fire.Fire(start_download)
