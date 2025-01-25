import pandas as pd
import json
import os
import traceback
from shapely.geometry import Polygon

from utils.env_path_util import processed_path

from data_class.display_data import DisplayInfo

from map.map_coordinate import change_pos_rectangle
from map.map_coordinate import read_single_road_file


from map.gps_time_filter2 import filter_gps_by_load


# 지정한 도로들과 시간대, 좌표들이 포함되어 있는 지 확인하는 함수
def gps_data_handler(
    gps_csv_path,
    road_name,
    display_time_dict: dict,
    gps_error_list: list,
    time_info: dict,
):
    try:
        # 기준 도로 좌표
        road_rec_coordinate = read_single_road_file(road_name)

        # 좌표 위도 경도 변경 사각형 좌표 찍는 데 필요함
        # 다각형 객체 생성
        base_polygon = change_pos_rectangle(road_rec_coordinate["coordinates"])
        front_polygon = change_pos_rectangle(road_rec_coordinate["front_gate"])
        back_polygon = change_pos_rectangle(road_rec_coordinate["back_gate"])
        front_gate_center = road_rec_coordinate["front_gate_center"]
        back_gate_center = road_rec_coordinate["back_gate_center"]

        polygon_infos = {
            "base_polygon": base_polygon,
            "front_polygon": front_polygon,
            "back_polygon": back_polygon,
            "front_gate_center": front_gate_center,
            "back_gate_center": back_gate_center,
        }

        # 해당 날짜의 gps 데이터 불러오기
        if os.path.getsize(gps_csv_path) == 0:
            gps_error_list.append(gps_csv_path)
            return
        else:
            # 에시 2024-09-01 데이터 로드 후 필터링
            gps_data = pd.read_csv(
                gps_csv_path, encoding="utf-8", on_bad_lines="skip"
            ).dropna()
            gps_data.columns = gps_data.columns.str.strip()
            gps_data = gps_data[
                ~(
                    (gps_data["latitude"] == 0)
                    & (gps_data["longitude"] == 0)
                    & (gps_data["speed"] == 0)
                    & (gps_data["distance"] == 0)
                )
            ]
            gps_data["time2"] = pd.to_datetime(gps_data["time"])
            gps_data["time"] = pd.to_datetime(gps_data["time"]).dt.time

            if not gps_data.empty:
                display_time_dict["road_time_range"] = filter_gps_by_load(
                    gps_data, polygon_infos, time_info
                )
            else:
                gps_error_list.append(gps_csv_path)

    except Exception as e:
        print("에러 발생:", e)
        gps_error_list.append(gps_csv_path)
