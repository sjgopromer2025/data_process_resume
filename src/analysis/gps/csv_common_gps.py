import pandas as pd
import json
import os
import traceback
from shapely.geometry import Polygon

from utils.env_path_util import processed_path

from data_class.display_data import DisplayInfo

from errors.data_error import road_file_check
from errors.data_error import csv_list_check

from map.map_creator import create_map
from map.map_creator import create_map_point_and_rectangle
from map.map_creator import create_map_point_and_rectangle_test
from map.road_file_read import get_road_file
from map.road_file_read import get_total_road_file

from utils.init_dict_util import init_display_info
from utils.init_dict_util import init_road_dict

from map.map_coordinate import create_Polygon
from map.map_coordinate import change_pos_rectangle
from map.map_coordinate import is_within_polygon
from map.map_coordinate import read_road_file
from map.map_coordinate import read_gps_csv_file
from map.map_coordinate import read_single_road_file


from map.gps_time_filter import filter_gps_by_time_range
from utils.json_save_util import save_gps_error_json


def csv_gps_total(display_name, display_id, date_str):
    display_info = init_display_info(display_name, display_id, date_str)
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day

    json_data = read_gps_csv_file(display_info)
    # 에러 파일 기록
    error_file_dict = {display_id: []}
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
            csv_data.columns = csv_data.columns.str.strip()
            # csv_data['time'] = pd.to_datetime(csv_data['time'])
            csv_data = csv_data[
                ~(
                    (csv_data["latitude"] == 0)
                    & (csv_data["longitude"] == 0)
                    & (csv_data["speed"] == 0)
                    & (csv_data["distance"] == 0)
                )
            ]
            csv_data["time"] = pd.to_datetime(csv_data["time"]).dt.time

            if csv_data.empty:
                error_file_dict[display_id].append(csv_file)
                continue
            create_map(csv_data, display_name, display_id, year, month, day)
        except Exception as e:
            print("에러 발생:", e)
            traceback.print_exc()
            error_file_dict[display_id].append(csv_file)


# 지정한 도로들과 시간대, 좌표들이 포함되어 있는 지 확인하는 함수
def csv_gps_rectangle(
    display_info: DisplayInfo, total_dict: dict, time_range_dict: dict
):
    # 매체 정보
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day
    full_date = f"{"-".join([year,month,day])}"

    single_dict = total_dict[display_name][display_id][full_date]

    # road 파일 검사 후 리스트 리턴
    road_file_list = get_road_file(display_info)
    # 에러 파일 확인 dict
    error_file_dict = {display_id: []}
    # road 파일 리스트
    if len(road_file_list) > 0:
        for road_file_path in road_file_list:
            # print(road_file_path)
            road_name = road_file_path.split(".")[0].split("_")[-1]
            # print(road_name)
            single_dict[road_name] = init_road_dict()

            try:
                if os.path.exists(road_file_path):
                    # gps_csv_file_data
                    json_data = read_gps_csv_file(display_info)

                    # 도로 좌표 읽어 오기
                    rectangle = read_road_file(road_file_path)

                    # 좌표 위도 경도 변경 사각형 좌표 찍는 데 필요함
                    try:
                        change_pos_rectangle = [
                            [coord[1], coord[0]] for coord in rectangle["coordinates"]
                        ]
                    except KeyError:
                        change_pos_rectangle = [
                            [coord[1], coord[0]] for coord in rectangle
                        ]

                    # 다각형 객체 생성
                    polygon = create_Polygon(change_pos_rectangle)
                    # csv 파일 리스트
                    csv_files = json_data[display_id]

                    # csv 파일 리스트 체크
                    csv_list_check(csv_files, display_info)

                    for csv_file in csv_files:
                        if os.path.getsize(csv_file) == 0:
                            error_file_dict[display_id].append(csv_file)
                            continue

                        try:
                            gps_data = pd.read_csv(
                                csv_file, encoding="utf-8", on_bad_lines="skip"
                            ).dropna()
                            gps_data.columns = gps_data.columns.str.strip()
                            # csv_data['time'] = pd.to_datetime(csv_data['time'])
                            gps_data = gps_data[
                                ~(
                                    (gps_data["latitude"] == 0)
                                    & (gps_data["longitude"] == 0)
                                    & (gps_data["speed"] == 0)
                                    & (gps_data["distance"] == 0)
                                )
                            ]
                            gps_data["time"] = pd.to_datetime(gps_data["time"]).dt.time

                            if gps_data.empty:
                                error_file_dict[display_id].append(csv_file)
                                continue
                            time_diff_dict = single_dict[road_name]["time_in_diff"]

                            stat = filter_gps_by_time_range(
                                gps_data, time_range_dict, polygon, time_diff_dict
                            )
                            if stat:
                                road_info = single_dict[road_name]["road_info"]
                                road_info["average_speed"] = stat["average_speed"]
                                road_info["min_speed"] = stat["min_speed"]
                                road_info["max_speed"] = stat["max_speed"]
                                road_info["road_length"] = stat["road_length"]

                            # create_map_point_and_rectangle(filtered_df, rectangle,display_name, display_id, year, month, day,road_name)

                        except Exception as e:
                            print(e)
                            error_file_dict[display_id].append(csv_file)
                else:
                    road_file_check(False, display_info, road_name)
            except Exception as e:
                print("에러 발생:", e)
                continue
    save_gps_error_json(display_name, display_id, error_file_dict)
    return


