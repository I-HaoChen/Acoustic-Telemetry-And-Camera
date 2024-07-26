import datetime

import pandas as pd
from pandas import DataFrame, Timestamp

from src.utils.project_constants import ProjectConstants


def filter_by_snr(df: DataFrame, lower_bound_inclusive=25, upper_bound_exclusive=35):
    filtered_df = df[(df['SNR [dB]'] >= lower_bound_inclusive) & (df['SNR [dB]'] < upper_bound_exclusive)]
    print(
        f"Length of input df: {len(df)}\nAfter filtering by SNR [dB] ({lower_bound_inclusive}, {upper_bound_exclusive}): {len(filtered_df)}")
    return filtered_df


def cut_by_start_date(df: DataFrame, start_date: str, add_days=0):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if add_days > 0:
        start_date = start_date - datetime.timedelta(days=add_days)
    filtered_df = df[df["datum"] > Timestamp(start_date)]
    return filtered_df


def cut_by_end_date(df: DataFrame, end_date: str, include_end=True, add_days=0):
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    if include_end:
        end_date = end_date + datetime.timedelta(days=1)
    if add_days:
        end_date = end_date + datetime.timedelta(days=add_days)
    filtered_df = df[df["datum"] < Timestamp(end_date)]
    return filtered_df


def assign_experiment_section(row):
    for section, dates in ProjectConstants.EXPERIMENT_SECTIONS_DICT.items():
        if dates[0] <= row['date'] < dates[1]:
            return section
    return 'No Section'


def reduce_to_interpolated_values_with_sections_df(df, minutes, include_random_phases=False, data_type="activity"):
    if data_type == "activity":
        df = df.loc[df["is_activity"]]
    elif data_type == "temperature":
        df = df.loc[df["is_temperature"]]
    df = df.reset_index(level=0)
    df = df.resample(f'{minutes}min', label='left', closed='left',
                     offset=f"{0}min",
                     on="Time (corrected)").mean()  # STATS 0.1

    df["date"] = df.index.date
    df['section'] = df.apply(assign_experiment_section, axis=1)
    if not include_random_phases:
        df = df.loc[(df["section"] != "Irregular Phase 1") & (df["section"] != "Irregular Phase 2")]

    rows_with_nan = df[df.isna().any(axis=1)]
    initial_nans = 0
    if data_type == "activity":
        initial_nans = 10
    elif data_type == "Depth [m] (est. or from tag)":
        initial_nans = 8
    elif data_type == "temperature":
        initial_nans = 9

    assert len(rows_with_nan) <= initial_nans, f"{initial_nans} NAN values for {data_type} before interpolation"

    df = df.interpolate(method='linear')  # STATS 0.2

    rows_with_nan = df[df.isna().any(axis=1)]
    assert len(rows_with_nan) == 0, f"Found NAN values for {data_type} after interpolation"
    df = df[["section", data_type]]
    df.index = df.index.tz_localize(None)
    df.index = pd.to_datetime(df.index)
    return df


def get_start_and_end_from_df_act(df_act):
    df_act["date"] = df_act.index.get_level_values(0).date
    df_act["datum"] = df_act.index.get_level_values(0)
    start = df_act["date"].min()
    end = df_act["date"].max()
    return start, end


def filter_by_valid_days(df: DataFrame):
    filtered_df = pd.DataFrame()
    for experiment_section in ProjectConstants.FEEDING_PHASES:
        [start, end] = ProjectConstants.EXPERIMENT_SECTIONS_DICT[experiment_section]
        try:
            short_df = df[(df["datum"]) < pd.Timestamp(end, tz="UTC")]
            short_df = short_df[short_df["datum"] >= pd.Timestamp(start, tz="UTC")]
        except TypeError as e:
            short_df = df[(df["datum"]) < pd.Timestamp(end)]
            short_df = short_df[short_df["datum"] >= pd.Timestamp(start)]
        short_df["experiment_section"] = experiment_section
        filtered_df = pd.concat([filtered_df, short_df])
    return filtered_df


def reduce_two_dfs_to_common_index(df_act, df_speed):
    df_act.index = df_act.index.tz_localize(None)
    df_act.index = pd.to_datetime(df_act.index)
    common_data_index = df_act.index.intersection(df_speed.index)  # STATS 0.3
    df_act = df_act.loc[common_data_index]
    df_speed = df_speed.loc[common_data_index]
    return df_act, df_speed
