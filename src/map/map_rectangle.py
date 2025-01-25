import folium
import math
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)
from utils.env_path_util import src_path
from map.map_coordinate import read_total_road_file
from map.map_coordinate import map_rectangle_center
from folium import Popup
from geopy.distance import distance


def rotate_point(lat, lon, center_lat, center_lon, angle):
    """좌표를 중심으로 특정 각도(도)만큼 회전"""
    angle_rad = math.radians(angle)

    # 중심점을 기준으로 좌표 이동
    lat_shifted = lat - center_lat
    lon_shifted = lon - center_lon

    # 회전 변환 행렬 적용
    rotated_lat = lat_shifted * math.cos(angle_rad) - lon_shifted * math.sin(angle_rad)
    rotated_lon = lat_shifted * math.sin(angle_rad) + lon_shifted * math.cos(angle_rad)

    # 중심점을 기준으로 다시 이동
    rotated_lat += center_lat
    rotated_lon += center_lon

    return rotated_lat, rotated_lon


def create_rotated_rectangle(
    center_lat, center_lon, width_meters, height_meters, angle
):
    """중심 좌표, 너비, 높이, 회전각을 이용해 회전된 사각형 좌표 생성"""
    earth_radius = 6378137  # 지구 반지름 (미터)

    # 거리(m)를 위도와 경도로 변환
    delta_lat = height_meters / (2 * earth_radius)
    delta_lon = width_meters / (2 * earth_radius * math.cos(math.radians(center_lat)))

    delta_lat_deg = math.degrees(delta_lat)
    delta_lon_deg = math.degrees(delta_lon)

    # 회전 전 사각형 꼭짓점 (남서, 북서, 북동, 남동 순)
    corners = [
        (center_lat - delta_lat_deg, center_lon - delta_lon_deg),  # 남서
        (center_lat + delta_lat_deg, center_lon - delta_lon_deg),  # 북서
        (center_lat + delta_lat_deg, center_lon + delta_lon_deg),  # 북동
        (center_lat - delta_lat_deg, center_lon + delta_lon_deg),  # 남동
    ]

    # 각 꼭짓점을 회전
    rotated_corners = [
        rotate_point(lat, lon, center_lat, center_lon, angle) for lat, lon in corners
    ]

    # GeoJSON 형식의 다각형 좌표로 반환
    return rotated_corners + [
        rotated_corners[0]
    ]  # 첫 점을 마지막에 추가해 닫힌 다각형 생성


