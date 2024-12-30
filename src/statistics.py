import time
from datetime import datetime
from datetime import time as time_stuff

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import kruskal, stats, levene, shapiro
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.tsa.stattools import kpss

from src.fab_analysis import identify_lasting_peaks
from src.mean_around_feeding import mean_around_feeding
from src.peak_analysis import calculate_persistence
from src.peak_analysis_boxplot import plot_rank_diff_against_feeding_time
from src.utils.data_loader import init_standard_data
from src.utils.data_loader_speed import init_speed_data, zero_interpolation_of_speed_data, \
    spline_interpolation_of_speed_data
from src.utils.feeding_times import load_feeding_times
from src.utils.filter_util import assign_experiment_section, filter_by_valid_days
from src.utils.project_constants import ProjectConstants


def run_stationarity_test():
    df_act = init_standard_data(include_random_phases=True)
    df_depth = init_standard_data(include_random_phases=True, data_type="Depth [m] (est. or from tag)")
    df_temp = init_standard_data(include_random_phases=True, data_type="temperature")
    df_speed = init_speed_data(include_random_phases=True)
    # STATS 1: activity, depth and speed are stationary, temperature is not stationary!

    # Test for stationarity - Augmented Dickey-Fuller test
    adfuller1 = sm.tsa.stattools.adfuller(df_act["activity"])
    print(f"{adfuller1=}")  # Stats 1: stationary
    adfuller2 = sm.tsa.stattools.adfuller(df_speed["speed"])
    print(f"{adfuller2=}")  # Stats 1: stationary
    adfuller3 = sm.tsa.stattools.adfuller(df_depth["Depth [m] (est. or from tag)"])
    print(f"{adfuller3=}")  # Stats 1: stationary
    adfuller4 = sm.tsa.stattools.adfuller(df_temp["temperature"])
    print(f"{adfuller4=}")  # Stats 1: NOT stationary

    # Test for stationarity - KPSS test
    kpsstest1 = kpss(df_act["activity"])
    print(f"{kpsstest1=}")  # Stats 1: stationary
    kpsstest2 = kpss(df_speed["speed"])
    print(f"{kpsstest2=}")  # Stats 1: stationary
    kpsstest3 = kpss(df_depth["Depth [m] (est. or from tag)"])
    print(f"{kpsstest3=}")  # Stats 1: stationary
    kpsstest4 = kpss(df_temp["temperature"])
    print(f"{kpsstest4=}")  # Stats 1: NOT stationary

    # Testing the df_speed variants with different spline
    print("Testing the speed variations with splines...")
    df_speed_interpolated = zero_interpolation_of_speed_data(df_speed.copy())
    df_speed_interpolated_spline = spline_interpolation_of_speed_data(df_speed.copy()).fillna(0)

    adfuller_speed_1 = sm.tsa.stattools.adfuller(df_speed_interpolated["speed"])
    print(f"{adfuller_speed_1=}")  # Stats 1: stationary
    adfuller_speed_2 = sm.tsa.stattools.adfuller(df_speed_interpolated_spline["speed"])
    print(f"{adfuller_speed_2=}")  # Stats 1: stationary

    kpsstest_speed_1 = kpss(df_speed_interpolated["speed"])
    print(f"{kpsstest_speed_1=}")  # Stats 1: stationary
    kpsstest_speed_2 = kpss(df_speed_interpolated_spline["speed"])
    print(f"{kpsstest_speed_2=}")  # Stats 1: stationary


