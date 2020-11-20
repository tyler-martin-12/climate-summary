import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import time
import os
from glob import glob
import matplotlib.dates as mdates
import matplotlib.dates as mdates
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def read_key():
    with open('../key.txt') as f:
        key = f.read()
    return key


def read_latlong():
    with open('latlong.json', 'r') as f:
        latlong = json.load(f)
    return latlong


def unix_to_ts(unix):
    return pd.to_datetime(unix, unit='s')


def get_unix_time():
    now = datetime.now()
    unix = int(time.mktime(now.timetuple()))
    return unix


def dt_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def response_to_df(response):
    day = json.loads(response.text)
    df = pd.DataFrame(day['hourly']['data'])
    to_drop = 'dewPoint ozone precipType pressure uvIndex'.split()
    to_drop = [c for c in to_drop if c in df.columns]
    df.drop(to_drop, axis=1, inplace=True)
    return df


def construct_url(key, lat, long, dt):
    endpt = 'https://api.darksky.net/forecast'
    ts = dt_to_unix(dt)
    url = f'{endpt}/{key}/{lat},{long},{ts}'
    return url


def setup_dir(place):
    data_dir = f'data/{place}'
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def load_year(place):
    path = f'data/{place}/*csv'
    files = glob(path)
    logging.info(f'{len(files)} days downloaded')
    df = pd.concat([pd.read_csv(f) for f in files], sort=False)
    df.reset_index(inplace=True, drop=True)
    df.sort_values('time', inplace=True)
    df['dt'] = df.time.apply(unix_to_ts)
    return df


def apply_mdates(ax, date_index, freq='quarter'):
    accepted_freq = ['quarter', 'month', '2week', 'monday', 'daily']
    if freq not in accepted_freq:
        logging.info(f'freq {freq} not accepted. Accepted list: {accepted_freq}')

    if freq == 'quarter':
        date_locator = mdates.MonthLocator((1, 4, 7, 10))
        date_fmt = mdates.DateFormatter('%b %y')
        buffer = 45
        ax = format_axis(ax, date_index, date_locator, date_fmt, buffer)

    if freq == 'month':
        date_locator = mdates.MonthLocator()
        date_fmt = mdates.DateFormatter('%b %y')
        buffer = 15
        ax = format_axis(ax, date_index, date_locator, date_fmt, buffer)

    if freq == '2week':
        date_locator = mdates.DayLocator((1, 15))
        date_fmt = mdates.DateFormatter('%d %b %y')
        buffer = 2
        ax = format_axis(ax, date_index, date_locator, date_fmt, buffer)

    if freq == 'monday':
        date_locator = mdates.WeekdayLocator((0))
        date_fmt = mdates.DateFormatter('%d %b %y')
        buffer = 4
        ax = format_axis(ax, date_index, date_locator, date_fmt, buffer)

    if freq == 'daily':
        date_locator = mdates.DayLocator()
        date_fmt = mdates.DateFormatter('%d %b')
        buffer = 1
        ax = format_axis(ax, date_index, date_locator, date_fmt, buffer)
    return ax


def format_axis(ax, date_index, date_locator, date_fmt, buffer):
    ax.xaxis.set_major_locator(date_locator)
    ax.xaxis.set_major_formatter(date_fmt)
    ax.set_xlim((date_index.min() - timedelta(buffer), date_index.max() + timedelta(buffer)))
    return ax

def make_summary(df):
    summary = {}
    summary['mean_wind'] = round(df.windSpeed.mean(), 2)
    summary['mean_temp'] = round(df.temperature.mean(), 2)
    summary['mean_humidity'] = round(df.humidity.mean(), 3)
    summary['mean_cc'] = round(df.cloudCover.mean(), 3)

    daily_mean = df.groupby(pd.Grouper(key='dt', freq='D')).agg({'cloudCover':'mean'})
    n_sunny = (daily_mean.cloudCover < .5).value_counts()[True]
    summary['n_sunny'] = n_sunny
    return summary

def initialize_summary():
    path = 'summary.csv'
    if os.path.exists(path):
        return path

    with open(path,'w') as f:
        f.write('place,mean_wind,mean_temp,mean_humidity,mean_cloud_cover,n_sunny')
        f.write('\n')
    return path

def save_summary(summary,place):
    path = initialize_summary()
    with open(path,'a') as f:
        f.write(f"{place},"
                f"{summary['mean_wind']},"
                f"{summary['mean_temp']},"
                f"{summary['mean_humidity']},"
                f"{summary['mean_cc']},"
                f"{summary['n_sunny']}")
        f.write('\n')