# 지도 사각형 반경 표시
def map_rectangle_creator(params):
    center_lat = params["center_lat"]
    center_lon = params["center_lon"]
    width_meters = params["width_meters"]
    height_meters = params["height_meters"]
    rotation_angle = params["rotation_angle"]
    display_name = params["display_name"]
    display_id = params["display_id"]

    date_str = params["date_str"]
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]

    json_save = params["json_save"]
    road_name = params["road_name"]
    road_name_kr = params["road_name_kr"]
    # 회전된 사각형 좌표 생성
    rotated_rectangle = create_rotated_rectangle(
        center_lat, center_lon, width_meters, height_meters, rotation_angle
    )

    # 최초 루트 경로
    root_path = os.path.join(
        src_path, "roads", display_name, display_id, year, month, day
    )
    # 사각형 좌표 json 저장
    if json_save:
        coordinate_file_name = (
            f"{display_name}_{display_id}_{year}_{month}_{day}_{road_name}.json"
        )
        json_file_path = os.path.join(root_path, "coordinate")
        os.makedirs(json_file_path, exist_ok=True)
        with open(
            os.path.join(root_path, "coordinate", coordinate_file_name),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(rotated_rectangle, f, ensure_ascii=False, indent=4)

        road_file_name = f"{road_name}.json"
        total_json_file_path = os.path.join(src_path, "roads", "total_coordinate")
        os.makedirs(total_json_file_path, exist_ok=True)
        with open(
            os.path.join(total_json_file_path, road_file_name), "w", encoding="utf-8"
        ) as f:
            json.dump(rotated_rectangle, f, ensure_ascii=False, indent=4)

    # 지도 생성
    map_rec = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 회전된 사각형 추가 (GeoJSON)
    folium.Polygon(
        locations=rotated_rectangle,
        color="blue",
        fill=True,
        fill_color="lightblue",
        fill_opacity=0.5,
    ).add_to(map_rec)

    # HTML 팝업을 사용해 글자를 가로로 표시
    popup_text = get_pop_text(road_name_kr)

    folium.Marker(
        location=[center_lat, center_lon],
        popup=Popup(popup_text, max_width=300),  # HTML 팝업 적용
        icon=folium.Icon(color="red"),
    ).add_to(map_rec)
    # # 중심점 표시
    # folium.Marker(
    #     location=[center_lat, center_lon],
    #     popup=road_name_kr,
    #     icon=folium.Icon(color="red")
    # ).add_to(map_rec)

    # HTML 파일로 저장

    map_name = f"{road_name}_rectangle_map.html"
    # 이미지 파일로 저장
    map_save_path = os.path.join(root_path, "rectangle")
    os.makedirs(map_save_path, exist_ok=True)

    map_rec.save(os.path.join(map_save_path, map_name))


# 모든 도로 지도 생성
def total_road_map():
    # 정의한 도로 좌표 리스트
    total_road_coordinate_list = read_total_road_file()
    first_road_info = total_road_coordinate_list[0]

    # 도로 리스트 맵 기준 좌표 설정
    map_center = map_rectangle_center(first_road_info[1][:-1])

    # 지도 생성
    map_rec = folium.Map(location=map_center, zoom_start=14)

    for road_info in total_road_coordinate_list:
        # 도로 리스트 맵 기준 좌표 설정
        road_name = road_info[0]
        road_coordinate = road_info[1]
        road_centers = map_rectangle_center(road_coordinate[:-1])

        # 회전된 사각형 추가 (GeoJSON)
        folium.Polygon(
            locations=road_coordinate,
            color="blue",
            fill=True,
            fill_color="lightblue",
            fill_opacity=0.5,
        ).add_to(map_rec)

        # 중심점 표시
        folium.Marker(
            location=road_centers, popup=road_name, icon=folium.Icon(color="red")
        ).add_to(map_rec)

    # HTML 파일로 저장
    # 최초 루트 경로
    root_path = os.path.join(
        src_path,
        "roads",
    )
    map_name = f"total_road_map.html"
    # 이미지 파일로 저장
    map_save_path = os.path.join(root_path, "total_road_map")
    os.makedirs(map_save_path, exist_ok=True)

    map_rec.save(os.path.join(map_save_path, map_name))


# 도로 입구 출구 지도 생성
def draw_rectangle_on_map(params):
    display_name = params["display_name"]
    display_id = params["display_id"]

    date_str = params["date_str"]
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]

    road_name = params["road_name"]
    road_name_kr = params["road_name_kr"]
    coordinates = params["coordinates"]
    reversed = params["reverse"]

    # 최초 루트 경로
    root_path = os.path.join(
        src_path, "roads", display_name, display_id, year, month, day
    )

    # 지도 중심
    center_coordinate = map_rectangle_center(coordinates[:-1])

    # 지도 생성
    map_rec = folium.Map(location=center_coordinate, zoom_start=16)

    # 전체 폴리곤 경계와 내부 색상 설정
    folium.Polygon(
        locations=coordinates,  # 4개의 좌표 리스트
        color="green",  # 경계선 색깔
        fill=True,
        fill_color="lightblue",  # 내부 색깔
        fill_opacity=0.5,
    ).add_to(map_rec)

    # 단축 경로 구별 선
    # drawing_polyline(coordinates, map_rec)

    # HTML 팝업을 사용해 글자를 가로로 표시
    popup_text = get_pop_text(road_name_kr)

    params["gate_info"] = drawing_gates(coordinates, map_rec, reversed)
    folium.Marker(
        location=center_coordinate,
        popup=Popup(popup_text, max_width=300),  # HTML 팝업 적용
        icon=folium.Icon(color="red"),
    ).add_to(map_rec)

    # 사각형 좌표 json 저장
    save_coordinates_json(params)

    map_name = f"{road_name}_rectangle_map.html"
    # 이미지 파일로 저장
    map_save_path = os.path.join(root_path, "rectangle")
    os.makedirs(map_save_path, exist_ok=True)

    map_rec.save(os.path.join(map_save_path, map_name))
    return