def run_statistics_peaks_act_and_speed():
    # STATS 2.0: Peak 1 speed difference between Fasting 1 and "7:30 and 13:30 Feeding" is significant
    # STATS 2.1: Difference between peak 1 of activity and peak 1 of speed in Twilight phase is significant
    # Preparing the time difference dfs
    df_act = init_standard_data(include_random_phases=False)
    peaks_df_act = calculate_persistence(df_act.copy(), 3, 0, type="activity")
    df_speed = init_speed_data(include_random_phases=False)
    peaks_df_speed = calculate_persistence(df_speed.copy(), 3, 0, type="speed")
    # Calculate time diff between feeding and persistent peaks
    time_df_act = plot_rank_diff_against_feeding_time(peaks_df_act.copy())
    time_df_act['section'] = time_df_act.apply(assign_experiment_section, axis=1)
    time_df_speed = plot_rank_diff_against_feeding_time(peaks_df_speed.copy())
    time_df_speed['section'] = time_df_speed.apply(assign_experiment_section, axis=1)
    time_df_act["type"] = "activity"
    time_df_speed["type"] = "speed"
    df = pd.concat([time_df_act, time_df_speed], ignore_index=True)
    df = df.drop(columns=["Time (corrected)", "time_difference", "date"])
    # Test for difference - Kruskal Wallis test
    # Testing between rank and section
    stats_df = pd.DataFrame()
    for (data_type, group_rank), group_df in df.groupby(["type", "rank_within_day"]):
        for group_1, group_2 in ProjectConstants.VALID_EXPERIMENT_DAYS_WITH_PAUSES_PAIRS:
            group_df_1 = group_df.loc[group_df["section"] == group_1]["time_difference_hours"]
            group_df_2 = group_df.loc[group_df["section"] == group_2]["time_difference_hours"]
            stats_kruskal, p_value_kruskal = kruskal(group_df_1, group_df_2)

            stats_df = pd.concat([stats_df, pd.DataFrame(
                {"Section A": [group_1], "Section B": [group_2], "Rank": [group_rank],
                 "Data Type": [data_type],
                 "Kruskal-Wallis H Statistic (H)": [round(stats_kruskal, 4)],
                 "DoF": 1,
                 "p-value": [round(p_value_kruskal, 4)],
                 "Significance": ["Yes" if p_value_kruskal < 0.05 else "No"],
                 })], ignore_index=True)
    stats_df.to_csv(
        ProjectConstants.STATISTICS.joinpath(f"boxplots_stats_between_phases").with_suffix(".csv").as_posix(),
        index=False)

    # Test for difference - Kruskal Wallis test
    # Testing between data types within the same section
    stats_df = pd.DataFrame()
    for group_section in ProjectConstants.VALID_EXPERIMENT_DAYS_WITH_PAUSES:
        sectioned_df = df.loc[df["section"] == group_section]
        for (group_rank), group_df in sectioned_df.groupby(["rank_within_day"]):
            group_act = group_df.loc[group_df["type"] == "activity"]["time_difference_hours"]
            group_speed = group_df.loc[group_df["type"] == "speed"]["time_difference_hours"]
            stats_kruskal, p_value_kruskal = kruskal(group_act, group_speed)
            stats_df = pd.concat([stats_df, pd.DataFrame(
                {"Section": [group_section], "Rank": [group_rank],
                 "Kruskal-Wallis H Statistic (H)": [round(stats_kruskal, 4)],
                 "DoF": 1,
                 "p-value": [round(p_value_kruskal, 4)],
                 "Significance": ["Yes" if p_value_kruskal < 0.05 else "No"],
                 })], ignore_index=True)
    stats_df.to_csv(
        ProjectConstants.STATISTICS.joinpath(f"boxplots_stats_between_types").with_suffix(".csv").as_posix(),
        index=False)


def feeding_list_to_expanded_df(faa_list):
    faa_df = pd.concat([pd.DataFrame(sublist) for sublist in faa_list], axis=0)
    faa_df["date"] = faa_df["faa_start"].dt.date

    faa_df_expanded = pd.DataFrame(columns=["Time (corrected)"])
    for _, row in faa_df.iterrows():
        start = row['faa_start']
        end = row['faa_end']

        faa_df_expanded = pd.concat([faa_df_expanded,
                                     pd.DataFrame(pd.date_range(start, end, freq='10min'),
                                                  columns=['Time (corrected)'])])
    return faa_df_expanded


