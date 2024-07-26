from pathlib import Path
from typing import Final

import pandas as pd
import plotly.express.colors as px_colors

ROOT_PATH = Path(__file__).parent.parent.parent


class ProjectConstants():
    ROOT: Final = ROOT_PATH
    DATA: Final = ROOT_PATH.joinpath("data")
    SRC: Final = ROOT_PATH.joinpath("src")
    YEAR_2023: Final = DATA.joinpath("2023")
    CONSTRAINED_TRANSMITTER_DATA = YEAR_2023.joinpath('Acoustic Transmitters Constrained')
    FEEDING_TIMES = YEAR_2023.joinpath('Feeding Times', 'feeding_schedule.json')
    FEEDING_TIMES_NO_BREAKS = YEAR_2023.joinpath('Feeding Times', 'feeding_schedule_nan_breaks.json')
    RECEIVER_DATA = YEAR_2023.joinpath('Receivers')
    PLOTS = SRC.joinpath("plots")
    STATISTICS = SRC.joinpath("statistics")
    CAMERA_DATA = YEAR_2023.joinpath("Camera Speed Data")

    START_OF_EXPERIMENT = pd.Timestamp(2023, 5, 2)  # Tag activation
    FISH_EXPERIMENT_SECTION_1 = pd.Timestamp(2023, 6, 2)  # Experiment protocol started
    FISH_EXPERIMENT_PAUSE_1 = pd.Timestamp(2023, 6, 13)
    FISH_EXPERIMENT_RANDOM_START = pd.Timestamp(2023, 6, 18)
    FISH_EXPERIMENT_RANDOM_END = pd.Timestamp(2023, 6, 21)
    FISH_EXPERIMENT_SECTION_2 = pd.Timestamp(2023, 6, 22)
    FISH_EXPERIMENT_PAUSE_2 = pd.Timestamp(2023, 7, 2)
    FISH_EXPERIMENT_RANDOM_2_START = pd.Timestamp(2023, 7, 7)
    FISH_EXPERIMENT_RANDOM_2_END = pd.Timestamp(2023, 7, 7)
    FISH_EXPERIMENT_SECTION_3 = pd.Timestamp(2023, 7, 8)
    FISH_EXPERIMENT_PAUSE_3 = pd.Timestamp(2023, 7, 18)

    END_OF_EXPERIMENT_INCLUSIVE = pd.Timestamp(2023, 7, 23)
    END_OF_EXPERIMENT_PERIOD_PAPER_EXCLUSIVE = pd.Timestamp(2023, 7, 13)

    EXPERIMENT_SECTIONS_DICT = {"8:00 Feeding": [FISH_EXPERIMENT_SECTION_1, FISH_EXPERIMENT_PAUSE_1],
                                "Fasting 1": [FISH_EXPERIMENT_PAUSE_1, FISH_EXPERIMENT_RANDOM_START],
                                "Irregular Phase 1": [FISH_EXPERIMENT_RANDOM_START,
                                                      FISH_EXPERIMENT_SECTION_2],
                                "7:30 and 13:30 Feeding": [FISH_EXPERIMENT_SECTION_2,
                                                           FISH_EXPERIMENT_PAUSE_2],
                                "Fasting 2": [FISH_EXPERIMENT_PAUSE_2,
                                              FISH_EXPERIMENT_RANDOM_2_START],
                                "Irregular Phase 2": [FISH_EXPERIMENT_RANDOM_2_START,
                                                      FISH_EXPERIMENT_SECTION_3],
                                "Twilight Feeding": [FISH_EXPERIMENT_SECTION_3,
                                                     FISH_EXPERIMENT_PAUSE_3],
                                "Fasting 3": [FISH_EXPERIMENT_PAUSE_3, END_OF_EXPERIMENT_INCLUSIVE],
                                "Whole experiment": [FISH_EXPERIMENT_SECTION_1,
                                                     END_OF_EXPERIMENT_PERIOD_PAPER_EXCLUSIVE],
                                }
    FEEDING_PHASES = ["8:00 Feeding", "7:30 and 13:30 Feeding", "Twilight Feeding"]
    VALID_EXPERIMENT_DAYS_WITH_PAUSES = ["8:00 Feeding", "Fasting 1", "7:30 and 13:30 Feeding",
                                         "Fasting 2", "Twilight Feeding"]
    VALID_EXPERIMENT_DAYS_WITH_PAUSES_PAIRS = [["8:00 Feeding", "Fasting 1"], ["Fasting 1", "7:30 and 13:30 Feeding"],
                                               ["7:30 and 13:30 Feeding", "Fasting 2"],
                                               ["Fasting 2", "Twilight Feeding"]]
    EXPERIMENT_ORDER_FOR_PANDAS_SORT = {
        "8:00 Feeding": 1,
        "Fasting 1": 2,
        "Irregular Phase 1": 3,
        "7:30 and 13:30 Feeding": 4,
        "Fasting 2": 5,
        "Irregular Phase 2": 6,
        "Twilight Feeding": 7,
        "Fasting 3": 8,
    }

    COLOR_LIST_GREEN = ["#006400", "#228b22", "#3cb371", "#00fa9a", "#7cfc00", "#adff2f"]  # Activity
    COLOR_LIST_ORANGE = ["#ff4500", "#ff8c00", "#ffa500", "#ffd700", "#ffff00", "#ffffe0"]  # Speed
    COLOR_LIST_BLUE = ["#0000cc", "#3f52b7", "#3f7bb7", "#7f96b3", "#8cb3d9", "#99ccff"]  # Depth
    COLOR_LIST_PEAKS = [px_colors.qualitative.Plotly[0], px_colors.qualitative.Plotly[3],
                        px_colors.qualitative.Plotly[2]]
    COLOR_LIST_GRAY = ["#999999", "#888888", "#777777", "#666666", "#555555", "#444444", "#333333", "#222222",
                       "#111111"]
    COLOR_LIST_BLACK = ["#000000"]

    @classmethod
    def all_key_value_items(cls):
        return {_key.upper(): _value for _key, _value in vars(cls).items() if _key.isupper()}.items()


if __name__ == "__main__":
    # Show all constants
    for key, value in ProjectConstants.all_key_value_items():
        print(f"{key}:{value}")
        if isinstance(value, Path):
            if not "." in value.name:
                value.mkdir(parents=True, exist_ok=True)
