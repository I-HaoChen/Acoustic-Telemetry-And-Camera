import datetime as dt
import json
from typing import List

import pandas
import pandas as pd
import plotly.graph_objs

from src.utils.project_constants import ProjectConstants


def load_feeding_times(with_breaks: bool = True) -> pandas.DataFrame:
    """
    Load the feeding times from a json file
    :param with_breaks: Whether the file with Fasting periods should be loaded or the one where
    "ghost" feeding times are added to make comparisons.
    :return:
    """
    if with_breaks:
        with open(ProjectConstants.FEEDING_TIMES_NO_BREAKS, 'r') as json_file:
            feeding_times_data = json.load(json_file)
    else:
        with open(ProjectConstants.FEEDING_TIMES, 'r') as json_file:
            feeding_times_data = json.load(json_file)
    feeding_times_df = pd.DataFrame([{'date': k, 'feeding_times': v} for k, v in feeding_times_data.items()])
    feeding_times_df["date"] = pd.to_datetime(feeding_times_df["date"], format='%d.%m.%Y').dt.date
    return feeding_times_df


def add_feeding_bars_discrete(fig: plotly.graph_objs.Figure, start_end_inclusive: List = None, y0=0, y1=1,
                              pause_hours_after_feeding=2,
                              verbose: bool = False, color="red") -> plotly.graph_objs.Figure:
    """Add Feeding bars under the time series graph to visualize when feeding happened"""
    feeding_times = load_feeding_times()
    if start_end_inclusive:
        feeding_times = feeding_times[
            feeding_times["date"].between(start_end_inclusive[0], start_end_inclusive[1])]
    for date in feeding_times["date"]:
        for feeding_events_of_the_day in feeding_times.loc[feeding_times["date"] == date, "feeding_times"]:
            for feeding_event in feeding_events_of_the_day:
                if verbose:
                    print(f"On {date}, feeding events was/were {feeding_event}")
                fig.add_shape(
                    type='rect',
                    x0=dt.datetime.combine(date, dt.datetime.strptime(feeding_event[0], '%H:%M:%S').time()),
                    x1=dt.datetime.combine(date, dt.datetime.strptime(feeding_event[1], '%H:%M:%S').time())
                       + pd.Timedelta(hours=pause_hours_after_feeding),
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.75,
                    line_width=0
                )
    return fig
