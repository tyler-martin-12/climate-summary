import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import json
from datetime import datetime, timedelta
import time
import fire
import os
from tqdm import tqdm
import requests
import utils
from glob import glob


def start_plots():
    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)

    latlong = utils.read_latlong()
    place_list = list(latlong.keys())

    place_data = {}
    means = {}
    for place in place_list:
        place_data[place] = utils.load_year(place)
        means[place] = compute_means(place_data[place])
        plot_single_place(means[place]['daily'], place, plot_dir)

    comparison_plot(means, plot_dir)


def compute_means(df):
    place_means = {}
    agg = {}
    agg['windSpeed'] = 'mean'
    agg['temperature'] = 'mean'
    agg['humidity'] = 'mean'
    agg['cloudCover'] = 'mean'

    place_means['daily'] = df.groupby(pd.Grouper(key='dt', freq='D')).agg(agg)
    place_means['monthly'] = df.groupby(pd.Grouper(key='dt', freq='M')).agg(agg)

    return place_means


def plot_single_place(daily_mean, place, plot_dir):
    fig, axes = plt.subplots(4, 1)
    colors = 'red blue green purple'.split()
    names = ['Temperature', 'Wind Speed', 'Humidity', 'Cloud Cover']
    cols = 'temperature windSpeed humidity cloudCover'.split()

    for idx, (color, name, col) in enumerate(zip(colors, names, cols)):
        _ = axes[idx].plot(daily_mean.index, daily_mean[col], c=color, alpha=.2, label='daily mean')
        _ = axes[idx].plot(daily_mean.index, daily_mean[col].rolling(7, center=True).mean(), c=color, alpha=1, label='7 day rolling mean')

        axes[idx] = utils.apply_mdates(axes[idx], daily_mean.index, 'month')
        _ = axes[idx].legend(loc=1)
        _ = axes[idx].grid()
        title_text = f'Mean {name} over 2019 for {place.upper()}'
        _ = axes[idx].set_title(title_text, size=15)

    fig.set_size_inches(20, 20)
    path = f'{plot_dir}/{place}'
    plt.savefig(path)


def comparison_plot(means, plot_dir, freq='daily', rolling=14):
    fig, axes = plt.subplots(4, 1)

    names = ['Temperature', 'Wind Speed', 'Humidity', 'Cloud Cover']
    cols = 'temperature windSpeed humidity cloudCover'.split()

    place2color = get_color_dict()

    for idx, (name, col) in enumerate(zip(names, cols)):
        for place, place_means in means.items():
            _ = axes[idx].plot(place_means[freq].index, place_means[freq][col].rolling(rolling, center=True).mean(), c=place2color.get(place), alpha=1, label=place.upper())

        axes[idx] = utils.apply_mdates(axes[idx], place_means[freq].index, 'month')
        _ = axes[idx].legend(loc=1)
        _ = axes[idx].grid()
        title_text = f'{rolling} day rolling {name} over 2019'
        _ = axes[idx].set_title(title_text, size=15)

    fig.set_size_inches(20, 20)
    path = f'{plot_dir}/comparison'
    plt.savefig(path)


def get_color_dict():
    place2color = {}
    place2color['london'] = 'red'  ## red lion
    place2color['christchurch'] = 'black'  ## all blacks
    place2color['denver'] = 'blue'  ## broncos
    place2color['auckland'] = 'green'  ## out of ideas

    return place2color


if __name__ == '__main__':
    fire.Fire(start_plots)