def run_statistics_on_faa(cutoff_additional_hours=2, duration_threshold_minutes=60):
    # STATS 3 cutoff_additional_hours = 0,1,2 and duration_threshold_minutes=60, 120
    # makes no difference, still same significant result
    df_act = init_standard_data(include_random_phases=True)
    df_act = df_act.reset_index()

    df_speed = init_speed_data(include_random_phases=True)
    formatting_data_start = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-06-02 00:00:00']))
    formatting_data_end = pd.DataFrame({'speed': [np.nan]}, index=pd.to_datetime(['2023-07-12 23:50:00']))
    df_speed = pd.concat([df_speed.copy(), formatting_data_start, formatting_data_end]).asfreq(freq='10min')
    df_speed = df_speed.reset_index(names="Time (corrected)")

    df_speed = df_speed.reset_index()

    faa_list_act_feeding = identify_lasting_peaks(df_act, 10, duration_threshold_minutes=duration_threshold_minutes,
                                                  quantile=0.5, data_type="activity",
                                                  cutoff_additional_hours=cutoff_additional_hours,
                                                  only_untiL_feeding=True)
    faa_list_speed_feeding = identify_lasting_peaks(df_speed, 10, duration_threshold_minutes=duration_threshold_minutes,
                                                    quantile=0.2, data_type="speed",
                                                    cutoff_additional_hours=cutoff_additional_hours,
                                                    only_untiL_feeding=True)
    faa_act_expanded = feeding_list_to_expanded_df(faa_list_act_feeding)
    faa_speed_expanded = feeding_list_to_expanded_df(faa_list_speed_feeding)
    print("######## Statistics with all phases ########")
    feeding_times = load_feeding_times()
    feeding_times["datum"] = feeding_times["date"]
    feeding_times = filter_by_valid_days(feeding_times)
    first_last_act_speed_df = pd.DataFrame(
        columns=["date", "feeding_event", "who_first", "value_first", "who_last", "value_last"])
    for date, feedings in feeding_times.groupby(["date"]):
        for feeding_events in feedings["feeding_times"]:
            for feeding_event in feeding_events:
                feeding_start = datetime.combine(date, time_stuff.fromisoformat(feeding_event[0]))
                feeding_end = datetime.combine(date, time_stuff.fromisoformat(feeding_event[1]))
                faa_act_of_the_day = faa_act_expanded.loc[faa_act_expanded["Time (corrected)"].dt.date == date]
                faa_speed_of_the_day = faa_speed_expanded.loc[faa_speed_expanded["Time (corrected)"].dt.date == date]

                prev_timestamp = feeding_start - pd.Timedelta(minutes=10)
                minutes_to_add = (10 - prev_timestamp.minute % 10) if prev_timestamp.minute % 10 != 0 else 0
                prev_timestamp = prev_timestamp + pd.Timedelta(minutes=minutes_to_add)
                while faa_act_of_the_day['Time (corrected)'].isin([prev_timestamp]).any():
                    prev_timestamp -= pd.Timedelta(minutes=10)
                act_first = prev_timestamp + pd.Timedelta(minutes=10)

                prev_timestamp = feeding_start - pd.Timedelta(minutes=10)
                minutes_to_add = (10 - prev_timestamp.minute % 10) if prev_timestamp.minute % 10 != 0 else 0
                prev_timestamp = prev_timestamp + pd.Timedelta(minutes=minutes_to_add)
                while faa_speed_of_the_day['Time (corrected)'].isin([prev_timestamp]).any():
                    prev_timestamp -= pd.Timedelta(minutes=10)
                speed_first = prev_timestamp + pd.Timedelta(minutes=10)

                if act_first < speed_first:
                    value_first = act_first
                    who_first = "act"
                elif act_first > speed_first:
                    value_first = speed_first
                    who_first = "speed"
                else:
                    value_first = act_first  # or speed_first
                    who_first = "same"

                prev_timestamp = feeding_end + pd.Timedelta(hours=cutoff_additional_hours) + pd.Timedelta(minutes=10)
                prev_timestamp = prev_timestamp - pd.Timedelta(minutes=prev_timestamp.minute % 10)
                while faa_act_of_the_day['Time (corrected)'].isin([prev_timestamp]).any():
                    prev_timestamp += pd.Timedelta(minutes=10)
                act_last = prev_timestamp - pd.Timedelta(minutes=10)

                prev_timestamp = feeding_end + pd.Timedelta(hours=cutoff_additional_hours) + pd.Timedelta(minutes=10)
                prev_timestamp = prev_timestamp - pd.Timedelta(minutes=prev_timestamp.minute % 10)
                while faa_speed_of_the_day['Time (corrected)'].isin([prev_timestamp]).any():
                    prev_timestamp += pd.Timedelta(minutes=10)
                speed_last = prev_timestamp - pd.Timedelta(minutes=10)

                if act_last > speed_last:
                    value_last = act_last
                    who_last = "act"
                elif act_last < speed_last:
                    value_last = speed_last
                    who_last = "speed"
                else:
                    value_last = act_last  # or speed_last
                    who_last = "same"
                first_last_act_speed_df = pd.concat(
                    [first_last_act_speed_df, pd.DataFrame({"date": [date], "feeding_event": [feeding_event[0]],
                                                            "who_first": who_first, "value_first": [value_first],
                                                            "who_last": [who_last], "value_last": [value_last]})])
    print(first_last_act_speed_df)
    time.sleep(1)
    seq_length = len(first_last_act_speed_df)
    act_count = len(first_last_act_speed_df.loc[first_last_act_speed_df["who_first"] == "act"])
    speed_count = len(first_last_act_speed_df.loc[first_last_act_speed_df["who_first"] == "speed"])

    act_proportion_first = act_count / seq_length
    speed_proportion_first = speed_count / seq_length

    # Two-proportion z-test, STATS 3 // All significant for cutoff_hours in 0,1,2 and FAA duration 60,120
    z_score, p_value = proportions_ztest([act_count, speed_count], [seq_length, seq_length])
    print(len(first_last_act_speed_df))
    print(f"Proportion of 'act' occurrences that were first: {act_proportion_first:.2f}")
    print(f"Proportion of 'speed' occurrences that were first: {speed_proportion_first:.2f}")
    print(f"z-score: {z_score:.4f}")
    print(f"p-value: {p_value:.4f}")
    if p_value < 0.05:
        if act_count > speed_count:
            print("The difference is statistically significant. 'act' is significantly more often first.")
        else:
            print(
                "SOMETHING WENT WRONG! WE DO NOT HAVE SIGNIFICANCE! CHECK THE DATA AGAIN")
    else:
        print(
            "SOMETHING WENT WRONG! WE DO NOT HAVE SIGNIFICANCE! CHECK THE DATA AGAIN")

    seq_length = len(first_last_act_speed_df)
    act_count = len(first_last_act_speed_df.loc[first_last_act_speed_df["who_last"] == "act"])
    speed_count = len(first_last_act_speed_df.loc[first_last_act_speed_df["who_last"] == "speed"])

    act_proportion_last = act_count / seq_length
    speed_proportion_last = speed_count / seq_length

    # Two-proportion z-test, STATS 3 // All significant for cutoff_hours in 0,1,2 and FAA duration 60,120
    z_score, p_value = proportions_ztest([act_count, speed_count], [seq_length, seq_length])
    print(f"Proportion of 'act' occurrences that were last: {act_proportion_last:.2f}")
    print(f"Proportion of 'speed' occurrences that were last: {speed_proportion_last:.2f}")
    print(f"z-score: {z_score:.4f}")
    print(f"p-value: {p_value:.4f}")
    if p_value < 0.05:
        if speed_count > act_count:
            print("The difference is statistically significant. 'speed' is significantly more often last.")
        else:
            print(
                "SOMETHING WENT WRONG! WE DO NOT HAVE SIGNIFICANCE! CHECK THE DATA AGAIN")
    else:
        print(
            "SOMETHING WENT WRONG! WE DO NOT HAVE SIGNIFICANCE! CHECK THE DATA AGAIN")