# 지도에 전체 도로 표시 하는 함수
def csv_gps_total_2(display_name, display_id, date_str):
    display_info = init_display_info(display_name, display_id, date_str)
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day

    json_data = read_gps_csv_file(display_info)
    # 에러 파일 기록
    error_file_dict = {display_id: []}
    # csv 파일 리스트
    csv_files = json_data[display_id]

    # csv 파일 리스트 체크
    csv_list_check(csv_files, display_info)

    # road 파일 검사 후 리스트 리턴
    road_file_list = get_total_road_file()

    for csv_file in csv_files:
        if os.path.getsize(csv_file) == 0:
            error_file_dict[display_id].append(csv_file)
            continue

        try:
            csv_data = pd.read_csv(
                csv_file, encoding="utf-8", on_bad_lines="skip"
            ).dropna()
            csv_data.columns = csv_data.columns.str.strip()
            csv_data = csv_data[
                ~(
                    (csv_data["latitude"] == 0)
                    & (csv_data["longitude"] == 0)
                    & (csv_data["speed"] == 0)
                    & (csv_data["distance"] == 0)
                )
            ]
            csv_data["time"] = pd.to_datetime(csv_data["time"]).dt.time

            if csv_data.empty:
                error_file_dict[display_id].append(csv_file)
                continue

            map_route = create_map(csv_data, display_name, display_id, year, month, day)

            for road_file_path in road_file_list:
                # print(road_file_path)
                road_name = road_file_path.split(".")[0].split("_")[-1]

                if os.path.exists(road_file_path):
                    # gps_csv_file_data
                    json_data = read_gps_csv_file(display_info)

                    # 도로 좌표 읽어 오기
                    rectangle = read_road_file(road_file_path)

                    # #좌표 위도 경도 변경 사각형 좌표 찍는 데 필요함
                    # change_pos_rectangle = [
                    #     [coord[1], coord[0]] for coord in rectangle
                    # ]

                    # # 다각형 객체 생성
                    # polygon = create_Polygon(change_pos_rectangle)
                    # 사각형 추가

                    create_map_point_and_rectangle_test(map_route, rectangle)

            # 지도 저장
            map_name = f'{"_".join([display_name,display_id,year,month,day])}_rectangle_point_map.html'
            # 이미지 파일로 저장
            map_save_path = os.path.join(
                processed_path, display_name, display_id, "GPS", "rectangle_and_point"
            )
            os.makedirs(map_save_path, exist_ok=True)

            map_route.save(os.path.join(map_save_path, map_name))

        except Exception as e:
            print("에러 발생:", e)
            traceback.print_exc()
            error_file_dict[display_id].append(csv_file)


# 지정한 도로들과 시간대, 좌표들이 포함되어 있는 지 확인하는 함수
def gps_data_handler(
    gps_csv_path,
    road_name,
    display_time_dict: dict,
    time_range_dict: dict,
    gps_error_list: list,
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

        if os.path.getsize(gps_csv_path) == 0:
            gps_error_list.append(gps_csv_path)
            return
        else:
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
            gps_data["time"] = pd.to_datetime(gps_data["time"]).dt.time

            if not gps_data.empty:
                time_diff_dict = display_time_dict["time_in_diff"]
                filter_gps_by_time_range(
                    gps_data, time_range_dict, polygon_infos, time_diff_dict
                )
            else:
                gps_error_list.append(gps_csv_path)

    except Exception as e:
        print("에러 발생:", e)
        gps_error_list.append(gps_csv_path)
