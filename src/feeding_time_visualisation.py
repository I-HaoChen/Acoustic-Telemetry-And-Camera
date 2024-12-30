import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.data_loader import init_standard_data
from src.utils.feeding_times import load_feeding_times
from src.utils.project_constants import ProjectConstants


def create_feeding_graph():
    """Plots Figure S1"""
    df = init_standard_data(include_random_phases=True)
    df["date"] = df.index.date

    start = df["date"].min()
    end = df["date"].max()
    feeding_times = load_feeding_times()
    feeding_times = feeding_times[feeding_times["date"].between(start, end)]
    feeding_times = feeding_times.explode("feeding_times")
    feeding_times["feeding_n"] = feeding_times.groupby("date").cumcount() + 1
    feeding_times = feeding_times.explode("feeding_times")
    feeding_times["feeding_times"] = pd.to_datetime(feeding_times["feeding_times"])
    fig = go.Figure()
    red_color = px.colors.qualitative.D3[3]
    green_color = px.colors.qualitative.D3[2]
    colours = [green_color] * 16 + [red_color] * 4 + [green_color] * 15 + [red_color] + [green_color] * 7
    for idx, (_, feeding_group) in enumerate(feeding_times.groupby(["date"])):
        color = colours[idx]
        for _, feeding_n in feeding_group.groupby(["feeding_n"]):
            fig.add_trace(
                go.Scatter(
                    mode='markers+lines',
                    x=feeding_n['feeding_times'],
                    y=feeding_n['date'],
                    marker=dict(color=color),
                    showlegend=False
                ),
            )
    fig.add_trace(
        go.Scatter(x=[None], y=[None], name="Normal Feeding", marker=dict(color=green_color), legendgroup="Feeding",
                   legendgrouptitle_text="Feeding Mode"))
    fig.add_trace(go.Scatter(x=[None], y=[None], name="Irregular Feeding", marker=dict(color=red_color)))

    fig.update_yaxes(
        range=[pd.to_datetime(end) + pd.Timedelta(days=1), pd.to_datetime(start) - pd.Timedelta(days=1)])
    fig.update_yaxes(ticklabelposition="outside left")
    fig.update_yaxes(tickmode='linear', dtick=86400000.0 * 3)
    fig.update_layout(yaxis_tickformat='%d %b')

    fig.update_xaxes(tickmode='array', ticklabelposition='outside', ticklen=10)
    fig.update_layout(xaxis_tickformat='%H:%M')
    fig.update_xaxes(range=[pd.to_datetime('00:00:00'), pd.to_datetime('23:59:59')])
    fig.update_layout(margin={'t': 0, 'b': 0, 'l': 75})
    fig.update_layout(
        yaxis_title='Date',
        xaxis_title='Time',
    )
    fig.update_layout(template="plotly_white")
    fig.update_layout(width=1000, height=350)
    fig.write_image(ProjectConstants.PLOTS.joinpath("supp_figure_1").with_suffix(".pdf").as_posix())
    fig.show()
