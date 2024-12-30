import warnings

from plotly.subplots import make_subplots

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.feeding_times import load_feeding_times
from src.utils.filter_util import filter_by_valid_days
from src.utils.project_constants import ProjectConstants

warnings.simplefilter(action="ignore", category=FutureWarning)
import pandas as pd
import plotly.graph_objects as go
import time


def mean_around_feeding(df, hours_prior, hours_after, type="activity", calc_mean=True, fixed_twilight=False):
    """Cuts the df into the time around feeding and averaging results if wished."""
    feeding_times = load_feeding_times()
    feeding_times["datum"] = feeding_times["date"]
    feeding_times = filter_by_valid_days(feeding_times)
    interval_before = pd.Timedelta(hours=hours_prior)
    interval_after = pd.Timedelta(hours=hours_after)
    if calc_mean:
        mean_df = pd.DataFrame(
            columns=["start_interval", "end_interval", "mean_for_feeding_period", "SE_for_feeding_period"])
    else:
        mean_df = pd.DataFrame(columns=df.columns)
    for experiment_section, fish_df in df.groupby(["experiment_section"]):
        for date in feeding_times.loc[feeding_times["experiment_section"] == experiment_section, "date"]:
            for feeding_events_of_the_day in feeding_times.loc[feeding_times["date"] == date, "feeding_times"]:
                for feeding_idx, feeding_event in enumerate(feeding_events_of_the_day):
                    if fixed_twilight and experiment_section == "Twilight Feeding":
                        if feeding_idx == 0:
                            feeding_event_1 = "06:33:00"
                            feeding_event_2 = "06:48:00"
                        elif feeding_idx == 1:
                            feeding_event_1 = "20:25:00"
                            feeding_event_2 = "20:40:00"
                    else:
                        feeding_event_1 = feeding_event[0]
                        feeding_event_2 = feeding_event[1]

                    feeding_start_time = pd.to_datetime(date) + pd.to_timedelta(feeding_event_1)
                    feeding_end_time = pd.to_datetime(date) + pd.to_timedelta(feeding_event_2)

                    interval_start = feeding_start_time - interval_before
                    interval_end = feeding_end_time + interval_after
                    try:
                        df_short_activity = fish_df[
                            (fish_df["datum"]) < pd.Timestamp(interval_end, tz="UTC")]
                        df_short_activity = df_short_activity[
                            df_short_activity["datum"] >= pd.Timestamp(interval_start, tz="UTC")]
                    except TypeError as e:
                        df_short_activity = fish_df[
                            (fish_df["datum"]) < pd.Timestamp(interval_end)]
                        df_short_activity = df_short_activity[
                            df_short_activity["datum"] >= pd.Timestamp(interval_start)]
                    if len(df_short_activity) > 0 and calc_mean:
                        activity_mean_for_feeding_period = df_short_activity[type].mean()
                        activity_SE_for_feeding_period = df_short_activity[type].sem()
                        mean_df = mean_df.append({"experiment_section": experiment_section,
                                                  "feeding_start": feeding_event[0],
                                                  "start_interval": interval_start,
                                                  "end_interval": interval_end,
                                                  "mean_for_feeding_period": activity_mean_for_feeding_period,
                                                  "SE_for_feeding_period": activity_SE_for_feeding_period,
                                                  "feeding_of_the_day": str(int(feeding_idx + 1))},
                                                 ignore_index=True)
                    else:
                        df_short_activity["feeding_of_the_day"] = str(int(feeding_idx + 1))
                        df_short_activity["start_interval"] = interval_start
                        df_short_activity["end_interval"] = interval_end
                        mean_df = mean_df.append(df_short_activity)
    mean_df["type"] = type
    if calc_mean:
        return mean_df.sort_values("start_interval")
    else:
        return mean_df.sort_values("datum")


