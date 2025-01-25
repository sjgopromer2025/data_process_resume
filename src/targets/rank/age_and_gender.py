from utils.csv_features_util import target_list


def csv_rank_age_gender(display_id, csv_data, csv_rank_dict):

    # 연령 및 성별 데이터 리스트 생성
    gender_list = csv_data[target_list[1]].to_list()
    age_list = csv_data[target_list[2]].to_list()

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
        csv_rank_dict[display_id][age_gender_key] += count
