import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.feeding_times import add_feeding_bars_discrete, load_feeding_times
from src.utils.filter_util import get_start_and_end_from_df_act
from src.utils.project_constants import ProjectConstants


def identify_lasting_peaks(df, minutes: int = 20, duration_threshold_minutes=120, quantile=0.5,
                           data_type="activity", cutoff_additional_hours=2,
                           only_untiL_feeding=False):
    df = df.resample(f"{minutes}min", label="left", closed="left",
                     offset=f"{0}min",
                     on="Time (corrected)").mean()
    df["time"] = df.index
    # choosing the quantile as threshold for FAA
    quantile = quantile
    faa_duration = int(duration_threshold_minutes / minutes)
    list_of_faa_time = []
    total_activations = 0
    # Adding ghost feeding times
    feeding_times = load_feeding_times(with_breaks=True)
    if only_untiL_feeding:
        previous_non_empty_list = None
        for index, row in feeding_times.iterrows():
            if row["feeding_times"] == []:
                if previous_non_empty_list is not None:
                    row["feeding_times"] = previous_non_empty_list
            else:
                previous_non_empty_list = row["feeding_times"]
        print(feeding_times)
    for datum, mini_df in df.groupby(df["time"].dt.date):
        mini_df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)
        faa_threshold = mini_df[data_type].quantile(quantile)
        # resample the data, since we only interested in the group behaviour
        # setting faa duration to 6 which equals 20 minutes * 6 = 120 minutes
        # This is how long a peak must persist to be considered true FAA (since 120 minutes is the feeding window)
        print(f"{faa_threshold=} and {duration_threshold_minutes=}")
        if only_untiL_feeding:
            # Remove the feeding times
            cutoff_time = feeding_times.loc[feeding_times["date"] == datum, "feeding_times"]
            # Getting the starting time of all feedings of that day
            cutoff_time_start_list = [cutoff_time.values[0][i][0] for i in range(len(cutoff_time.values[0]))]
            cutoff_time_end_list = [cutoff_time.values[0][i][1] for i in range(len(cutoff_time.values[0]))]
            cutoff_time_start_dt_list = [
                pd.to_datetime(datum.strftime("%Y-%m-%d") + " " + pd.to_datetime(el).time().strftime("%H:%M:%S")) for el
                in cutoff_time_start_list]
            fab_cutoff_time_end_dt_list = [
                pd.to_datetime(datum.strftime("%Y-%m-%d") + " " + pd.to_datetime(el).time().strftime("%H:%M:%S")) for el
                in
                cutoff_time_end_list]
            cutoff_time_start_dt_list = [el.tz_localize(None) for el in cutoff_time_start_dt_list]
            fab_cutoff_time_end_dt_list = [el.tz_localize(None) for el in fab_cutoff_time_end_dt_list]
            for (cutoff_start, cutoff_end) in zip(cutoff_time_start_dt_list, fab_cutoff_time_end_dt_list):
                cutoff_end = cutoff_end + pd.DateOffset(hours=cutoff_additional_hours)
                # Negation filtering here
                to_drop_df = mini_df.between_time(start_time=cutoff_start.time(), end_time=cutoff_end.time(),
                                                  include_end=False, include_start=True)
                mini_df = mini_df.drop(to_drop_df.index)

            mini_df = mini_df.asfreq("10min")
            na = mini_df[data_type].isna().cumsum()
            for i, d in mini_df.loc[na.eq(0) | na.duplicated()].groupby(na):
                print(d)
            # Number each value from the beginning starting with 1, but keep the number if over threshold

            grouper = mini_df.loc[na.eq(0) | na.duplicated()].groupby(
                [na, mini_df[data_type].ge(faa_threshold).diff().ne(0).cumsum()])
        else:
            grouper = mini_df.groupby(mini_df[data_type].ge(faa_threshold).diff().ne(0).cumsum())

        # The smallest in the group MUST be higher than the threshold
        # The diff between the first and last element in the group must exceed the set faa_duration
        result = []
        print(f"{faa_duration=}")
        for group_key, group in grouper:
            if group[data_type].min() >= faa_threshold:
                if len(group) >= faa_duration:
                    result.append(group)
        print(f"Number of FAA windows ({data_type}) detected for the f{datum}: {len(result)}")
        result_without_index = [df.reset_index(drop=True) for df in result]
        list_of_faa_time.append([{"faa_start": el["time"].iloc[0],
                                  "faa_end": el["time"].iloc[-1]} for el in result_without_index])
        total_activations += len(result)
    print(f"TOTAL: Number of FAA windows ({data_type}) detected: {total_activations}")
    return list_of_faa_time


def add_faa_bars(df, with_faa_bars, fig, minutes, duration_threshold_minutes=120, quantile=0.5,
                 data_type="activity",
                 color="darkgreen", y0=0.1, y1=0.12, cutoff_additional_hours=2,
                 only_untiL_feeding=False):
    if "is_activity" in df.columns:
        df = df.loc[df["is_activity"]]
    if with_faa_bars:
        faa_list = identify_lasting_peaks(df, minutes, duration_threshold_minutes=duration_threshold_minutes,
                                          quantile=quantile, data_type=data_type,
                                          cutoff_additional_hours=cutoff_additional_hours,
                                          only_untiL_feeding=only_untiL_feeding)
        for peak_list in faa_list:
            for peak in peak_list:
                fig.add_shape(
                    type="rect",
                    x0=peak["faa_start"].strftime("%Y-%m-%d %X"),
                    x1=(peak["faa_end"] + pd.Timedelta(minutes=10)).strftime("%Y-%m-%d %X"),
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.75,
                    line_width=0
                )

        return fig, faa_list