def plot_means_around_feeding_with_all():
    """Plots Figure 8"""
    df_act = init_standard_data()

    df_depth = init_standard_data(data_type="Depth [m] (est. or from tag)")

    df_speed = init_speed_data()

    df_act["experiment_section"] = df_act["section"]
    df_speed["experiment_section"] = df_speed["section"]
    df_depth["experiment_section"] = df_depth["section"]
    df_act["datum"] = df_act.index
    df_speed["datum"] = df_speed.index
    df_depth["datum"] = df_depth.index
    df_act = filter_by_valid_days(df_act)
    df_speed = filter_by_valid_days(df_speed)
    df_depth = filter_by_valid_days(df_depth)

    mean_df_act = mean_around_feeding(df_act.copy(), 1, 2, type="activity", calc_mean=True)
    mean_df_depth = mean_around_feeding(df_depth.copy(), 1, 2, type="Depth [m] (est. or from tag)", calc_mean=True)
    mean_df_speed = mean_around_feeding(df_speed.copy(), 1, 2, type="speed", calc_mean=True)

    mean_df = pd.concat([mean_df_act, mean_df_speed, mean_df_depth])

    mean_df["feeding_of_the_day"].replace({"1": "first", "2": "second"}, inplace=True)
    mean_df["type"].replace({"Depth [m] (est. or from tag)": "depth"}, inplace=True)
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=3, shared_yaxes=False, horizontal_spacing=0.025, vertical_spacing=0.025,
        subplot_titles=mean_df["experiment_section"].unique() + ["", "", ""],
        specs=[
            [{"secondary_y": True}, {"secondary_y": True}, {"secondary_y": True}],
            [{"secondary_y": True}, {"secondary_y": True}, {"secondary_y": True}]
        ],
        row_heights=[0.3, 0.7]
    )

    # All x axis
    fig.layout.xaxis.matches = 'x4'
    fig.layout.xaxis2.matches = 'x5'
    fig.layout.xaxis3.matches = 'x6'
    fig.layout.xaxis4.matches = 'x4'
    fig.layout.xaxis5.matches = 'x5'
    fig.layout.xaxis6.matches = 'x6'

    # row 1
    fig.layout.yaxis.matches = 'y'
    fig.layout.yaxis3.matches = 'y'
    fig.layout.yaxis5.matches = 'y'
    # row 2
    fig.layout.yaxis7.matches = 'y7'
    fig.layout.yaxis8.matches = 'y8'
    fig.layout.yaxis9.matches = 'y7'
    fig.layout.yaxis10.matches = 'y8'
    fig.layout.yaxis11.matches = 'y7'
    fig.layout.yaxis12.matches = 'y8'

    custom_order = {"8:00 Feeding": 1, "7:30 and 13:30 Feeding": 2, "Twilight Feeding": 3}
    custom_order_types = {"activity": 1, "speed": 2, "depth": 3}
    mean_df["sort_key"] = mean_df["experiment_section"].map(custom_order)
    mean_df["sort_key_types"] = mean_df["type"].map(custom_order_types)
    mean_df = mean_df.sort_values(by=["sort_key", "sort_key_types", "feeding_of_the_day"])
    top_activity_axis = 1.25
    top_speed_axis = 1.25
    top_depth_axis = 3

    opacity = 0.7
    for idx, (experiment_section_n, facet_value_df) in enumerate(mean_df.groupby(["sort_key"])):
        for feeding_of_the_day, filtered_df in facet_value_df.groupby(["feeding_of_the_day"]):
            if feeding_of_the_day == "first":
                dash_line = "solid"
                color_for_bar = ProjectConstants.COLOR_LIST_BLUE[0]
            else:
                dash_line = "dash"
                color_for_bar = ProjectConstants.COLOR_LIST_BLUE[2]
            for (_, type), small_df in filtered_df.groupby(["sort_key_types", "type"]):
                # Adding line plots or bar plots
                if type != "depth":
                    if type == "activity":
                        color = ProjectConstants.COLOR_LIST_GREEN[0]
                    elif type == "speed":
                        color = ProjectConstants.COLOR_LIST_ORANGE[0]
                    else:
                        raise TypeError("Wrong type of data!")
                    fig.add_trace(go.Scatter(x=small_df["start_interval"], y=small_df["mean_for_feeding_period"],
                                             error_y=dict(type="data", array=small_df["SE_for_feeding_period"]),
                                             line=dict(dash=dash_line, color=color),
                                             name=f"{type}, {feeding_of_the_day}".title(), legendgroup=type),
                                  row=2, col=idx + 1, secondary_y=type != "activity")
                else:
                    #fig.add_trace(go.Bar(x=small_df["start_interval"], y=small_df["mean_for_feeding_period"],
                    #                     error_y=dict(type="data", array=small_df["SE_for_feeding_period"],
                    #                                  color=ProjectConstants.COLOR_LIST_GRAY[1]),
                    #                     marker=dict(color=color_for_bar), opacity=opacity,
                    #                     name=f"{type}, {feeding_of_the_day}", legendgroup=type),
                    #              row=1, col=idx + 1, secondary_y=False)
                    fig.add_trace(go.Scatter(x=small_df["start_interval"], y=small_df["mean_for_feeding_period"],
                                             error_y=dict(type="data", array=small_df["SE_for_feeding_period"]),
                                             line=dict(dash=dash_line, color=color_for_bar),
                                             name=f"{type}, {feeding_of_the_day}".title(), legendgroup=type),
                                  row=1, col=idx + 1, secondary_y=False)

    fig.update_layout(legend_title="Measurement Type,<br>Feeding Of The Day")

    fig.update_yaxes(range=[top_depth_axis, 0], secondary_y=False, row=1, col=1)
    fig.update_yaxes(range=[top_depth_axis, 0], secondary_y=False, row=1, col=2)
    fig.update_yaxes(range=[top_depth_axis, 0], secondary_y=False, row=1, col=3)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_xaxes(showticklabels=False, row=1, col=3)
    fig.update_yaxes(showticklabels=False, secondary_y=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, secondary_y=False, row=1, col=3)
    fig.update_yaxes(title_text="Mean Depth [m]", secondary_y=False, row=1, col=1)
    fig.update_layout(barmode='group', bargap=0.15)

    fig.update_yaxes(title_text="Mean<br>Activity [m/s²]", secondary_y=False, row=2, col=1)
    fig.update_yaxes(title_text="Mean Speed [bd/s]", secondary_y=True, row=2, col=3)
    fig.update_yaxes(range=[0, top_activity_axis], secondary_y=False, row=2, col=1)
    fig.update_yaxes(range=[0, top_activity_axis], secondary_y=False, row=2, col=2)
    fig.update_yaxes(range=[0, top_activity_axis], secondary_y=False, row=2, col=3)
    fig.update_yaxes(range=[0, top_speed_axis], secondary_y=True, row=2, col=1)
    fig.update_yaxes(range=[0, top_speed_axis], secondary_y=True, row=2, col=2)
    fig.update_yaxes(range=[0, top_speed_axis], secondary_y=True, row=2, col=3)
    fig.update_yaxes(showticklabels=False, secondary_y=True, row=2, col=1)
    fig.update_yaxes(showticklabels=False, secondary_y=False, row=2, col=2)
    fig.update_yaxes(showticklabels=False, secondary_y=True, row=2, col=2)
    fig.update_yaxes(showticklabels=False, secondary_y=False, row=2, col=3)
    fig.update_layout(width=1000, height=350)
    fig.update_layout(
        xaxis1=dict(title_text=""),
        xaxis2=dict(title_text=""),
        xaxis3=dict(title_text=""),
        xaxis4=dict(title_text=""),
        xaxis5=dict(title_text="Time"),
        xaxis6=dict(title_text=""))
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=30, r=5, b=0, t=30)))
    names = set()
    fig.for_each_trace(lambda trace: trace.update(showlegend=False) if (trace.name in names) else names.add(trace.name))
    fig.update_layout(legend_traceorder="grouped")
    time.sleep(1)
    fig.update_layout(template="plotly_white")
    fig.write_image(ProjectConstants.PLOTS.joinpath(f"figure_8").with_suffix(".pdf"))
    fig.show()
