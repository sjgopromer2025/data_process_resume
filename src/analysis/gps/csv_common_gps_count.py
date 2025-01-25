import os
import pandas as pd
import traceback
from data_class.display_data import DisplayInfo

from map.gps_time_filter import generate_time_intervals
from map.gps_time_filter import init_time_range
from map.gps_time_filter import filter_data_by_time_range
from utils.init_dict_util import init_display_info
from errors.data_error import csv_list_check
from .csv_common_gps import csv_gps_rectangle
from map.map_coordinate import read_data_csv_file
from utils.json_save_util import save_road_json
from utils.json_save_util import save_data_error_json


def csv_gps_time(
    display_name,
    display_id,
    date_str_list,
    start_hour,
    hour_range,
    interval_minutes,
    interval_seconds,
):
    error_file_dict = {display_id: []}
    total_dict = {display_name: {display_id: {}}}
    # 시간 범위 리스트
    time_interval_list = generate_time_intervals(
        start_hour, hour_range, interval_minutes, interval_seconds
    )

    for date_str in date_str_list:
        display_info: DisplayInfo = init_display_info(
            display_name, display_id, date_str
        )
        year = display_info.year
        month = display_info.month
        day = display_info.day
        full_date = f"{"-".join([year,month,day])}"

        total_dict[display_name][display_id][full_date] = {}

        # 시간 구간 설정 딕셔너리
        time_range_dict = init_time_range(time_interval_list)
        # gps 도로 데이터 검색
        csv_gps_rectangle(display_info, total_dict, time_range_dict)

        # 도로 이름 기준으로 딕셔너리 나옴
        date_dict: dict = total_dict[display_name][display_id][full_date]

        try:
            json_data = read_data_csv_file(display_info)

            # csv 파일 리스트
            csv_files = json_data[display_id]
            # csv 파일 리스트 체크
            csv_list_check(csv_files, display_info)

            for csv_file in csv_files:
                if os.path.getsize(csv_file) == 0:
                    error_file_dict[display_id].append(csv_file)
                    continue
                try:
                    csv_data = pd.read_csv(
                        csv_file, encoding="utf-8", on_bad_lines="skip"
                    ).dropna()
                    # 속성 공백 제거
                    csv_data.columns = csv_data.columns.str.strip()
                    # 중복 행 삭제
                    csv_data = csv_data.drop_duplicates(
                        subset="person_id", keep="first"
                    )

                    # 날짜와 시간이 결합된 경우 시간 부분만 추출
                    csv_data["appear_timing"] = (
                        csv_data["appear_timing"].str.split().str[1]
                    )
                    csv_data["appear_timing"] = pd.to_datetime(
                        csv_data["appear_timing"], format="%H:%M:%S"
                    ).dt.time

                    # 데이터 유무 체크
                    if csv_data.empty:
                        error_file_dict[display_id].append(csv_file)
                        continue

                    for road_name in date_dict:
                        # csv 파일에서 데이터 필터링이 필요한 시간 범위
                        time_diff_dict = date_dict[road_name]["time_in_diff"]

                        # 시간대 전부 포함한 딕셔너리
                        time_series_dict = date_dict[road_name]["time_series"]
                        road_info = date_dict[road_name]["road_info"]
                        filter_data_by_time_range(
                            csv_data.copy(), time_diff_dict, time_series_dict, road_info
                        )

                except Exception as e:
                    print("에러 발생:", e)
                    # traceback.print_exc()  # 에러의 상세 내용을 출력
                    # error_file_dict[display_id].append(csv_file)
        except Exception as e:
            print(e)
            continue
    save_data_error_json(display_name, display_id, error_file_dict)
    save_road_json(display_name, display_id, total_dict)