def feeding_list_to_expanded_df(faa_list):
    faa_df = pd.concat([pd.DataFrame(sublist) for sublist in faa_list], axis=0)
    faa_df["date"] = faa_df["faa_start"].dt.date

    faa_df_expanded = pd.DataFrame(columns=["Time (corrected)"])
    for _, row in faa_df.iterrows():
        start = row["faa_start"]
        end = row["faa_end"]

        faa_df_expanded = pd.concat([faa_df_expanded,
                                     pd.DataFrame(pd.date_range(start, end, freq="10min"),
                                                  columns=["Time (corrected)"])])
    return faa_df_expanded


def plot_fab_analysis():
    """Plots Figure 9"""
    df_act = init_standard_data(include_random_phases=True)
    start, end = get_start_and_end_from_df_act(df_act)
    df_act = df_act.reset_index()

    df_speed = init_speed_data(include_random_phases=True)
    formatting_data_start = pd.DataFrame({"speed": [np.nan]}, index=pd.to_datetime(["2023-06-02 00:00:00"]))
    formatting_data_end = pd.DataFrame({"speed": [np.nan]}, index=pd.to_datetime(["2023-07-12 23:50:00"]))
    df_speed = pd.concat([df_speed.copy(), formatting_data_start, formatting_data_end]).asfreq(freq="10min")
    df_speed = df_speed.reset_index(names="Time (corrected)")

    df_speed = df_speed.reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    cutoff_additional_hours = 2
    fig = add_feeding_bars_discrete(fig, start_end_inclusive=[start, end], y0=0, y1=0.2,
                                    pause_hours_after_feeding=cutoff_additional_hours, color="blue")
    fig.add_trace(
        go.Line(x=df_act["Time (corrected)"], y=df_act["activity"], name="Activity",
                line_color=ProjectConstants.COLOR_LIST_GREEN[0], legendgroup="value"),
        secondary_y=False)
    fig.add_trace(
        go.Line(x=df_speed["Time (corrected)"], y=df_speed["speed"],
                name="Speed", line_color=ProjectConstants.COLOR_LIST_ORANGE[0], legendgroup="value",
                legendgrouptitle_text="Measurement Type"),
        secondary_y=True)
    fig.update_layout(
        xaxis_title="Time")
    fig.update_yaxes(title_text="Activity [m/s²]", secondary_y=False)
    fig.update_yaxes(title_text="Speed [bd/s]", secondary_y=True)
    quantile_act = 0.5
    # For speed: We want to have 12h out of the 15h worth of speed data above the threshold. Meaning (15-12)/15 = 0.2
    quantile_speed = 0.2
    duration_threshold_minutes = 60
    # STATS 8.1
    fig, faa_list_act_feeding = (
        add_faa_bars(df_act.reset_index(), True, fig, 10, duration_threshold_minutes, quantile_act, "activity",
                     color=ProjectConstants.COLOR_LIST_GREEN[1],
                     only_untiL_feeding=True, y0=0.05, y1=0.1, cutoff_additional_hours=cutoff_additional_hours))
    fig, faa_list_speed_feeding = (
        add_faa_bars(df_speed.reset_index(), True, fig, 10, duration_threshold_minutes, quantile_speed, "speed",
                     color=ProjectConstants.COLOR_LIST_ORANGE[1],
                     only_untiL_feeding=True, y0=0.1, y1=0.15, cutoff_additional_hours=cutoff_additional_hours))

    not_included_list = ["Whole experiment", "Sea cage time", "Everything"]
    for section_1, section_2 in zip(ProjectConstants.EXPERIMENT_SECTIONS_DICT.items(),
                                    list(ProjectConstants.EXPERIMENT_SECTIONS_DICT.items())[1:]):
        y = 1.9
        if section_1[0] in not_included_list:
            continue
        if section_2[0] in not_included_list:
            continue
        second_date = section_2[1][0]
        if section_1[0] == "Twilight Feeding":
            second_date = pd.Timestamp("2023-07-12 23:59:59")
        if section_1[0] in ["Irregular Phase 1", "Irregular Phase 2"]:
            y = 2
        fig.add_annotation(x=section_1[1][0] + (second_date - section_1[1][0]) / 2, y=y, showarrow=False,
                           text=f"<b>{section_1[0]}<b>", bgcolor="white")
        if section_1[0] in ["8:00 Feeding", "7:30 and 13:30 Feeding", "Twilight Feeding"]:
            color = "blue"
        elif section_1[0] in ["Fasting 1", "Fasting 2"]:
            color = "red"
        else:
            color = "yellow"
        fig.add_shape(type="rect", x0=section_1[1][0], x1=second_date,
                      y0=1.9, y1=1.9,
                      line=dict(color=color, width=5))
    # Adding phantom traces for legend
    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        name="High Activity Window",
        marker_color=ProjectConstants.COLOR_LIST_GREEN[1],
        legendgroup="high"))
    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        name="High Speed Window",
        marker_color=ProjectConstants.COLOR_LIST_ORANGE[1],
        legendgroup="high",
        legendgrouptitle_text="High Measurement Window"))

    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        name="Feeding Event<br>Plus Two Hours",
        marker_color=ProjectConstants.COLOR_LIST_BLUE[1],
        legendgroup="Feeding",
        legendgrouptitle_text="Feeding"))

    fig.update_yaxes(range=[0, 2.1], secondary_y=False)
    fig.update_yaxes(range=[0, 2.1], secondary_y=True)
    fig.update_layout(width=1500, height=400)
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=65, r=5, b=60, t=25)))
    fig.update_layout(template="plotly_white")
    fig.write_image(ProjectConstants.PLOTS.joinpath("figure_9").with_suffix(".pdf").as_posix())
    fig.show()
