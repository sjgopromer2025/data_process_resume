import json
import os
from utils.env_path_util import base_path, processed_path
from utils.datetime_util import check_day
from utils.datetime_util import check_pick_days
from utils.datetime_util import check_pick_one_day


# 데이터 폴더 월 전체 검사
def directory_month_total_read(display_name, year, month):
    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_ids = os.listdir(display_path)
    display_info_dict = {}

    for id in display_ids:
        display_year_path = os.path.join(display_path, id, year)
        # print(display_year_path)
        # print(month_dirs)
        display_csv_path = os.path.join(display_year_path, month)

        display_info_dict[id] = []
        # print(display_csv_path)
        if os.path.isdir(display_csv_path):
            if os.path.exists(display_csv_path):
                csv_files = os.listdir(display_csv_path)
                # print(csv_files)
                for file in csv_files:
                    file_path = os.path.join(display_csv_path, file)
                    display_info_dict[id].append(file_path)
        else:
            continue

    json_file_path = (
        f"{processed_path}/csv_list_{display_name}_total_{year}_{month}.json"
    )
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)
    return json_file_path


# 데이터 폴더 월 전체 검사
def directory_month_day_read(display_name, year, month, day_list):
    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_ids = os.listdir(display_path)
    display_info_dict = {}

    for id in display_ids:
        display_year_path = os.path.join(display_path, id, year)
        # print(display_year_path)
        # print(month_dirs)
        display_csv_path = os.path.join(display_year_path, month)

        display_info_dict[id] = []
        # print(display_csv_path)
        if os.path.isdir(display_csv_path):
            if os.path.exists(display_csv_path):
                csv_files = check_day(os.listdir(display_csv_path), day_list)
                for file in csv_files:
                    file_path = os.path.join(display_csv_path, file)
                    display_info_dict[id].append(file_path)
        else:
            continue

    json_file_path = f'{processed_path}/csv_list_{display_name}_total_{year}_{month}_{"_".join(day_list)}.json'
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)
    return json_file_path


# 데이터 폴더 월 전체 검사
def directory_month_pick_day_read(display_name, year, month, day_pick_list):
    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_ids = os.listdir(display_path)
    display_info_dict = {}

    for id in display_ids:
        display_year_path = os.path.join(display_path, id, year)

        display_csv_path = os.path.join(display_year_path, month)
        display_info_dict[id] = []
        # print(display_csv_path)
        if os.path.isdir(display_csv_path):
            if os.path.exists(display_csv_path):
                csv_files = check_pick_days(os.listdir(display_csv_path), day_pick_list)
                for file in csv_files:
                    file_path = os.path.join(display_csv_path, file)
                    display_info_dict[id].append(file_path)
        else:
            continue

    json_file_path = (
        f"{processed_path}/csv_list_{display_name}_total_{year}_{month}_pick_day.json"
    )
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)

    return json_file_path


# 데이터 특정 매체 폴더 특정 요일 검사
def directory_pick_one_day_read(display_name, display_id, year, month, day):
    one_day = f"{year}-{month}-{day}"

    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_info_dict = {}

    display_year_path = os.path.join(display_path, display_id, year)

    display_csv_path = os.path.join(display_year_path, month)
    display_info_dict[display_id] = []
    # print(display_csv_path)
    if os.path.isdir(display_csv_path):
        if os.path.exists(display_csv_path):
            csv_files = check_pick_one_day(os.listdir(display_csv_path), one_day)
            for file in csv_files:
                file_path = os.path.join(display_csv_path, file)
                display_info_dict[display_id].append(file_path)
        else:
            return False

    # 최초 루트 경로
    root_path = os.path.join(
        processed_path, display_name, display_id, "DATA", year, month, day
    )

    gps_json_name = (
        f'{"_".join([display_name,display_id,year,month,day])}_data_csv_list.json'
    )
    # 이미지 파일로 저장
    gps_json_save_path = os.path.join(root_path, "csv_list")
    os.makedirs(gps_json_save_path, exist_ok=True)

    json_file_path = os.path.join(gps_json_save_path, gps_json_name)
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)

    return json_file_path


# 데이터 폴더 월 단일 검사
def directory_month_single_read(display_name, year, month, display_id):
    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_info_dict = {}

    display_year_path = os.path.join(display_path, display_id, year)
    # print(display_year_path)
    # print(month_dirs)
    display_csv_path = os.path.join(display_year_path, month)

    display_info_dict[display_id] = []
    # print(display_csv_path)
    if os.path.isdir(display_csv_path):
        if os.path.exists(display_csv_path):
            csv_files = os.listdir(display_csv_path)
            # print(csv_files)
            for file in csv_files:
                file_path = os.path.join(display_csv_path, file)
                display_info_dict[display_id].append(file_path)

            json_file_path = f"{processed_path}/csv_list_{display_name}_{display_id}_{year}_{month}.json"

            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(display_info_dict, f, ensure_ascii=False, indent=4)
            return json_file_path
    else:
        return False


