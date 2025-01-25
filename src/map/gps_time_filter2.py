from datetime import datetime, timedelta, time
import pandas as pd
from shapely.geometry import Polygon

from utils.csv_features_util import appear_timing
from utils.env_path_util import attention_time
from utils.env_path_util import exposed_time
from utils.env_path_util import watched_time
from utils.init_dict_util import init_dict_target
from utils.csv_features_util import target_list
from collections import Counter
from map.map_coordinate import is_within_polygon
import numpy as np
import folium


def calculate_statistics(filtered_data_list):
    """
    주어진 필터링된 데이터를 하나로 합치고 통계를 계산합니다.
    """
    # 모든 필터링된 데이터 결합
    combined_data = pd.concat(filtered_data_list, ignore_index=True)

    # 통계 계산
    average_speed = combined_data["speed"].mean() if not combined_data.empty else None
    min_speed = combined_data["speed"].min() if not combined_data.empty else None
    max_speed = combined_data["speed"].max() if not combined_data.empty else None
    road_length = combined_data["distance"].sum() if not combined_data.empty else 0

    return {
        "average_speed": average_speed,
        "min_speed": min_speed,
        "max_speed": max_speed,
        "road_length": road_length,
        "total_span_time": 0,
    }


# csv  target 기준 카운팅 함수
def csv_person(time_series_dict, filtered_rows, target):
    count = len(filtered_rows[target].to_list())
    time_series_dict[target] += count


def csv_view(time_series_dict, filtered_rows, csv_data_columns):
    if "attention_time" in csv_data_columns and not filtered_rows.empty:
        time_series_dict["time"]["attention"] += int(
            (filtered_rows["attention_time"] > attention_time).sum()
        )

    if "exposed_time" in csv_data_columns and not filtered_rows.empty:
        time_series_dict["time"]["exposed"] += int(
            (filtered_rows["exposed_time"] > exposed_time).sum()
        )

    if "watched_time" in csv_data_columns and not filtered_rows.empty:
        time_series_dict["time"]["watched"] += int(
            (filtered_rows["watched_time"] > watched_time).sum()
        )


# csv  target 기준 카운팅 함수
def csv_gender(time_series_dict, filtered_rows, target):

    gender_list = filtered_rows[target].to_list()

    male_count = sum(1 for gender in gender_list if gender > 0)
    female_count = sum(1 for gender in gender_list if gender < 0)

    time_series_dict[target]["M"] += male_count
    time_series_dict[target]["F"] += female_count


# csv  target 기준 카운팅 함수
def csv_age(time_series_dict, filtered_rows, target):
    # 성별에 따라 분류
    age_list = filtered_rows[target].to_list()

    age_0_20 = sum(1 for age in age_list if 0 <= age < 20)
    age_20_40 = sum(1 for age in age_list if 20 <= age < 40)
    age_40_60 = sum(1 for age in age_list if 40 <= age < 60)
    age_60_above = sum(1 for age in age_list if age >= 60)

    time_series_dict[target]["age_0_20"] += age_0_20
    time_series_dict[target]["age_20_40"] += age_20_40
    time_series_dict[target]["age_40_60"] += age_40_60
    time_series_dict[target]["age_60_above"] += age_60_above


