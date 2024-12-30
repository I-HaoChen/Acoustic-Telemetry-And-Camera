import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pywt

from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data, spline_interpolation_of_speed_data
from src.utils.project_constants import ProjectConstants


def plot_make_wavelet_spectrum(series_with_datetime_index, scales, wavelet, title='Wavelet Power Spectrum'):
    # Calculate the power spectrum
    coefficients, freq = pywt.cwt(series_with_datetime_index, scales, wavelet)
    power_spectrum = (np.abs(coefficients)) ** 2

    fig = go.Figure(data=go.Heatmap(
        z=power_spectrum,
        x=series_with_datetime_index.index,
        y=1 / freq / 6,
        colorscale='viridis',
        colorbar=dict(title='Power')
    ))

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Period [h]',
        showlegend=False,
    )

    not_included_list = ["Whole experiment"]
    for section_1, section_2 in zip(ProjectConstants.EXPERIMENT_SECTIONS_DICT.items(),
                                    list(ProjectConstants.EXPERIMENT_SECTIONS_DICT.items())[1:]):
        # Drawing the different phases of the experiments as colorbar in the rop area of the Figure
        y = 40
        if section_1[0] in not_included_list:
            continue
        if section_2[0] in not_included_list:
            continue
        second_date = section_2[1][0]
        if section_1[0] == "Twilight Feeding":
            second_date = pd.Timestamp('2023-07-12 23:59:59')
        if section_1[0] in ["Irregular Phase 1", "Irregular Phase 2"]:
            y = 45
        fig.add_annotation(x=section_1[1][0] + (second_date - section_1[1][0]) / 2, y=y, showarrow=False,
                           text=f"<b>{section_1[0]}<b>", bgcolor="white")
        if section_1[0] in ["8:00 Feeding", "7:30 and 13:30 Feeding", "Twilight Feeding"]:
            color = "blue"
        elif section_1[0] in ["Fasting 1", "Fasting 2"]:
            color = "red"
        else:
            color = "yellow"
        fig.add_shape(type='rect', x0=section_1[1][0], x1=second_date,
                      y0=40, y1=40,
                      line=dict(color=color, width=5))

    fig.update_layout(width=1000, height=350)
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=50, r=50, b=50, t=10)))
    fig.update_layout(template="plotly_white")
    fig.write_image(
        ProjectConstants.PLOTS.joinpath(title).with_suffix(".pdf").as_posix())
    fig.show()


def plot_wavelet_spectrum_activity():
    """Plots Figure 7"""
    df_act = init_standard_data(include_random_phases=True)
    # Use morlet wavelets
    wavelet = 'morl'
    days = 2
    # Calibration for hours of the day
    scales = np.arange(1, 144 * days + 1)
    # Activity Wavelet Power Spectrum
    plot_make_wavelet_spectrum(df_act["activity"], scales, wavelet, "figure_7")


def plot_wavelet_spectrum_speed_supp():
    """Plots Figure S2"""
    df_speed = init_speed_data(include_random_phases=True)
    # Use morlet wavelets
    wavelet = 'morl'
    days = 2
    # Calibration for hours of the day
    scales = np.arange(1, 144 * days + 1)
    # Speed Wavelet Power Spectrum
    plot_make_wavelet_spectrum(df_speed["speed"], scales, wavelet, "supp_figure_2a")
    # Speed (nan filled with spline interpolation (edges with 0 padding) Wavelet Power Spectrum
    plot_make_wavelet_spectrum(spline_interpolation_of_speed_data(df_speed).fillna(0)["speed"], scales, wavelet,
                               "supp_figure_2b")
