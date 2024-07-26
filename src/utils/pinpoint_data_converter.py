import numpy as np
import pandas


def convert_data2(df: pandas.DataFrame) -> pandas.DataFrame:
    df = append_data2_is_activity_as_column_2023(df)
    df = append_data2_is_temperature_as_column_2023(df)
    df = calculate_activity_from_data2_2023(df)
    df = calculate_temperature_from_data2_2023(df)
    return df


def append_data2_is_activity_as_column_2023(df: pandas.DataFrame) -> pandas.DataFrame:
    """For all ODD number IDs for the dataset year 2023, the second part of data is carrying acceleration data"""
    df["is_activity"] = df["ID"] % 2 == 1
    assert (df.loc[df["is_activity"], "Data 2 unit"] == "ms-2").all()
    return df


def append_data2_is_temperature_as_column_2023(df: pandas.DataFrame) -> pandas.DataFrame:
    """For all EVEN number IDs for the dataset year 2023, the second part of data is carrying temperature data"""
    df["is_temperature"] = df["ID"] % 2 == 0
    assert (df.loc[df["is_temperature"], "Data 2 unit"] == "degC").all()
    return df


def calculate_activity_from_data2_2023(df: pandas.DataFrame) -> pandas.DataFrame:
    df["activity"] = -1
    df.loc[df["is_activity"], "activity"] = df.loc[df["is_activity"], "Temperature / RMS (Data 2)"]
    return df


def calculate_temperature_from_data2_2023(df: pandas.DataFrame) -> pandas.DataFrame:
    df["temperature"] = -1
    # t_min = 10, t_max = 35.5
    df.loc[df["is_temperature"], "temperature"] = df.loc[df["is_temperature"], "Temperature / RMS (Data 2)"]
    return df


def exclude_all_outliers(df: pandas.DataFrame, unconstrained: bool = False) -> pandas.DataFrame:
    for name in ["temperature"]:
        # Should exclude eleven points for temperature
        df = exclude_data2_or_depth_outliers(df, name, unconstrained=unconstrained)

    df = df.loc[df["Depth [m] (est. or from tag)"] <= 9]
    df = df.loc[0 <= df["Depth [m] (est. or from tag)"]]
    print(f"After final exclusion: {len(df)}")
    return df


def exclude_data2_or_depth_outliers(df: pandas.DataFrame, column_name: str, unconstrained=False) -> pandas.DataFrame:
    df["z_score_temp"] = 0
    if column_name == "temperature":
        df_small = df.loc[df["is_temperature"]]
    elif column_name == "activity":
        df_small = df.loc[df["is_activity"]]
    elif column_name == "Depth [m] (est. or from tag)":
        df_small = df
    else:
        raise AttributeError("No boolean given!")
    if unconstrained:
        for name, group in df_small.groupby(df_small.index.get_level_values(1)):
            df.loc[group.index, "z_score_temp"] = np.divide(group[column_name] - group[column_name].mean(),
                                                            group[column_name].std(ddof=0))
        df_lefties = df.loc[df["z_score_temp"] < 3]
        df_lefties = df_lefties.loc[-3 < df_lefties["z_score_temp"]]
        print(f"{len(df) - len(df_lefties)} outliers with (z_score > 3) excluded for column {column_name}")
        df_lefties = df_lefties.drop(columns=["z_score_temp"])
    else:
        for name, group in df_small.groupby("Name"):
            df.loc[group.index, "z_score_temp"] = np.divide(group[column_name] - group[column_name].mean(),
                                                            group[column_name].std(ddof=0))
        df_lefties = df.loc[df["z_score_temp"] < 3]
        df_lefties = df_lefties.loc[-3 < df_lefties["z_score_temp"]]
        print(f"{len(df) - len(df_lefties)} outliers with (z_score > 3) excluded for column {column_name}")
        df_lefties = df_lefties.drop(columns=["z_score_temp"])
    return df_lefties