def csv_age_and_gender(time_series_dict, filtered_rows):

    # 연령 및 성별 데이터 리스트 생성
    gender_list = filtered_rows[target_list[1]].to_list()
    age_list = filtered_rows[target_list[2]].to_list()

    # 연령대 및 성별별 카운트 계산
    age_gender_counts = {
        "age_0_20_Male": 0,
        "age_0_20_Female": 0,
        "age_20_40_Male": 0,
        "age_20_40_Female": 0,
        "age_40_60_Male": 0,
        "age_40_60_Female": 0,
        "age_60_above_Male": 0,
        "age_60_above_Female": 0,
    }

    for age, gender in zip(age_list, gender_list):
        if 0 <= age < 20:
            if gender > 0:
                age_gender_counts["age_0_20_Male"] += 1
            elif gender < 0:
                age_gender_counts["age_0_20_Female"] += 1
        elif 20 <= age < 40:
            if gender > 0:
                age_gender_counts["age_20_40_Male"] += 1
            elif gender < 0:
                age_gender_counts["age_20_40_Female"] += 1
        elif 40 <= age < 60:
            if gender > 0:
                age_gender_counts["age_40_60_Male"] += 1
            elif gender < 0:
                age_gender_counts["age_40_60_Female"] += 1
        elif age >= 60:
            if gender > 0:
                age_gender_counts["age_60_above_Male"] += 1
            elif gender < 0:
                age_gender_counts["age_60_above_Female"] += 1

    # 날짜별로 카운트를 csv_count_dict에 저장
    for age_gender_key, count in age_gender_counts.items():
        time_series_dict["age_and_gender"][age_gender_key] += count


######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################


def filter_gps_by_load(
    gps_data: pd.DataFrame,
    polygon_infos: dict,
    time_info: dict,
):

    base_polygon = polygon_infos["base_polygon"]
    front_polygon = polygon_infos["front_polygon"]
    back_polygon = polygon_infos["back_polygon"]
    front_gate_center = polygon_infos["front_gate_center"]
    back_gate_center = polygon_infos["back_gate_center"]

    filtered_rows: pd.DataFrame = gps_data.copy()
    filtered_rows["in_polygon"] = filtered_rows.apply(
        lambda row: is_within_polygon(base_polygon, row["latitude"], row["longitude"]),
        axis=1,
    )
    filtered_rows = filtered_rows[filtered_rows["in_polygon"]]

    if not filtered_rows.empty:
        filtered_rows["front_polygon"] = filtered_rows.apply(
            lambda row: is_within_polygon(
                front_polygon, row["latitude"], row["longitude"]
            ),
            axis=1,
        )

        filtered_rows["back_polygon"] = filtered_rows.apply(
            lambda row: is_within_polygon(
                back_polygon, row["latitude"], row["longitude"]
            ),
            axis=1,
        )

        # in_polygon 컬럼 삭제
        filtered_rows = filtered_rows.drop(columns=["in_polygon"])
        filtered_rows.to_csv("filtered_rows.csv")
        groups = csv_data_groupping(filtered_rows, time_info)

        # groups.to_csv("groups.csv")
        road_info_process_data(filtered_rows, groups)
        return groups

    return None


def road_info_process_data(csv_data: pd.DataFrame, groups: dict):
    # stat = calculate_statistics([filtered_rows])
    for time_range in groups.keys():
        groups[time_range]["road_info"]["total_road_info"] = (
            common_road_info_process_data(csv_data, time_range)
        )
        for time_range2 in groups[time_range]["road_info"].keys():
            if time_range2 != "total_road_info":
                groups[time_range]["road_info"][time_range2] = (
                    common_road_info_process_data(csv_data, time_range2)
                )

    return


def common_road_info_process_data(csv_data: pd.DataFrame, time_range: str):
    # stat = calculate_statistics([filtered_rows])
    start_time_str, end_time_str = time_range.split(" - ")
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
    # 시간 범위에 맞는 행 필터링
    mask = (csv_data["time"] >= start_time) & (csv_data["time"] <= end_time)
    filtered_rows: pd.DataFrame = csv_data[mask].copy()
    stat = calculate_statistics([filtered_rows])
    # time 객체를 timedelta로 변환
    start_seconds = timedelta(
        hours=start_time.hour,
        minutes=start_time.minute,
        seconds=start_time.second,
    )
    end_seconds = timedelta(
        hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second
    )

    # 시간 차이를 초 단위로 계산
    stat["total_span_time"] += (end_seconds - start_seconds).total_seconds()

    return convert_numpy_types(stat)