def run_related_t_test(df, data_type, section: str = None):
    # STATS 4
    section_df = df.loc[df["experiment_section"] == section]
    df_1 = section_df.loc[section_df["feeding_of_the_day"] == "1"]
    df_2 = section_df.loc[section_df["feeding_of_the_day"] == "2"]

    _, p_value_shap = shapiro(df_1["mean_for_feeding_period"])
    _, p_value_shap_2 = shapiro(df_2["mean_for_feeding_period"])

    _, p_value_levene = levene(df_1["mean_for_feeding_period"], df_2["mean_for_feeding_period"])

    t_statistic, p_value = stats.ttest_rel(df_1["mean_for_feeding_period"],
                                           df_2["mean_for_feeding_period"])
    print(f"***** {data_type} {section} *****")
    print("Shapiro-Wilk p-values: ", p_value_shap, p_value_shap_2)
    print("Levene's p-value: ", p_value_levene)
    print('T-statistic:', t_statistic)
    print('P-value:', p_value)

    alpha = 0.05
    if alpha <= p_value_shap and alpha <= p_value_shap_2 and alpha <= p_value_levene:
        print("All assumptions are met! The significance below is valid!")
    else:
        print("At least one assumptions failed! Below results are to be taken with caution")
    if p_value < alpha:
        print(
            f'SIGNIFICANCE! There is a significant difference between {data_type} during the feeding 1 and feeding 2.')
    else:
        print(
            f'NOOOOOO. There is no significant difference between {data_type} during feeding 1 and feeding 2.')
    print("\n")


