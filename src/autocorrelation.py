import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import acf

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.project_constants import ProjectConstants


def plot_write_acf(plot_title, df, type, lags, n_lagperiods, periodicity, find_p1_min,
                   find_p1_max):
    fig = make_subplots(rows=len(df.groupby(["section"])), cols=1, y_title='Autocorrelation', x_title='Lags',
                        subplot_titles=ProjectConstants.VALID_EXPERIMENT_DAYS_WITH_PAUSES)

    for idx, (section_name, group_df) in enumerate(df.groupby(["section"], sort=False), 1):
        group_df = group_df.sort_index()
        # Use statsmodels to calculate ACF
        acf_values, confidence_intervals = acf(group_df[type], nlags=len(group_df[type]) - 1,
                                               alpha=0.05)
        lower_y = confidence_intervals[:, 0] - acf_values
        upper_y = confidence_intervals[:, 1] - acf_values
        # Plot the autocorrelation
        fig.add_trace(
            go.Scatter(x=np.arange(len(acf_values)), y=acf_values, name=section_name), row=idx,
            col=1)
        p1_max = np.argmax(acf_values[find_p1_min:find_p1_max]) + find_p1_min
        # Plot the period of the autocorrelation
        fig.add_trace(
            go.Scatter(x=[0, p1_max], y=[acf_values[0], acf_values[p1_max]], marker_size=10, marker_color="red",
                       marker_symbol="x", text=["P0", "P1"], mode="markers+text", textposition="middle right"),
            row=idx, col=1)
        # Plot the 5% significance line
        fig.add_trace(go.Scatter(x=np.arange(len(acf_values)), y=upper_y, mode='lines',
                                 line_color='rgba(255,255,255,0)',
                                 showlegend=False), row=idx, col=1)
        fig.add_trace(go.Scatter(x=np.arange(len(acf_values)), y=lower_y, mode='lines',
                                 fillcolor='rgba(32, 146, 230,0.3)',
                                 fill='tonexty', line_color='rgba(255,255,255,0)'), row=idx, col=1)
        fig.update_yaxes(zerolinecolor='#000000')
        fig.update_yaxes(range=[-1, 1.25])
        fig.update_xaxes(range=[-10, lags * n_lagperiods])
        fig.update_layout(showlegend=False)
        # Add periodicity annotation
        fig.add_annotation(
            xref="paper", yref="paper",
            x=lags * n_lagperiods * 0.85, y=0.95,
            text=f"Period: {24 * p1_max * 1 / periodicity:0.2f}h" + ("<br>(P1-P0)" if idx == 1 else ""),
            showarrow=False,
            font=dict(size=12),
            row=idx, col=1
        )
    fig.update_layout(width=500, height=500)
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=65, r=5, b=60, t=25)))
    fig.update_layout(template="plotly_white")
    fig.write_image(
        ProjectConstants.PLOTS.joinpath(plot_title).with_suffix(".pdf").as_posix())
    fig.show()


def run_autocorrelation_analysis():
    """Plots Figure 6a and Figure 6b"""
    df_act = init_standard_data(include_random_phases=False)
    df_speed = init_speed_data(include_random_phases=False)
    plot_write_acf("figure_6a", df_act, "activity", 144, 3, 144, 70, 210)
    plot_write_acf("figure_6b", df_speed, "speed", 144, 3, 90, 50, 210)
