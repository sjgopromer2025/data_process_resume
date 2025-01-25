import folium
import os
import folium.map
from geopy.distance import geodesic
from utils.env_path_util import processed_path
from map.map_coordinate import map_rectangle_center

# 거리 임계값 (예: 500m 이상일 경우 불규칙한 점프로 간주)
DISTANCE_THRESHOLD = 500  # 단위: 미터


def create_map_time_range(csv_data, time_range):
    # 지도 초기 위치 설정
    start_location = [csv_data.iloc[0]["latitude"], csv_data.iloc[0]["longitude"]]
    map_route = folium.Map(location=start_location, zoom_start=15)

    # 필터링된 경로 저장
    locations = []
    previous_location = None

    # 좌표 간 거리 차이를 계산하여 경로 생성
    for _, row in csv_data.iterrows():
        current_location = (row["latitude"], row["longitude"])

        # 이전 좌표와 비교하여 임계값을 초과하면 무시
        if previous_location:
            distance = geodesic(previous_location, current_location).meters
            if distance > DISTANCE_THRESHOLD:
                # print(f"Skipping outlier point at {current_location} with distance: {distance}m")
                continue

        locations.append(current_location)
        previous_location = current_location

    # 경로를 지도에 추가

    # print(locations)
    folium.PolyLine(locations, color="blue", weight=5).add_to(map_route)

    # 시작과 종료 마커
    folium.Marker(
        location=start_location, popup="Start", icon=folium.Icon(color="green")
    ).add_to(map_route)
    folium.Marker(
        location=locations[-1], popup="End", icon=folium.Icon(color="red")
    ).add_to(map_route)

    # 지도 저장
    map_route.save(
        f'{"_".join(time_range.replace(":","_").split(" - "))}_route_map.html'
    )


def create_map(csv_data, display_name, display_id, year, month, day):
    # 지도 초기 위치 설정
    start_location = [csv_data.iloc[0]["latitude"], csv_data.iloc[0]["longitude"]]
    map_route = folium.Map(location=start_location, zoom_start=13)

    # 필터링된 경로 저장
    locations = []
    previous_location = None

    # 좌표 간 거리 차이를 계산하여 경로 생성
    for _, row in csv_data.iterrows():
        current_location = (row["latitude"], row["longitude"])

        # 이전 좌표와 비교하여 임계값을 초과하면 무시
        if previous_location:
            distance = geodesic(previous_location, current_location).meters
            if distance > DISTANCE_THRESHOLD:
                # print(f"Skipping outlier point at {current_location} with distance: {distance}m")
                continue

        locations.append(current_location)
        previous_location = current_location

    # 경로를 지도에 추가

    # print(locations)
    folium.PolyLine(locations, color="blue", weight=5).add_to(map_route)

    # 시작과 종료 마커
    folium.Marker(
        location=start_location, popup="Start", icon=folium.Icon(color="green")
    ).add_to(map_route)
    folium.Marker(
        location=locations[-1], popup="End", icon=folium.Icon(color="red")
    ).add_to(map_route)

    # 지도 저장
    map_name = f'{"_".join([display_name,display_id,year,month,day])}_total_map.html'
    # 이미지 파일로 저장
    map_save_path = os.path.join(
        processed_path, display_name, display_id, "GPS", "total_maps"
    )
    os.makedirs(map_save_path, exist_ok=True)

    map_route.save(os.path.join(map_save_path, map_name))
    return map_route


def create_map_point_and_rectangle(
    csv_data, rectangle, display_name, display_id, year, month, day, road_name
):
    map_center = map_rectangle_center(rectangle[:-1])
    map_route = folium.Map(location=map_center, zoom_start=12)

    # 사각형 추가
    folium.Polygon(
        locations=rectangle,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.4,
    ).add_to(map_route)

    # # 필터링된 좌표 추가
    # for _, row in filtered_df.iterrows():
    #     folium.Marker(
    #         location=[row["latitude"], row["longitude"]],
    #         popup=f"Time: {row['time']}, Speed: {row['speed']} km/h",
    #         icon=folium.Icon(color="red", icon="info-sign"),
    #     ).add_to(m)

    # 필터링된 좌표에 점 찍기 (CircleMarker 사용)
    for _, row in csv_data.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,  # 점의 크기 조절
            color="red",  # 테두리 색상
            fill=True,
            fill_color="red",  # 점 안의 색상
            fill_opacity=0.7,  # 점의 투명도
            popup=f"Time: {row['time']}, Speed: {row['speed']} km/h",
        ).add_to(map_route)

    # 지도 저장
    map_name = (
        f'{"_".join([display_name,display_id,year,month,day])}_rectangle_point_map.html'
    )
    # 이미지 파일로 저장
    map_save_path = os.path.join(
        processed_path, display_name, display_id, "GPS", "rectangle_and_point"
    )
    os.makedirs(map_save_path, exist_ok=True)

    map_route.save(os.path.join(map_save_path, map_name))


def create_map_point_and_rectangle_test(map_route: folium.map, rectangle):
    # 사각형 추가
    folium.Polygon(
        locations=rectangle,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.4,
    ).add_to(map_route)
    return
