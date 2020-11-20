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


def start_summary():
    path = utils.initialize_summary()
    latlong = utils.read_latlong()
    place_list = list(latlong.keys())
    for place in place_list:
        df = utils.load_year(place)
        summary = utils.make_summary(df)
        utils.save_summary(summary, place)

if __name__ == '__main__':
    fire.Fire(start_summary)