from utils.datetime_util import find_day
from utils.csv_features_util import target_list


def csv_count_age_gender(key, csv_file, csv_data, csv_count_dict, month):
    date = csv_file.split("_")[-1].split(".")[0]

    # 연령 및 성별 데이터 리스트 생성
    gender_list = csv_data[target_list[1]].to_list()
    age_list = csv_data[target_list[2]].to_list()

    # 각 연령대별 성별 카운트를 초기화
    if "age_0_20_Male" not in csv_count_dict[key][month]:
        csv_count_dict[key][month] = {
            "age_0_20_Male": {},
            "age_0_20_Female": {},
            "age_20_40_Male": {},
            "age_20_40_Female": {},
            "age_40_60_Male": {},
            "age_40_60_Female": {},
            "age_60_above_Male": {},
            "age_60_above_Female": {},
        }

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
        csv_count_dict[key][month][age_gender_key][date] = {
            "count": count,
            "date": find_day(date),
        }
