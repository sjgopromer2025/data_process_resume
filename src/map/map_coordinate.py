import json
import os
from data_class.display_data import DisplayInfo
from shapely.geometry import Point, Polygon
from utils.directroy_util import directory_pick_one_day_read_gps
from utils.directroy_util import directory_pick_one_day_read
from utils.directroy_util import directory_gps_and_data_read
from errors.data_error import json_file_check
from errors.data_error import json_data_check
from utils.env_path_util import src_path


def map_rectangle_center(rectangle):
    # Latitude와 Longitude 분리
    latitudes = [point[0] for point in rectangle]
    longitudes = [point[1] for point in rectangle]

    # 중심 좌표 계산
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)

    return [center_lat, center_lon]


# 다각형 객체 생성
def create_Polygon(change_pos_rectangle):
    return Polygon(change_pos_rectangle)


# 좌표 필터링 함수
def is_within_polygon(polygon: Polygon, lat, lon):
    point = Point(lon, lat)  # Point는 (경도, 위도) 순서
    return polygon.contains(point)  # 다각형 안에 점이 포함되면 True


def read_road_file(road_file_path):
    # 파일 불러오기
    with open(road_file_path, "r", encoding="utf-8") as file:
        rectangle = json.load(file)
    return rectangle


def change_pos_rectangle(coordinates):
    try:
        change_pos_rectangle = [[coord[1], coord[0]] for coord in coordinates]
    except KeyError:
        raise ValueError("도로 좌표가 잘못되었습니다.")
    return create_Polygon(change_pos_rectangle)


def read_gps_csv_file(display_info: DisplayInfo):
    # 매체 정보
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day

    # csv 파일 검색
    json_file_path = directory_pick_one_day_read_gps(
        display_name, display_id, year, month, day
    )

    # 파일 체크
    json_file_check(json_file_path, display_info)

    # 파일 불러오기
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # 파일 데이터 체크
    json_data_check(json_data, display_info)

    return json_data


def read_data_csv_file(display_info: DisplayInfo):
    # 매체 정보
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day

    # 디렉토리 읽기
    json_file_path = directory_pick_one_day_read(
        display_name, display_id, year, month, day
    )
    # csv 데이터 검색
    json_file_check(json_file_path, display_info)
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    # 파일 데이터 체크
    json_data_check(json_data, display_info)

    return json_data


def read_data_and_gps_csv_file(display_name, day_list):
    # 디렉토리 읽기
    json_file_path = directory_gps_and_data_read(display_name, day_list)

    if not json_file_path:
        raise ValueError(f"{display_name}의 {day_list} 정보가 없습니다.")

    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    return json_data


def read_single_road_file(road_name):
    road_file_path = os.path.join(
        src_path, "roads", "total_coordinate", f"{road_name}.json"
    )
    # print(total_road_path)
    if os.path.exists(road_file_path):
        with open(road_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        return json_data
    else:
        raise ValueError("도로 정보가 존재하지 않습니다.")


def read_total_road_file():
    road_file_path = os.path.join(src_path, "roads", "total_coordinate")
    # print(total_road_path)
    if os.path.exists(road_file_path):
        datas = []
        road_file_list = os.listdir(road_file_path)

        for road_file_name in road_file_list:
            road_name = road_file_name.split(".")[0]
            full_file_path = os.path.join(road_file_path, road_file_name)
            with open(full_file_path, "r", encoding="utf-8") as file:
                datas.append([road_name, json.load(file)])
        return datas
    else:
        raise ValueError("도로 정보가 존재하지 않습니다.")
