import pandas as pd

from src.utils.project_constants import ProjectConstants


class TransmitterDataSheet:
    def __init__(self, empty=False):
        self._csv_files = {}
        if not empty:
            self._add_all_csv_files()

    def _add_all_csv_files(self):
        iterator = ProjectConstants.CONSTRAINED_TRANSMITTER_DATA.glob('*.csv')
        for file in iterator:
            self.add_one_csv_file(file)

    def add_one_csv_file(self, file):
        df_indexed = pd.read_csv(file, header=0, skipinitialspace=True)
        df_indexed["time_index"] = pd.to_datetime(df_indexed["Date and Time (UTC)"]) + pd.DateOffset(
            hours=3)  # Crete is +3 towards UTC!
        df_indexed["Time (corrected)"] = pd.to_datetime(df_indexed["Date and Time (UTC)"]) + pd.DateOffset(
            hours=3)  # Crete is +3 towards UTC!
        df_indexed = df_indexed.set_index(df_indexed["time_index"])
        datetime_series = pd.to_datetime(df_indexed.index)
        datetime_index = pd.DatetimeIndex(datetime_series.values)
        df_indexed["datum"] = datetime_index
        df_indexed_datetime = df_indexed.set_index(datetime_index)
        df_indexed_datetime = df_indexed_datetime[
                              ProjectConstants.START_OF_EXPERIMENT:
                              ProjectConstants.END_OF_EXPERIMENT_INCLUSIVE]
        df_indexed_datetime["SNR [dB]"] = df_indexed_datetime["SNR"]
        df_indexed_datetime.drop(columns=["SNR"])
        df_indexed_datetime["ID"] = df_indexed_datetime["Id"]
        df_indexed_datetime.drop(columns=["Id"])
        df_indexed_datetime["Depth [m] (est. or from tag)"] = df_indexed_datetime["Depth (Data 1)"]
        df_indexed_datetime.drop(columns=["Depth (Data 1)"])
        self._csv_files[file.stem] = df_indexed_datetime

    def get_all_current_csv_files_as_one_df(self):
        df = pd.concat(self._csv_files.values(), keys=self._csv_files.keys(), names=["fish_name", "dates"])
        df = self.add_fish_numbers(df)
        return df

    def add_fish_numbers(self, df):
        """Add unique ID to each fish (two tag numbers per fish)"""
        df["fish_number"] = -1
        for name in sorted(set(df["Name"])):
            identifier = int(name.split("-")[1])
            other_name = name.split("-")[0] + "-" + str(identifier + 1)
            if (df.loc[df["Name"] == name, "fish_number"] == -1).all():
                try:
                    df.loc[df["Name"] == name, "fish_number"] = identifier + 1
                    df.loc[df["Name"] == other_name, "fish_number"] = identifier + 1
                except ValueError:
                    pass
        return df
