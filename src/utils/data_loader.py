import pandas
import pandas as pd

from src.utils.filter_util import cut_by_start_date, filter_by_snr, cut_by_end_date, \
    reduce_to_interpolated_values_with_sections_df
from src.utils.pinpoint_data_converter import convert_data2, exclude_all_outliers
from src.utils.project_constants import ProjectConstants
from src.utils.transmitter_datasheets import TransmitterDataSheet


def add_water_columns(df):
    df["water_column"] = "ERROR"
    df.loc[df["Depth [m] (est. or from tag)"] < 3, "water_column"] = "0-3m"
    df.loc[(3 <= df["Depth [m] (est. or from tag)"]) & (
            df["Depth [m] (est. or from tag)"] < 6), "water_column"] = "3-6m"
    df.loc[6 <= df["Depth [m] (est. or from tag)"], "water_column"] = "6-9m"
    return df


def init_standard_data(with_dates=True, use_cache=True, include_random_phases=False, data_type="activity"):
    if use_cache:
        try:
            df = pandas.read_pickle(
                ProjectConstants.DATA.joinpath(
                    f'cached_df_2023_{data_type}_{include_random_phases}.pkl').as_posix())
            print("Manual cache used!")
            return df
        except:
            print("Loading manually...")
    df = init_data([], all_fish=True, start_date="2023-06-02", end_date="2023-07-20",
                   snr_slider_values=[20, 100000], with_dates=with_dates)
    df['hour'] = df.index.get_level_values(1).hour
    df['minute'] = df.index.get_level_values(1).minute
    df['second'] = df.index.get_level_values(1).second
    df['time_numeric'] = df['hour'] + df['minute'] / 60 + df['second'] / 3600
    try:
        df = df[(df["datum"]) < pd.Timestamp(ProjectConstants.END_OF_EXPERIMENT_PERIOD_PAPER_EXCLUSIVE, tz="UTC")]
        df = df[df["datum"] > pd.Timestamp(ProjectConstants.FISH_EXPERIMENT_SECTION_1, tz="UTC")]
    except TypeError as e:
        df = df[(df["datum"]) < pd.Timestamp(ProjectConstants.END_OF_EXPERIMENT_PERIOD_PAPER_EXCLUSIVE)]
        df = df[df["datum"] > pd.Timestamp(ProjectConstants.FISH_EXPERIMENT_SECTION_1)]

    df = reduce_to_interpolated_values_with_sections_df(df, minutes=10, include_random_phases=include_random_phases,
                                                        data_type=data_type)
    if use_cache:
        df.to_pickle(
            ProjectConstants.DATA.joinpath(f'cached_df_2023_{data_type}_{include_random_phases}.pkl').as_posix())

    return df


def init_data(files, all_fish, start_date, end_date, snr_slider_values,
              with_dates=True) -> pandas.DataFrame:
    if all_fish:
        data_sheet = TransmitterDataSheet(empty=False)
    else:
        data_sheet = TransmitterDataSheet(empty=True)
        try:
            print(len(files))
            print(files)
            print(type(files))
            if len(files) == 1:
                for file in ProjectConstants.CONSTRAINED_TRANSMITTER_DATA.glob(files[0] + "*.csv"):
                    print(file)
                    data_sheet.add_one_csv_file(
                        ProjectConstants.CONSTRAINED_TRANSMITTER_DATA.joinpath(file).with_suffix(".csv"))
            else:
                for file in files:
                    print(f"Loading {file}")
                    for real_file in ProjectConstants.CONSTRAINED_TRANSMITTER_DATA.glob(file + "*.csv"):
                        print(real_file)
                        data_sheet.add_one_csv_file(
                            ProjectConstants.CONSTRAINED_TRANSMITTER_DATA.joinpath(real_file).with_suffix(".csv"))
        except (FileNotFoundError, TypeError):
            return pd.DataFrame()
    df = data_sheet.get_all_current_csv_files_as_one_df()
    if with_dates:
        df = cut_by_start_date(df, start_date)
        df = cut_by_end_date(df, end_date)
        print(f"Number of signals in the experiment window: {len(df)}")
    df = filter_by_snr(df, snr_slider_values[0], snr_slider_values[1])
    df = convert_data2(df)
    try:
        df = df.drop(columns=["Raw Data", "Data 1 unit", "Temperature / RMS (Data 2)", "Data 2", "Unix Timestamp (UTC)",
                              "Data 2 unit"])
    except KeyError as e:
        print("Tried to drop some columns, failed")
    df = exclude_all_outliers(df)
    return df


if __name__ == "__main__":
    df_act = init_standard_data(include_random_phases=True)
    print(df_act.head(2))
    print(df_act.tail(2))
    print(f"Standard data 2023 ({len(df_act)}) loaded")