# numpy 데이터 타입을 Python 기본 데이터 타입으로 변환
def convert_numpy_types(data):
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, (np.integer, np.floating)):
        return data.item()  # numpy 데이터를 Python 기본 타입으로 변환
    else:
        return data


# 도로 시간대 그룹핑 및 시간대 범위 생성
def csv_data_groupping(df: pd.DataFrame, time_info: dict):

    # 결과 저장용 리스트
    groups = []
    current_group = []

    # 시간 차 기준 (예: 1분)
    time_threshold = timedelta(minutes=2)
    for i, row in df.iterrows():
        # 현재 행의 조건
        is_front_true = row["front_polygon"] == True
        is_back_true = row["back_polygon"] == True
        current_time = row["time2"]

        if not current_group:
            # 그룹이 비어있을 때 시작 조건 설정
            if is_front_true:
                current_group.append([row["time"], "front", row["time2"]])

            if is_back_true:
                current_group.append([row["time"], "back", row["time2"]])
        else:
            # 그룹이 시작된 상태
            start_direction = current_group[0][1]  # front or back

            last_direction = current_group[-1][1]
            if start_direction == last_direction:
                # # True면 front 인데 is_back_true가 True면 그룹 종료
                if start_direction == "front":
                    if is_back_true:
                        current_group.append([row["time"], "back", row["time2"]])
                        # groups.append(current_group)

                if start_direction == "back":
                    if is_front_true:
                        current_group.append([row["time"], "front", row["time2"]])

            elif start_direction != last_direction:
                # 리스트에 이미 front와 back이 존재하고 있는 경우
                # 여기서 front일 경우 back 마지막 리스트에 추가된 상태임 (front, back, ?)
                # 3번 째 아이템이 front일 경우 그룹 종료 후 새로이 그룹 생성
                # 3번 째 아이템이 back일 경우 시간 차이 계산하여 그룹 종료할지 판단

                # 시간 차가 기준 초과 → 새로운 그룹 시작
                last_time = current_group[-1][2]
                time_diff = current_time - last_time
                time_check = time_diff > time_threshold

                if start_direction == "front":
                    if is_front_true:
                        groups.append(current_group)
                        current_group = []
                        current_group.append([row["time"], "front", row["time2"]])
                        # groups.append(current_group)
                    if is_back_true:
                        if time_check:
                            groups.append(current_group)
                            current_group = []
                        current_group.append([row["time"], "back", row["time2"]])

                if start_direction == "back":
                    if is_back_true:
                        groups.append(current_group)
                        current_group = []
                        current_group.append([row["time"], "back", row["time2"]])
                    if is_front_true:
                        if time_check:
                            groups.append(current_group)
                            current_group = []
                        current_group.append([row["time"], "front", row["time2"]])

    # 마지막 그룹 추가
    if current_group:
        groups.append(current_group)

    # 결과 출력
    # for idx, group in enumerate(groups):
    # print(f"Group {idx + 1}:")
    # print(pd.DataFrame(group))

    return road_time_process_data(groups, time_info)


def road_time_process_data(data, time_info):
    result = {}

    for entry in data:
        # Convert to datetime objects directly
        start_time = entry[0][2]
        end_time = entry[-1][2]

        time_range = (
            f"{start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
        )

        if entry[0][1] == "back" and entry[-1][1] == "front":
            direction_text = "back to front"
            direction_value = 2
        elif entry[0][1] == "front" and entry[-1][1] == "back":
            direction_text = "front to back"
            direction_value = 1
        else:
            direction_text = "unknown"
            direction_value = 0

        time_series_list = road_generate_time_range(
            start_time,
            end_time,
            time_info["interval_minutes"],
            time_info["interval_seconds"],
        )
        result[time_range] = {
            "direction_text": direction_text,
            "direction": direction_value,
            "total_road_data": {},
            "road_info": {"total_road_info": None}
            | {time_series: None for time_series in time_series_list},
            "time_range": time_series_list,
            "time_series": {time_series: None for time_series in time_series_list},
        }

    return result


