import os
import json
from utils.env_path_util import report_path
from utils.env_path_util import processed_path
from datetime import time


# 시간 데이터를 변환하는 함수
def convert_time_in_dict(data):
    if isinstance(data, dict):
        return {k: convert_time_in_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_time_in_dict(item) for item in data]
    elif isinstance(data, time):
        return data.strftime("%H:%M:%S")  # 시간 형식 변환
    else:
        return data


# 도로 gps + data csv 시간대 분류 데이터 저장
def save_road_json(display_name, display_id, total_dict):
    # total_dict 변환
    total_dict = convert_time_in_dict(total_dict)

    file_name = f"{display_name}_{display_id}_total_data.json"
    file_save_path = os.path.join(processed_path, display_name, display_id, "ROAD")
    os.makedirs(file_save_path, exist_ok=True)

    with open(os.path.join(file_save_path, file_name), "w", encoding="utf-8") as f:
        json.dump(total_dict, f, ensure_ascii=False, indent=4)

    return


def save_data_error_json(display_name, display_id, error_file_dict):
    file_name = f"{display_name}_{display_id}_data_error_list.json"
    file_save_path = os.path.join(
        processed_path, display_name, display_id, "road", "error"
    )
    os.makedirs(file_save_path, exist_ok=True)

    with open(os.path.join(file_save_path, file_name), "w", encoding="utf-8") as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4)

    return


def save_gps_error_json(display_name, display_id, error_file_dict):
    file_name = f"{display_name}_{display_id}_gps_error_list.json"
    file_save_path = os.path.join(
        processed_path, display_name, display_id, "road", "error"
    )
    os.makedirs(file_save_path, exist_ok=True)

    with open(os.path.join(file_save_path, file_name), "w", encoding="utf-8") as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4)

    return


# 도로 gps + data csv 시간대 분류 데이터 저장
def save_single_road_data_json(
    display_name,
    road_name,
    total_dict,
    start_hour,
    hour_range,
    interval_minutes=0,
    interval_seconds=0,
):
    # total_dict 변환
    total_dict = convert_time_in_dict(total_dict)

    file_name_parts = [
        display_name,
        road_name,
        list(total_dict[road_name].keys())[0].replace("-", ""),
        f"{start_hour}",
        f"{hour_range}",
    ]
    if interval_minutes > 0:
        file_name_parts.append(f"{interval_minutes}min")
    if interval_seconds > 0:
        file_name_parts.append(f"{interval_seconds}sec")

    # 파일명 조합
    file_name = "_".join(file_name_parts) + "_data.json"
    file_save_path = os.path.join(
        processed_path, display_name, "GPS_AND_DATA", "result"
    )
    os.makedirs(file_save_path, exist_ok=True)

    with open(os.path.join(file_save_path, file_name), "w", encoding="utf-8") as f:
        json.dump(total_dict, f, ensure_ascii=False, indent=4)
    return


def save_single_road_error_json(display_name, road_name, error_file_dict):
    file_name = f"{display_name}_{road_name}_total_error_list.json"
    file_save_path = os.path.join(processed_path, display_name, "GPS_AND_DATA", "error")
    os.makedirs(file_save_path, exist_ok=True)

    with open(os.path.join(file_save_path, file_name), "w", encoding="utf-8") as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4)

    return
