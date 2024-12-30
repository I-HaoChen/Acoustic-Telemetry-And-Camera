from src.autocorrelation import run_autocorrelation_analysis
from src.cross_correlation import plot_cross_correlation
from src.fab_analysis import plot_fab_analysis
from src.feeding_time_visualisation import create_feeding_graph
from src.mean_around_feeding import plot_means_around_feeding_with_all
from src.peak_analysis import plot_whole_act_speed_time_series_with_peaks, \
    plot_one_feeding_phase_act_time_series_with_peaks
from src.peak_analysis_boxplot import plot_both_act_speed_time_diffs_in_one_boxplot
from src.persistent_homology_example import plot_superlevel_set_example
from src.statistics import run_stationarity_test, run_statistics_peaks_act_and_speed, run_statistics_on_faa, \
    run_t_test_mean_stats
from src.wavelets import plot_wavelet_spectrum_activity, plot_wavelet_spectrum_speed_supp


def create_figure_1():
    plot_whole_act_speed_time_series_with_peaks()


def create_figure_2():
    plot_one_feeding_phase_act_time_series_with_peaks()


def create_figure_3():
    plot_superlevel_set_example()


def create_figure_4():
    plot_both_act_speed_time_diffs_in_one_boxplot()


def create_figure_6ab():
    run_autocorrelation_analysis()


def create_figure_7():
    plot_wavelet_spectrum_activity()


def create_figure_8():
    plot_means_around_feeding_with_all()


def create_figure_9():
    plot_fab_analysis()


def create_figure_S1():
    create_feeding_graph()


def create_figure_S2():
    plot_wavelet_spectrum_speed_supp()


def create_figure_S3():
    plot_cross_correlation()


def run_stats_1():
    run_stationarity_test()


def run_stats_2():
    run_statistics_peaks_act_and_speed()


def run_stats_3():
    run_statistics_on_faa()


def run_stats_4():
    run_t_test_mean_stats()


def create_paper_figures():
    print("Figures for paper are being created...")
    create_figure_1()
    create_figure_2()
    create_figure_3()
    create_figure_4()
    create_figure_6ab()
    create_figure_7()
    create_figure_8()
    create_figure_9()
    print("Supplementary Figures for paper are being created...")
    create_figure_S1()
    create_figure_S2()
    create_figure_S3()


def run_all_statistics():
    print("Running all statistics...")
    run_stats_1()
    run_stats_2()
    run_stats_3()
    run_stats_4()


if __name__ == "__main__":
    create_paper_figures()
    run_all_statistics()
