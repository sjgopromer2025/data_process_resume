from datetime import datetime, timedelta
from utils.csv_features_util import appear_timing
from utils.env_path_util import attention_time
from utils.env_path_util import exposed_time
from utils.env_path_util import watched_time
from utils.init_dict_util import init_dict_target
from utils.csv_features_util import target_list


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
        ] = init_dict_target()

    return filtered_data


# # 예제 사용
# time_intervals = ['09:00:00', '09:12:00', '09:24:00', '09:36:00', '09:48:00', '10:00:00', '10:12:00', '10:24:00', '10:36:00', '10:48:00']
# data_times = ['09:05:00', '09:15:00', '09:20:00', '09:35:00', '10:05:00']

# filtered_data = filter_data_by_time_range(time_intervals, data_times)
# print(filtered_data)


# 시간 범위에 맞는 행만 필터링하는 함수
def filter_data_by_time_range(csv_data, time_range_dict):
    time_range_list_keys = time_range_dict.keys()

    for time_range in time_range_list_keys:
        start_str, end_str = time_range.split(" - ")
        start_time = datetime.strptime(start_str, "%H:%M:%S").time()
        end_time = datetime.strptime(end_str, "%H:%M:%S").time()

        # 시간 범위에 맞는 행 필터링
        mask = (csv_data[appear_timing] >= start_time) & (
            csv_data[appear_timing] < end_time
        )
        filtered_rows = csv_data[mask]

        csv_person(time_range_dict, time_range, filtered_rows, target_list[0])
        csv_gender(time_range_dict, time_range, filtered_rows, target_list[1])
        csv_age(time_range_dict, time_range, filtered_rows, target_list[2])
        csv_age_and_gender(time_range_dict, time_range, filtered_rows)
        csv_view(time_range_dict, time_range, filtered_rows, csv_data.columns)

    return


# csv  target 기준 카운팅 함수
def csv_person(time_range_dict, time_range, filtered_rows, target):
    count = len(filtered_rows[target].to_list())

    time_range_dict[time_range][target] += count


def csv_view(time_range_dict, time_range, filtered_rows, csv_data_columns):
    if "attention_time" in csv_data_columns and not filtered_rows.empty:
        time_range_dict[time_range]["time"]["attention"] += int(
            (filtered_rows["attention_time"] > attention_time).sum()
        )

    if "exposed_time" in csv_data_columns and not filtered_rows.empty:
        time_range_dict[time_range]["time"]["exposed"] += int(
            (filtered_rows["exposed_time"] > exposed_time).sum()
        )

    if "watched_time" in csv_data_columns and not filtered_rows.empty:
        time_range_dict[time_range]["time"]["watched"] += int(
            (filtered_rows["watched_time"] > watched_time).sum()
        )


# csv  target 기준 카운팅 함수
def csv_gender(time_range_dict, time_range, filtered_rows, target):

    gender_list = filtered_rows[target].to_list()

    male_count = sum(1 for gender in gender_list if gender > 0)
    female_count = sum(1 for gender in gender_list if gender < 0)

    time_range_dict[time_range][target]["M"] += male_count
    time_range_dict[time_range][target]["F"] += female_count


# csv  target 기준 카운팅 함수
def csv_age(time_range_dict, time_range, filtered_rows, target):
    # 성별에 따라 분류
    age_list = filtered_rows[target].to_list()

    age_0_20 = sum(1 for age in age_list if 0 <= age < 20)
    age_20_40 = sum(1 for age in age_list if 20 <= age < 40)
    age_40_60 = sum(1 for age in age_list if 40 <= age < 60)
    age_60_above = sum(1 for age in age_list if age >= 60)

    time_range_dict[time_range][target]["age_0_20"] += age_0_20
    time_range_dict[time_range][target]["age_20_40"] += age_20_40
    time_range_dict[time_range][target]["age_40_60"] += age_40_60
    time_range_dict[time_range][target]["age_60_above"] += age_60_above


def csv_age_and_gender(time_range_dict, time_range, filtered_rows):

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
        time_range_dict[time_range]["age_and_gender"][age_gender_key] += count
