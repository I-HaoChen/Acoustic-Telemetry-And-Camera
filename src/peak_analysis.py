import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.feeding_times import add_feeding_bars_discrete
from src.utils.filter_util import get_start_and_end_from_df_act
from src.utils.persistent_homology import get_persistent_homology
from src.utils.project_constants import ProjectConstants


def calculate_persistence(df, number_of_peaks_for_comparison, threshold, type="activity"):
    # Here is where we actually compute the persistence
    peaks_df = get_persistent_homology(df[type])
    peaks_df[type] = peaks_df["value"]
    peaks_df = peaks_df.loc[peaks_df["persistence"] > threshold]
    datetimes = df[[type]].reset_index().iloc[peaks_df["born"], 0]
    peaks_df["Time (corrected)"] = pd.to_datetime(datetimes.values)
    peaks_df = peaks_df.set_index(peaks_df["Time (corrected)"])
    peaks_df['rank_within_day'] = (
        peaks_df.groupby(peaks_df.index.date)['persistence']
        .transform(lambda x: x.rank(ascending=False, method='first'))
    ).astype(int).astype(str)
    # Get the highest n rows by persistence
    peaks_df = peaks_df.loc[
        peaks_df.groupby(peaks_df.index.date)["persistence"].nlargest(
            number_of_peaks_for_comparison).reset_index(
            level=0, drop=True).index]
    return peaks_df


def add_peaks_to_fig_subplot(fig, peak_df, n: int, marker_size: int = 7, type_value="activity"):
    for i in range(n):
        mini_df = peak_df.iloc[i::n, :]
        fig.add_trace(go.Scatter(x=mini_df.index, y=mini_df["value"], mode="markers", marker_symbol="circle-open",
                                 marker=dict(
                                     size=marker_size,
                                     color=ProjectConstants.COLOR_LIST_PEAKS[i])
                                 , name=f"Peak {i + 1}" if type_value else None,
                                 showlegend=True if type_value else False,
                                 legendgroup="Persistence",
                                 legendgrouptitle_text="Persistent Peaks"
                                 ), secondary_y=True if type_value is not None else False)
    return fig


def plot_whole_act_speed_time_series_with_peaks():
    """Plots Figure 1"""
    df_act = init_standard_data(include_random_phases=True)
    df_speed = init_speed_data(include_random_phases=True)
    peaks_df_act = calculate_persistence(df_act.copy(), 3, 0, type="activity")
    peaks_df_speed = calculate_persistence(df_speed.copy(), 3, 0, type="speed")
    df_speed = df_speed.asfreq("10min")
    df_speed = df_speed.reset_index()
    start, end = get_start_and_end_from_df_act(df_act)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_act["datum"], y=df_act["activity"],
                             mode='lines',
                             line=dict(color=ProjectConstants.COLOR_LIST_GREEN[0]), name="Activity",
                             legendgroup="general", legendgrouptitle_text="General"
                             ), secondary_y=False)

    fig.add_trace(go.Scatter(x=df_speed["Time (corrected)"], y=df_speed["speed"],
                             mode='lines',
                             line=dict(color=ProjectConstants.COLOR_LIST_ORANGE[0]), name="Speed",
                             legendgroup="general"
                             ), secondary_y=True)
    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        name="Feeding Event",
        marker_color="blue",
        legendgroup="general"))
    fig = add_peaks_to_fig_subplot(fig, peaks_df_act, 3)
    fig = add_peaks_to_fig_subplot(fig, peaks_df_speed, 3, type_value=None)
    fig = add_feeding_bars_discrete(fig, start_end_inclusive=[start, end], y0=0, y1=0.2,
                                    pause_hours_after_feeding=0, color="blue")
    fig.update_yaxes(range=[0, 2.1], secondary_y=False)
    fig.update_yaxes(range=[0, 2.1], secondary_y=True)

    fig.update_layout(width=1200, height=250)
    fig.update_layout(yaxis_title="Activity [m/s²]")
    fig.update_yaxes(title_text="Speed [bd/s]", secondary_y=True)
    fig.update_layout(xaxis_title="Time")
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=65, r=5, b=60, t=25)))
    fig.update_layout(template="plotly_white")
    fig.write_image(
        ProjectConstants.PLOTS.joinpath(f"figure_1").with_suffix(".pdf").as_posix())
    fig.show()


def plot_one_feeding_phase_act_time_series_with_peaks():
    """Plots Figure 2"""
    df_act = init_standard_data()
    df_act = df_act.loc[df_act["section"] == "8:00 Feeding"]
    peaks_df_act = calculate_persistence(df_act.copy(), 3, 0, type="activity")
    start, end = get_start_and_end_from_df_act(df_act)
    peaks_df_act = peaks_df_act[peaks_df_act["Time (corrected)"].dt.date.between(start, end)]
    top_3_naive = df_act.groupby('date')['activity'].nlargest(3)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_act["datum"], y=df_act["activity"],
                             mode='lines',
                             line=dict(color=ProjectConstants.COLOR_LIST_GREEN[0]), name="Activity",
                             legendgroup="general", legendgrouptitle_text="General"
                             ))
    type_value = "activity"
    # Add the persistent peaks onto the graph
    for index in range(3):
        mini_df = peaks_df_act.iloc[index::3, :]
        fig.add_trace(go.Scatter(x=mini_df.index, y=mini_df["value"], mode="markers", marker_symbol="circle-open",
                                 marker=dict(
                                     size=7,
                                     color=ProjectConstants.COLOR_LIST_PEAKS[index])
                                 , name=f"Peak {index + 1}" if type_value else None,
                                 legendgroup="Persistence",
                                 legendgrouptitle_text="Persistent Peaks"
                                 ))
    # Add the local maxima onto the graph
    top_3_naive = top_3_naive.reset_index()
    for index in range(3):
        part_df = top_3_naive.groupby("date").apply(lambda x: x.iloc[index])
        fig.add_trace(go.Scatter(x=part_df["Time (corrected)"], y=part_df["activity"], mode='markers',
                                 marker=dict(symbol='cross', color=ProjectConstants.COLOR_LIST_PEAKS[index]),
                                 name=f"Top {index + 1}", legendgroup="Maxima", legendgrouptitle_text="Maxima"
                                 ))
    fig = add_feeding_bars_discrete(fig, start_end_inclusive=[start, end], y0=0, y1=0.2,
                                    pause_hours_after_feeding=0, color="blue")
    for datetime, act, persistence in zip(peaks_df_act.index, peaks_df_act["activity"], peaks_df_act["persistence"]):
        fig.add_shape(
            type="line",
            x0=datetime,
            x1=datetime,
            y0=act - persistence,
            y1=act,
            line=dict(color=px.colors.qualitative.T10[5], width=1.5)
        )

    # Add phantom trace for persistence lines
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        name="Persistence",
        marker_color=px.colors.qualitative.T10[5],
        mode='lines',
        legendgroup="Persistence",
        legendgrouptitle_text="Persistence"))
    fig.add_trace(go.Bar(
        x=[None],
        y=[None],
        name="Feeding Event",
        marker_color="blue",
        legendgroup="general"))
    fig.update_yaxes(range=[0, 2])
    fig.update_layout(width=1200, height=350)
    fig.update_layout(yaxis_title="Activity [m/s²]")
    fig.update_layout(xaxis_title="Time")
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=65, r=5, b=60, t=25)))
    fig.update_layout(template="plotly_white")
    fig.write_image(
        ProjectConstants.PLOTS.joinpath(f"figure_2").with_suffix(".pdf").as_posix())
    fig.show()