# 데이터 폴더 전체 검사
def directory_total_read(display_name, year):
    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "DATA")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_ids = os.listdir(display_path)
    display_info_dict = {}

    for id in display_ids:
        display_year_path = os.path.join(display_path, id, year)
        # print(display_year_path)
        if os.path.exists(display_year_path):
            month_dirs = os.listdir(display_year_path)

            display_info_dict[id] = {}
            for month in month_dirs:
                display_csv_path = os.path.join(display_year_path, month)

                display_info_dict[id][month] = []
                if os.path.isdir(display_csv_path):
                    csv_files = os.listdir(display_csv_path)
                    # print(csv_files)
                    for file in csv_files:
                        file_path = os.path.join(display_csv_path, file)
                        display_info_dict[id][month].append(file_path)
        else:
            continue

    json_file_path = f"{processed_path}/csv_list_{display_name}_total_{year}.json"
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)
    return json_file_path


# GPS 특정 매체 폴더 특정 요일 검사
def directory_pick_one_day_read_gps(display_name, display_id, year, month, day):
    one_day = f"{year}-{month}-{day}"

    # display 기준 파일 경로
    display_path = os.path.join(base_path, display_name, "GPS")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_info_dict = {}

    display_year_path = os.path.join(display_path, display_id, year)

    display_csv_path = os.path.join(display_year_path, month)
    display_info_dict[display_id] = []
    # print(display_csv_path)
    if os.path.exists(display_csv_path):
        csv_files = check_pick_one_day(os.listdir(display_csv_path), one_day)
        for file in csv_files:
            file_path = os.path.join(display_csv_path, file)
            display_info_dict[display_id].append(file_path)
    else:
        return False

    # 최초 루트 경로
    root_path = os.path.join(
        processed_path, display_name, display_id, "GPS", year, month, day
    )

    gps_json_name = (
        f'{"_".join([display_name,display_id,year,month,day])}_gps_csv_list.json'
    )
    # 이미지 파일로 저장
    gps_json_save_path = os.path.join(root_path, "csv_list")
    os.makedirs(gps_json_save_path, exist_ok=True)

    json_file_path = os.path.join(gps_json_save_path, gps_json_name)
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)

    return json_file_path


# 데이터 폴더 월 전체 검사
def directory_gps_and_data_read(display_name, day_pick_list):
    # DATA 파일 경로
    display_data_path = os.path.join(base_path, display_name, "DATA")
    # GPS 파일 경로
    display_gps_path = os.path.join(base_path, display_name, "GPS")

    # 디렉토리 내 모든 파일 목록 가져오기
    display_ids = os.listdir(display_data_path)

    display_info_dict = {}
    for day in day_pick_list:
        display_info_dict[day] = {}

        dates_info = day.split("-")
        year = dates_info[0]
        month = dates_info[1]

        for id in display_ids:
            # 시청 데이터 경로
            display_data_year_path = os.path.join(display_data_path, id, year)
            display_data_csv_path = os.path.join(display_data_year_path, month)

            # GPS 데이터 경로
            display_gps_year_path = os.path.join(display_gps_path, id, year)
            display_gps_csv_path = os.path.join(display_gps_year_path, month)

            # data , gps 파일 정보 저장 딕셔너리
            display_info_dict[day][id] = {"data": None, "gps": None}

            # 데이터 파일 처리
            append_csv_files(
                display_data_csv_path, day, "data", display_info_dict[day][id]
            )
            # GPS 파일 처리
            append_csv_files(
                display_gps_csv_path, day, "gps", display_info_dict[day][id]
            )

    # 최초 루트 경로
    root_path = os.path.join(processed_path, display_name, "GPS_AND_DATA", "file_info")

    os.makedirs(root_path, exist_ok=True)

    json_file_name = f"{display_name}_gps_and_data.json"
    full_path = os.path.join(root_path, json_file_name)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(display_info_dict, f, ensure_ascii=False, indent=4)

    return full_path
    # return False


def append_csv_files(base_path, day, file_type, target_dict):
    if os.path.exists(base_path) and os.path.isdir(base_path):
        csv_files = check_pick_days(os.listdir(base_path), [day])
        for file in csv_files:
            file_path = os.path.join(base_path, file)
            target_dict[file_type] = file_path
