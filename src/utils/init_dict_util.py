from utils.csv_features_util import target_list
from data_class.display_data import DisplayInfo


def init_dict(display_id, target, data_dict):
    if target == target_list[0]:
        data_dict[display_id] = {"count": 0}
    elif target == target_list[1]:
        data_dict[display_id] = {"M": 0, "F": 0}
    elif target == target_list[2]:
        data_dict[display_id] = {
            "age_0_20": 0,
            "age_20_40": 0,
            "age_40_60": 0,
            "age_60_above": 0,
        }
    elif target == target_list[3]:
        data_dict[display_id] = {
            "age_0_20_Male": 0,
            "age_0_20_Female": 0,
            "age_20_40_Male": 0,
            "age_20_40_Female": 0,
            "age_40_60_Male": 0,
            "age_40_60_Female": 0,
            "age_60_above_Male": 0,
            "age_60_above_Female": 0,
        }
    else:
        raise ValueError


def init_time_dict(display_id, data_dict):
    data_dict[display_id] = {"exposed": 0, "watched": 0, "attention": 0}


def init_dict_target():
    return {
        "person_id": 0,
        "gender": {"F": 0, "M": 0},
        "age": {"age_0_20": 0, "age_20_40": 0, "age_40_60": 0, "age_60_above": 0},
        "age_and_gender": {
            "age_0_20_Male": 0,
            "age_0_20_Female": 0,
            "age_20_40_Male": 0,
            "age_20_40_Female": 0,
            "age_40_60_Male": 0,
            "age_40_60_Female": 0,
            "age_60_above_Male": 0,
            "age_60_above_Female": 0,
        },
        "time": {"exposed": 0, "watched": 0, "attention": 0},
        "ad_id": 0,
    }


def init_display_info(display_name, display_id, date_str):
    year, month, day = date_str[:4], date_str[4:6], date_str[6:]
    return DisplayInfo(display_name, display_id, year, month, day)


def init_road_dict():
    return {
        "road_info": {
            "average_speed": None,
            "min_speed": None,
            "max_speed": None,
            "road_length": None,
            "road_span_time": 0,
        },
        "time_series": {},
        "time_in_diff": {},
    }
