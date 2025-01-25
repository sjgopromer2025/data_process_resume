import os
import pandas as pd
import traceback

from map.gps_time_filter2 import filter_data_by_time_range2

from map.map_coordinate import read_data_and_gps_csv_file
from map.map_coordinate import read_single_road_file

from analysis.gps.csv_common_gps2 import gps_data_handler
from map.map_coordinate import create_Polygon

from utils.json_save_util import save_single_road_data_json
from utils.json_save_util import save_single_road_error_json
import json


def csv_gps_road_time(
    display_name,
    road_name,
    date_str_list,
    start_hour,
    hour_range,
    interval_minutes,
    interval_seconds,
):

    error_file_dict = {display_name: {"data": [], "gps": []}}
    data_error_list = error_file_dict[display_name]["data"]
    gps_error_list = error_file_dict[display_name]["gps"]

    time_info = {
        "interval_minutes": interval_minutes,
        "interval_seconds": interval_seconds,
    }
    # 결과 정보 딕셔너리
    total_dict = {road_name: {}}

    # csv 파일 저장 딕셔너리
    day_gps_and_data_dict = {road_name: {}}

    # 날짜 리스트
    day_list = []
    for date_str in date_str_list:
        year, month, day = date_str[:4], date_str[4:6], date_str[6:]
        full_date = f"{"-".join([year,month,day])}"
        day_list.append(full_date)
        day_gps_and_data_dict[road_name][full_date] = {}
        total_dict[road_name][full_date] = {}

    mix_json_data = read_data_and_gps_csv_file(display_name, day_list)

    # 둘다 null 이거나 혹은 하나만 null 인 아이템 삭제
    remove_null_entries(mix_json_data)

    # 도로 > 날짜 > 매체 번호 > 시간대 >
    for day in day_list:
        day_dict = mix_json_data[day]
        for display_id in day_dict.keys():

            csv_info = day_dict[display_id]
            data_csv_path, gps_csv_path = csv_info["data"], csv_info["gps"]

            total_dict[road_name][day][display_id] = {
                "road_time_range": {},
            }

            # { timeseries:{} , timeindiff:{},"road_time_range": {}} 의 형태
            display_time_dict = total_dict[road_name][day][display_id]
            # 파일 에러
            if os.path.getsize(data_csv_path) == 0:
                data_error_list.append(data_csv_path)
                continue

            try:
                """
                gps 데이터를 사용하여 지정 도로의 좌표에 해당
                날짜의 좌표가 포함되어있는 것들을 필터링하여 시간대를 추출
                {'highway1':
                    {'2024-10-12':
                        {'7000':
                            {
                                road_time_range:{}
                            }
                        }
                    }
                }

                """
                gps_data_handler(
                    gps_csv_path,
                    road_name,
                    display_time_dict,
                    gps_error_list,
                    time_info,
                )

                ############################################
                ############################################
                ############################################
                ############################################

                csv_data = pd.read_csv(
                    data_csv_path, encoding="utf-8", on_bad_lines="skip"
                ).dropna()
                # 속성 공백 제거
                csv_data.columns = csv_data.columns.str.strip()
                # 중복 행 삭제
                csv_data = csv_data.drop_duplicates(subset="person_id", keep="first")

                # 날짜와 시간이 결합된 경우 시간 부분만 추출
                csv_data["appear_timing"] = csv_data["appear_timing"].str.split().str[1]
                csv_data["appear_timing"] = pd.to_datetime(
                    csv_data["appear_timing"], format="%H:%M:%S"
                ).dt.time

                # 데이터 유무 체크
                if csv_data.empty:
                    data_error_list.append(data_csv_path)
                    continue

                # time_diff_dict = display_time_dict["time_in_diff"]

                # # 시간대 전부 포함한 딕셔너리
                # time_series_dict = display_time_dict["time_series"]
                if display_time_dict["road_time_range"] != None:
                    filter_data_by_time_range2(
                        csv_data.copy(), display_time_dict["road_time_range"]
                    )
                # Convert the result to JSON format and print
                result_json = json.dumps(total_dict, indent=2)
                # print(result_json)
            except Exception as e:
                print("에러 발생:", e)
                data_error_list.append(data_csv_path)
                continue

    # remove_empty_time_in_diff(total_dict)

    save_single_road_error_json(display_name, display_id, error_file_dict)
    save_single_road_data_json(
        display_name,
        road_name,
        total_dict,
        start_hour,
        hour_range,
        interval_minutes,
        interval_seconds,
    )
    return


def remove_null_entries(json_data):
    """
    JSON 데이터에서 'data' 또는 'gps' 중 하나라도 null이면 해당 매체를 삭제합니다.

    :param json_data: dict 형태의 JSON 데이터
    :return: null 값이 제거된 JSON 데이터
    """
    for day, day_data in list(json_data.items()):
        for media, media_data in list(day_data.items()):
            if media_data.get("data") is None or media_data.get("gps") is None:
                del day_data[media]

        # 해당 날짜의 데이터가 모두 삭제된 경우 날짜도 제거
        if not day_data:
            del json_data[day]

    return json_data


def remove_empty_time_in_diff(data_dict):
    for road, dates in data_dict.items():
        for date, ids in list(
            dates.items()
        ):  # dict를 수정하면서 순회하려면 list로 복사
            ids_to_remove = [
                id_ for id_, values in ids.items() if not values.get("time_in_diff")
            ]
            for id_ in ids_to_remove:
                del ids[id_]
    return data_dict
