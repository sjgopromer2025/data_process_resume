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
import folium


def generate_time_intervals(
    start_hour, hour_range, interval_minutes=0, interval_seconds=0
):

    # 시작 시간을 소수로 받아 시간과 분으로 분리
    hours = int(start_hour)
    minutes = int((start_hour - hours) * 60)
    start_time = datetime.strptime(f"{hours}:{minutes:02d}", "%H:%M")

    # 종료 시간을 소수로 받아 시간과 분으로 분리
    range_hours = int(hour_range)
    range_minutes = int((hour_range - range_hours) * 60)
    end_time = start_time + timedelta(hours=range_hours, minutes=range_minutes)

    # 결과를 저장할 리스트
    intervals = []
    # 시작 시간부터 종료 시간까지 interval(간격)만큼 시간 증가
    current_time = start_time
    while current_time <= end_time:
        intervals.append(current_time.strftime("%H:%M:%S"))
        current_time += timedelta(minutes=interval_minutes, seconds=interval_seconds)

    return intervals


# 예시: (9, 2, 0.2)일 때의 출력
# result = generate_time_intervals(9, 2, 0.3)
# print(result)


def init_time_range(time_intervals):
    filtered_data = {}

    # 시간 구간별로 데이터 필터링
    for i in range(len(time_intervals) - 1):
        start_time = datetime.strptime(time_intervals[i], "%H:%M:%S")
        end_time = datetime.strptime(time_intervals[i + 1], "%H:%M:%S")

        # 현재 구간의 데이터 저장할 리스트
        filtered_data[
            f"{start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
        ] = {"data": None, "gps": None}

    return filtered_data


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
    }


def filter_gps_by_time_range(
    gps_data: pd.DataFrame, time_range_dict, polygon_infos: dict, time_diff_dict: dict
):

    base_polygon = polygon_infos["base_polygon"]
    front_polygon = polygon_infos["front_polygon"]
    back_polygon = polygon_infos["back_polygon"]
    front_gate_center = polygon_infos["front_gate_center"]
    back_gate_center = polygon_infos["back_gate_center"]

    time_range_list_keys = time_range_dict.keys()
    filtered_data_list = []

    for time_range in time_range_list_keys:
        start_time, end_time = map(
            lambda t: datetime.strptime(t, "%H:%M:%S").time(), time_range.split(" - ")
        )
        # # 시간 범위에 맞는 행 필터링
        mask = (gps_data["time"] >= start_time) & (gps_data["time"] < end_time)
        filtered_rows: pd.DataFrame = gps_data[mask].copy()

        # 폴리곤 내부 여부 계산
        filtered_rows["in_polygon"] = filtered_rows.apply(
            lambda row: is_within_polygon(
                base_polygon, row["latitude"], row["longitude"]
            ),
            axis=1,
        )

        filtered_rows = filtered_rows[filtered_rows["in_polygon"]]
        if not filtered_rows.empty:

            front_result = is_within_polygon(
                front_polygon,
                filtered_rows.iloc[0]["latitude"],
                filtered_rows.iloc[0]["longitude"],
            )

            back_result = is_within_polygon(
                back_polygon,
                filtered_rows.iloc[0]["latitude"],
                filtered_rows.iloc[0]["longitude"],
            )

            if front_result:
                back_result = is_within_polygon(
                    back_polygon,
                    filtered_rows.iloc[-1]["latitude"],
                    filtered_rows.iloc[-1]["longitude"],
                )
                if back_result:
                    filtered_data_list.append(filtered_rows)
                    time_diff_dict[time_range] = [
                        filtered_rows["time"].iloc[0],
                        filtered_rows["time"].iloc[-1],
                        1,
                    ]
            if back_result:
                front_result = is_within_polygon(
                    front_polygon,
                    filtered_rows.iloc[-1]["latitude"],
                    filtered_rows.iloc[-1]["longitude"],
                )

                if front_result:
                    filtered_data_list.append(filtered_rows)
                    time_diff_dict[time_range] = [
                        filtered_rows["time"].iloc[0],
                        filtered_rows["time"].iloc[-1],
                        2,
                    ]

    # 통계 계산
    if filtered_data_list:
        stat = calculate_statistics(filtered_data_list)
        return stat
    else:
        # 데이터가 없는 경우 빈 결과 반환
        return None


# 시간 범위에 맞는 행만 필터링하는 함수
def filter_data_by_time_range(
    csv_data: pd.DataFrame,
    time_diff_dict: dict,
    time_series_dict: dict,
    road_info: dict = None,
):
    time_diff_dict_keys = time_diff_dict.keys()
    # print(time_range_dict)

    for time_range in time_diff_dict_keys:
        diff_time_range = time_diff_dict[time_range]
        start_time = diff_time_range[0]
        end_time = diff_time_range[1]
        # 시간 범위에 맞는 행 필터링
        mask = (csv_data["appear_timing"] >= start_time) & (
            csv_data["appear_timing"] < end_time
        )
        filtered_rows: pd.DataFrame = csv_data[mask].copy()
        # print(filtered_rows)

        # time 객체를 timedelta로 변환
        start_seconds = timedelta(
            hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second
        )
        end_seconds = timedelta(
            hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second
        )

        # 시간 차이를 초 단위로 계산
        if road_info:
            road_info["road_span_time"] += (end_seconds - start_seconds).total_seconds()

        time_series_dict[time_range] = init_dict_target()

        time_series_dict[time_range]["ad_id"] = Counter(
            filtered_rows["ad_id"].to_list()
        )
        csv_person(time_series_dict[time_range], filtered_rows, target_list[0])
        csv_gender(time_series_dict[time_range], filtered_rows, target_list[1])
        csv_age(time_series_dict[time_range], filtered_rows, target_list[2])
        csv_age_and_gender(time_series_dict[time_range], filtered_rows)
        csv_view(time_series_dict[time_range], filtered_rows, csv_data.columns)
        time_series_dict[time_range]["time_diff"] = [
            diff_time_range[0],
            diff_time_range[1],
        ]

        # f"{diff_time_range[0]} - {diff_time_range[1]}"
        time_series_dict[time_range]["direction"] = diff_time_range[2]

    return


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


def get_time_ranges(start_hour, hour_range, interval_minutes, interval_seconds):
    time_intervals = generate_time_intervals(
        start_hour, hour_range, interval_minutes, interval_seconds
    )
    return init_time_range(time_intervals)
