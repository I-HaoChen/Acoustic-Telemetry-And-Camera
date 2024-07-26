import numpy as np
import pandas as pd

from src.utils.filter_util import assign_experiment_section
from src.utils.project_constants import ProjectConstants


def init_speed_data(minutes: int = 10, include_random_phases=False, interpolate=True):
    df_speed = pd.read_csv(ProjectConstants.CAMERA_DATA.joinpath("telemetryCameraSpeed10minAveragedDF.csv"),
                           index_col=0)
    df_speed.index = pd.to_datetime(df_speed.index)
    df_speed.index = df_speed.index + pd.DateOffset(hours=1)
    df_speed["Time (corrected)"] = df_speed.index

    start_of_activity_logs = pd.to_datetime("2023-06-02")
    end_of_activity_logs = pd.to_datetime("2023-07-13")

    df_speed = df_speed.resample(f'{minutes}min', label='left', closed='left',
                                 offset=f"{0}min",
                                 on="Time (corrected)").mean()  # STATS 0.1

    df_speed["date"] = df_speed.index.date
    df_speed['section'] = df_speed.apply(assign_experiment_section, axis=1)
    if not include_random_phases:
        df_speed = df_speed.loc[
            (df_speed["section"] != "Irregular Phase 1") & (df_speed["section"] != "Irregular Phase 2")]

    try:
        df_speed = df_speed[(df_speed["date"]) < pd.Timestamp(end_of_activity_logs, tz="UTC")]
        df_speed = df_speed[df_speed["date"] >= pd.Timestamp(start_of_activity_logs, tz="UTC")]
    except TypeError as e:
        df_speed = df_speed[(df_speed["date"]) < pd.Timestamp(end_of_activity_logs)]
        df_speed = df_speed[df_speed["date"] >= pd.Timestamp(start_of_activity_logs)]

    df_speed["time"] = df_speed.index.time
    start_time = pd.to_datetime('6:00')
    end_time = pd.to_datetime('21:00')
    # 89 data rows per day
    df_speed = df_speed[(df_speed["time"] >= start_time.time()) & (df_speed["time"] < end_time.time())]

    if interpolate:
        rows_with_nan = df_speed[df_speed.isna().any(axis=1)]
        if include_random_phases:
            assert len(rows_with_nan) <= 393, " NAN values for speed before interpolation"
        else:
            assert len(rows_with_nan) <= 202, " NAN values for speed before interpolation"
        df_speed = df_speed.interpolate(method='linear')  # STATS 0.2

        rows_with_nan = df_speed[df_speed.isna().any(axis=1)]
        assert len(rows_with_nan) == 0, "Found NAN values for speed after interpolation"
    df_speed = df_speed[["section", "speed"]]
    return df_speed


def spline_interpolation_of_speed_data(df_speed):
    formatting_data_start = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-06-02 00:00:00']))
    formatting_data_end = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-07-12 23:50:00']))
    df_speed_as_freq = pd.concat([df_speed.copy(), formatting_data_start, formatting_data_end]).asfreq(freq='10min')
    df_speed_interpolated_spline = df_speed_as_freq.interpolate("slinear")

    df_speed_interpolated_spline["date"] = df_speed_interpolated_spline.index.date
    df_speed_interpolated_spline['section'] = df_speed_interpolated_spline.apply(assign_experiment_section, axis=1)
    df_speed_interpolated_spline = df_speed_interpolated_spline[["section", "speed"]]
    return df_speed_interpolated_spline

def zero_interpolation_of_speed_data(df_speed):
    formatting_data_start = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-06-02 00:00:00']))
    formatting_data_end = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-07-12 23:50:00']))
    df_speed_as_freq = pd.concat([df_speed.copy(), formatting_data_start, formatting_data_end]).asfreq(freq='10min')
    df_speed_as_freq["speed"] = df_speed_as_freq['speed'].fillna(0)

    df_speed_as_freq["date"] = df_speed_as_freq.index.date
    df_speed_as_freq['section'] = df_speed_as_freq.apply(assign_experiment_section, axis=1)
    df_speed_as_freq = df_speed_as_freq[["section", "speed"]]
    return df_speed_as_freq

if __name__ == "__main__":
    df_speed = init_speed_data(include_random_phases=True)
    print(f"Speed data 2023 ({len(df_speed)}) loaded")