# 도로 시간대 안에서 시간 분리
def road_generate_time_range(
    start_time, end_time, interval_minutes=0, interval_seconds=0
):
    interval = timedelta(minutes=interval_minutes, seconds=interval_seconds)
    current_time = start_time
    intervals = []

    while current_time + interval <= end_time:
        next_time = current_time + interval
        intervals.append(
            f"{current_time.strftime('%H:%M:%S')} - {next_time.strftime('%H:%M:%S')}"
        )
        current_time = next_time

    if current_time < end_time:
        intervals.append(
            f"{current_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
        )

    return intervals


# 시간 범위에 맞는 행만 필터링하는 함수
def filter_data_by_time_range2(
    csv_data: pd.DataFrame,
    road_time_range: dict,
    road_info: dict = None,
):
    road_time_range_keys = road_time_range.keys()
    # print(time_range_dict)

    for time_range in road_time_range_keys:
        start_time_str, end_time_str = time_range.split(" - ")
        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
        # 시간 범위에 맞는 행 필터링
        mask = (csv_data["appear_timing"] >= start_time) & (
            csv_data["appear_timing"] < end_time
        )
        filtered_rows: pd.DataFrame = csv_data[mask].copy()

        # print(filtered_rows)
        # time 객체를 timedelta로 변환
        start_seconds = timedelta(
            hours=start_time.hour,
            minutes=start_time.minute,
            seconds=start_time.second,
        )
        end_seconds = timedelta(
            hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second
        )
        # 시간 차이를 초 단위로 계산
        if road_info:
            road_info["road_span_time"] += (end_seconds - start_seconds).total_seconds()

        road_time_range[time_range]["total_road_data"] = init_dict_target()
        prop_data_process(
            road_time_range[time_range]["total_road_data"], filtered_rows, csv_data
        )
        filter_data_by_time_range3(csv_data, road_time_range[time_range]["time_series"])
    return


# 시간 범위에 맞는 행만 필터링하는 함수
def filter_data_by_time_range3(
    csv_data: pd.DataFrame,
    time_series: dict,
    road_info: dict = None,
):
    time_series_keys = time_series.keys()
    # print(time_range_dict)

    for time_range in time_series_keys:
        start_time_str, end_time_str = time_range.split(" - ")
        start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
        # 시간 범위에 맞는 행 필터링
        mask = (csv_data["appear_timing"] >= start_time) & (
            csv_data["appear_timing"] < end_time
        )
        filtered_rows: pd.DataFrame = csv_data[mask].copy()

        # print(filtered_rows)
        # time 객체를 timedelta로 변환
        start_seconds = timedelta(
            hours=start_time.hour,
            minutes=start_time.minute,
            seconds=start_time.second,
        )
        end_seconds = timedelta(
            hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second
        )
        # 시간 차이를 초 단위로 계산
        if road_info:
            road_info["road_span_time"] += (end_seconds - start_seconds).total_seconds()

        time_series[time_range] = init_dict_target()
        prop_data_process(time_series[time_range], filtered_rows, csv_data)


def prop_data_process(data_dict, filtered_rows: pd.DataFrame, csv_data: pd.DataFrame):
    # print("prop_data_process")
    data_dict["ad_id"] = Counter(filtered_rows["ad_id"].to_list())
    csv_person(
        data_dict,
        filtered_rows,
        target_list[0],
    )
    csv_gender(
        data_dict,
        filtered_rows,
        target_list[1],
    )
    csv_age(
        data_dict,
        filtered_rows,
        target_list[2],
    )
    csv_age_and_gender(data_dict, filtered_rows)
    csv_view(
        data_dict,
        filtered_rows,
        csv_data.columns,
    )

    return
