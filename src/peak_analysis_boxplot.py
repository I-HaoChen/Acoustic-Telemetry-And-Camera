import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.peak_analysis import calculate_persistence
from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.feeding_times import load_feeding_times
from src.utils.filter_util import assign_experiment_section
from src.utils.project_constants import ProjectConstants


def plot_rank_diff_against_feeding_time(peaks_df):
    feeding_times = load_feeding_times(with_breaks=False)
    feeding_times["datum"] = feeding_times["date"]
    feeding_times = feeding_times.explode("feeding_times")
    feeding_times[["start", "end"]] = feeding_times["feeding_times"].apply(pd.Series)
    feeding_times["time_start"] = pd.to_datetime(
        feeding_times["date"].astype(str) + " " + feeding_times["start"])
    feeding_times["time_end"] = pd.to_datetime(
        feeding_times["date"].astype(str) + " " + feeding_times["end"])

    peaks_df = peaks_df.reset_index(drop=True)
    peaks_df = peaks_df.drop(columns=["born", "left", "right", "died"])
    feeding_times = feeding_times.drop(columns=["datum", "start", "end", "feeding_times"])

    peaks_df = peaks_df.sort_values("Time (corrected)")
    feeding_times = feeding_times.sort_values("time_start")

    merged_start_df = pd.merge_asof(peaks_df, feeding_times, left_on="Time (corrected)", right_on="time_start",
                                    direction='nearest')

    feeding_times = feeding_times.sort_values("time_end")
    merge_end_df = pd.merge_asof(peaks_df, feeding_times, left_on="Time (corrected)", right_on="time_end",
                                 direction='nearest')
    assert merged_start_df["Time (corrected)"].equals(
        merge_end_df["Time (corrected)"]), "The merge will give wrong results!"
    # Calculate distance between the feeding and the persistent peak
    distance_start = (merged_start_df["Time (corrected)"] - merged_start_df["time_start"]).dt.total_seconds()
    distance_end = (merge_end_df["Time (corrected)"] - merge_end_df["time_end"]).dt.total_seconds()
    merged_start_df['time_difference'] = distance_start.where(distance_start.abs() < distance_end.abs(),
                                                              distance_end)
    # If calculated time is in feeding time, set value to 0
    merged_start_df.loc[(merged_start_df["Time (corrected)"] >= merged_start_df["time_start"]) & (
            merged_start_df["Time (corrected)"] <= merged_start_df["time_end"]), 'time_difference'] = 0

    time_df = merged_start_df[["Time (corrected)", "time_difference", "rank_within_day"]]
    # Translate time from seconds back to hours
    time_df['time_difference_hours'] = time_df['time_difference'] / 3600

    time_df['date'] = time_df['Time (corrected)'].dt.date
    return time_df


def plot_both_act_speed_time_diffs_in_one_boxplot(include_irregular_phases=False):
    """Plots Figure 4"""
    df_act = init_standard_data(include_random_phases=True)
    peaks_df_act = calculate_persistence(df_act.copy(), 3, 0, type="activity")
    df_speed = init_speed_data(include_random_phases=True)
    peaks_df_speed = calculate_persistence(df_speed.copy(), 3, 0, type="speed")
    # Calculate time diff between feeding and persistent peaks
    time_df_act = plot_rank_diff_against_feeding_time(peaks_df_act.copy())
    time_df_act['section'] = time_df_act.apply(assign_experiment_section, axis=1)
    time_df_speed = plot_rank_diff_against_feeding_time(peaks_df_speed.copy())
    time_df_speed['section'] = time_df_speed.apply(assign_experiment_section, axis=1)
    time_df_act["type"] = "Activity"
    time_df_speed["type"] = "Speed"
    df = pd.concat([time_df_act, time_df_speed], ignore_index=True)
    df = df.drop(columns=["Time (corrected)", "time_difference", "date"])
    if not include_irregular_phases:
        df = df.loc[df["section"] != "Irregular Phase 1"]
        df = df.loc[df["section"] != "Irregular Phase 2"]

    # STATS 4.1
    fig = px.box(df, x='type', y='time_difference_hours', color='rank_within_day', facet_col='section',
                 color_discrete_sequence=ProjectConstants.COLOR_LIST_PEAKS)
    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("section=", "")))
    fig.for_each_annotation(lambda x: x.update(textangle=10))
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("section=", "")))

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_layout(yaxis_title='Time Difference [h]')
    fig.update_layout(legend_title_text='Rank Within<br>24-Hour Day')
    fig.update_layout(width=750, height=250)
    # Add x axis title (really workaround)
    fig.update_xaxes(title_text='')
    for i in [1, 2, 4, 5]:
        fig["layout"][f"xaxis{i}"].update(title_text='')
    fig.update_layout(xaxis3=dict(title_text='Data Type'))
    fig.update_layout(title_x=0.5)
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=55, r=35, b=40, t=45)))

    # STATS 4.2, see src/statistics/boxplots_stats_within_type.csv for the only significance
    # Plotly cannot draw the significance for us, so we have to look and see to match add the star etc.
    # correctly for the pdf file
    x_1 = 0.31915
    x_2 = 0.5232
    x_coords = [x_1, x_1, x_2, x_2]
    y_coords = [10, 12, 12, 10]
    for i in range(1, len(x_coords)):
        fig.add_shape(
            type="line",
            xref="paper",
            x0=x_coords[i - 1],
            y0=y_coords[i - 1],
            x1=x_coords[i],
            y1=y_coords[i],
            line=dict(color='rgba(0,0,0,1)', width=1.5), opacity=1
        )
    fig.add_annotation(text="<br>*<br>",
                       xref="paper",
                       x=(x_1 + x_2) / 2, y=12.3, showarrow=False,
                       )
    # STATS 4.2, see src/statistics/boxplots_stats_False.csv for significance
    x_1 = 0.84435
    x_2 = 0.93115
    x_coords = [x_1, x_1, x_2, x_2]
    y_coords = [8, 10, 10, 8]
    for i in range(1, len(x_coords)):
        fig.add_shape(
            type="line",
            xref="paper",
            x0=x_coords[i - 1],
            y0=y_coords[i - 1],
            x1=x_coords[i],
            y1=y_coords[i],
            line=dict(color='rgba(0,0,0,1)', width=1.5), opacity=1
        )
    fig.add_annotation(text="<br>*<br>",
                       xref="paper",
                       x=(x_1 + x_2) / 2 + 0.012, y=10.3, showarrow=False,
                       )
    fig.update_layout(template="plotly_white")
    fig.write_image(ProjectConstants.PLOTS.joinpath("figure_4").with_suffix(".pdf").as_posix())
    fig.show()
