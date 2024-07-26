import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data
from src.utils.filter_util import reduce_two_dfs_to_common_index
from src.utils.project_constants import ProjectConstants


def make_cross_correlation(time_series_1, time_series_2, save_figure_with_file_name: str = None):
    cross_corr = np.correlate(time_series_1 - np.mean(time_series_1),
                              time_series_2 - np.mean(time_series_2),
                              mode="full") / (
                         np.std(time_series_1) * np.std(time_series_2) * len(time_series_1))

    max_ts_length = len(time_series_1) + len(time_series_2) - 1
    lags = np.arange(int(-(max_ts_length) / 2), int((max_ts_length + 1) / 2))

    conf = 0.95  # confidence interval, qnorm((1 + ci)/2)/sqrt(x$n.used) formula used in stats:::plot.acf in ccf function
    conf_interval = norm.ppf((1 + conf) / 2) / np.sqrt(len(time_series_1))  # 1.96 / sqrt(n) is the significance line!
    print(f"{conf_interval=}")
    assert len(lags) == len(cross_corr), f"Number of x and y values differ! {len(lags), len(cross_corr)}"
    fig = go.Figure()
    fig.add_trace(go.Bar(x=lags, y=cross_corr, name='Cross-Correlation'))
    fig.update_layout(
        xaxis=dict(title='Lags [10 minutes]',
                   range=[-6 * 24, 6 * 24]
                   ),
        yaxis=dict(title='Cross-Correlation')
    )
    fig.add_trace(go.Scatter(x=lags, y=[conf_interval] * len(lags),
                             mode='lines', line=dict(dash='dash'), name='Upper Significance Line'))

    fig.add_trace(go.Scatter(x=lags, y=[-conf_interval] * len(lags),
                             mode='lines', line=dict(dash='dash'), name='Lower Significance Line'))

    if save_figure_with_file_name:
        fig.update_layout(width=1200, height=400)
        fig.update_layout(go.Layout(margin=go.layout.Margin(l=65, r=5, b=60, t=25)))
        fig.update_layout(template='plotly_white')
        fig.write_image(ProjectConstants.PLOTS.joinpath(save_figure_with_file_name).with_suffix(".pdf").as_posix())
        fig.show()


def plot_cross_correlation():
    """Plots Figure S3"""
    df_act = init_standard_data(include_random_phases=True)
    df_speed = init_speed_data(include_random_phases=True)
    df_act, df_speed = reduce_two_dfs_to_common_index(df_act, df_speed)
    make_cross_correlation(df_act['activity'], df_speed['speed'],
                           save_figure_with_file_name="supp_figure_3")