# def drawing_polyline(coordinates, map_rec):
#     # 첫 번째와 두 번째 좌표를 잇는 빨간 선
#     folium.PolyLine(
#         locations=coordinates[:2],
#         color="red",
#         weight=10,  # 선 두께
#     ).add_to(map_rec)
#     # 세 번째와 네 번째 좌표를 잇는 파란 선
#     folium.PolyLine(
#         locations=coordinates[2:4],
#         color="blue",
#         weight=10,  # 선 두께
#     ).add_to(map_rec)
#     return


def save_coordinates_json(params):
    width_meters = params["width_meters"]
    height_meters = params["height_meters"]
    rotation_angle = params["rotation_angle"]
    display_name = params["display_name"]
    display_id = params["display_id"]

    date_str = params["date_str"]
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]

    json_save = params["json_save"]
    road_name = params["road_name"]
    road_name_kr = params["road_name_kr"]
    coordinates = params["coordinates"]
    gate_info = params["gate_info"]

    json_data_form = {
        "road_name": road_name,
        "coordinates": coordinates,
        "front_gate": gate_info["front_gate"],
        "back_gate": gate_info["back_gate"],
        "front_gate_center": gate_info["front_gate_center"],
        "back_gate_center": gate_info["back_gate_center"],
    }
    # 최초 루트 경로
    root_path = os.path.join(
        src_path, "roads", display_name, display_id, year, month, day
    )
    # 사각형 좌표 json 저장
    if json_save:
        coordinate_file_name = (
            f"{display_name}_{display_id}_{year}_{month}_{day}_{road_name}.json"
        )
        json_file_path = os.path.join(root_path, "coordinate")
        os.makedirs(json_file_path, exist_ok=True)
        with open(
            os.path.join(root_path, "coordinate", coordinate_file_name),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(json_data_form, f, ensure_ascii=False, indent=4)

        road_file_name = f"{road_name}.json"
        total_json_file_path = os.path.join(src_path, "roads", "total_coordinate")
        os.makedirs(total_json_file_path, exist_ok=True)
        with open(
            os.path.join(total_json_file_path, road_file_name), "w", encoding="utf-8"
        ) as f:
            json.dump(json_data_form, f, ensure_ascii=False, indent=4)
    return


def drawing_gates(coordinates, map_rec, reversed):
    f_coordinates = coordinates[:-1]
    if len(f_coordinates) != 4:
        # logging.error("좌표가 4개가 아닙니다.")
        f_coordinates = f_coordinates[:2] + f_coordinates[3:]
    """
    01
     2
    43
    사각형 좌표 리스트를 이용해 사각형의 앞뒤 게이트를 그리는 함수
    0 ========= 1
    =           =
    =           =
    =           =
    =           =
    3 ========= 2
    """
    if reversed:
        t3_cor = calculate_intermediate_points(f_coordinates[0], f_coordinates[-1], 50)
        t4_cor = calculate_intermediate_points(f_coordinates[1], f_coordinates[-2], 50)

        front_gate_center = draw_circle_touching_two_points(
            f_coordinates[0], f_coordinates[1], map_rec, color="red"
        )
        front_gate = f_coordinates[:2] + t4_cor + t3_cor + f_coordinates[:1]
        folium.Polygon(
            locations=front_gate,  # 4개의 좌표 리스트
            color="green",  # 경계선 색깔
            fill=True,
            fill_color="red",  # 내부 색깔
            fill_opacity=0.5,
        ).add_to(map_rec)

        t3_cor = calculate_intermediate_points(f_coordinates[-1], f_coordinates[0], 50)
        t4_cor = calculate_intermediate_points(f_coordinates[-2], f_coordinates[1], 50)

        back_gate_center = draw_circle_touching_two_points(
            f_coordinates[-1], f_coordinates[-2], map_rec
        )
        back_gate = t3_cor + t4_cor + f_coordinates[2:] + t3_cor
        folium.Polygon(
            locations=back_gate,  # 4개의 좌표 리스트
            color="green",  # 경계선 색깔
            fill=True,
            fill_color="blue",  # 내부 색깔
            fill_opacity=0.5,
        ).add_to(map_rec)
    else:
        ### reverse
        t3_cor = calculate_intermediate_points(f_coordinates[0], f_coordinates[1], 50)
        t4_cor = calculate_intermediate_points(f_coordinates[-1], f_coordinates[-2], 50)

        front_gate_center = draw_circle_touching_two_points(
            f_coordinates[0], f_coordinates[-1], map_rec, color="red"
        )

        front_gate = (
            [f_coordinates[0]] + t3_cor + t4_cor + [f_coordinates[-1], f_coordinates[0]]
        )
        folium.Polygon(
            locations=front_gate,  # 4개의 좌표 리스트
            color="green",  # 경계선 색깔
            fill=True,
            fill_color="red",  # 내부 색깔
            fill_opacity=0.5,
        ).add_to(map_rec)

        t3_cor = calculate_intermediate_points(f_coordinates[1], f_coordinates[0], 50)
        t4_cor = calculate_intermediate_points(f_coordinates[-2], f_coordinates[-1], 50)

        back_gate_center = draw_circle_touching_two_points(
            f_coordinates[1], f_coordinates[-2], map_rec
        )
        back_gate = t3_cor + [f_coordinates[1], f_coordinates[-2]] + t4_cor + t3_cor
        folium.Polygon(
            locations=back_gate,  # 4개의 좌표 리스트
            color="green",  # 경계선 색깔
            fill=True,
            fill_color="blue",  # 내부 색깔
            fill_opacity=0.5,
        ).add_to(map_rec)

    return {
        "front_gate": front_gate,
        "back_gate": back_gate,
        "front_gate_center": front_gate_center,
        "back_gate_center": back_gate_center,
    }


def get_pop_text(road_name_kr):
    return f"""
        <div style="text-align: center; white-space: nowrap; font-size: 14px;">
            <b>{road_name_kr}</b>
        </div>
    """


########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################

from geopy.distance import geodesic


def calculate_intermediate_points(start, end, interval):
    """
    시작점과 끝점 사이를 따라 일정 간격으로 좌표를 계산하는 함수.

    Args:
        start (tuple): 시작점의 좌표 (위도, 경도)
        end (tuple): 끝점의 좌표 (위도, 경도)
        interval (float): 간격 (미터 단위)

    Returns:
        list: 간격에 따라 계산된 좌표 리스트
    """
    # 2번과 3번 좌표 간의 전체 거리 계산
    total_distance = geodesic(start, end).meters

    # 간격에 따른 좌표 계산
    points = []
    # num_points = int(total_distance // interval)  # 생성할 좌표의 개수

    ratio = interval / total_distance
    # 각 점의 위도, 경도 계산
    lat = start[0] + (end[0] - start[0]) * ratio
    lon = start[1] + (end[1] - start[1]) * ratio
    points.append([lat, lon])

    return points


def calculate_midpoint(point1, point2):
    return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2]


def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def draw_circle_touching_two_points(point1, point2, map_rec, color="blue"):
    midpoint = calculate_midpoint(point1, point2)

    radius = geodesic(point1, point2).meters / 2

    # radius = calculate_distance(point1, point2) / 2

    folium.Circle(
        location=midpoint,
        radius=radius,  # Convert to meters (approximation)
        color="green",
        fill=True,
        fill_color=color,
        fill_opacity=0.5,
    ).add_to(map_rec)
    return {"midpoint": midpoint, "radius": radius}