def run_t_test_mean_stats():
    df_act = init_standard_data(include_random_phases=False)
    df_depth = init_standard_data(include_random_phases=False, data_type="Depth [m] (est. or from tag)")
    df_act["datum"] = df_act.index
    df_act = filter_by_valid_days(df_act)

    df_depth["date"] = df_depth.index.date
    df_depth["datum"] = df_depth.index
    df_depth['experiment_section'] = df_depth.apply(assign_experiment_section, axis=1)

    df_speed = init_speed_data()
    df_speed["date"] = df_speed.index.date
    df_speed["datum"] = df_speed.index
    df_speed['experiment_section'] = df_speed.apply(assign_experiment_section, axis=1)

    mean_df_act = mean_around_feeding(df_act.copy(), 1, 2, type="activity", calc_mean=True)
    mean_df_depth = mean_around_feeding(df_depth.copy(), 1, 2, type="Depth [m] (est. or from tag)", calc_mean=True)
    mean_df_speed = mean_around_feeding(df_speed.copy(), 1, 2, type="speed", calc_mean=True)

    run_related_t_test(mean_df_act.copy(), data_type="activity", section="7:30 and 13:30 Feeding")
    run_related_t_test(mean_df_act.copy(), data_type="activity", section="Twilight Feeding")
    run_related_t_test(mean_df_depth.copy(), data_type="Depth [m] (est. or from tag)", section="7:30 and 13:30 Feeding")
    run_related_t_test(mean_df_depth.copy(), data_type="Depth [m] (est. or from tag)", section="Twilight Feeding")
    run_related_t_test(mean_df_speed.copy(), data_type="speed", section="7:30 and 13:30 Feeding")
    run_related_t_test(mean_df_speed.copy(), data_type="speed", section="Twilight Feeding")
