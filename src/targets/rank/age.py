# csv  target 기준 카운팅 함수
def csv_rank_age(display_id, csv_data, csv_rank_dict, target):
    # 성별에 따라 분류
    age_list = csv_data[target].to_list()

    age_0_20 = sum(1 for age in age_list if 0 <= age < 20)
    age_20_40 = sum(1 for age in age_list if 20 <= age < 40)
    age_40_60 = sum(1 for age in age_list if 40 <= age < 60)
    age_60_above = sum(1 for age in age_list if age >= 60)

    csv_rank_dict[display_id]["age_0_20"] += age_0_20
    csv_rank_dict[display_id]["age_20_40"] += age_20_40
    csv_rank_dict[display_id]["age_40_60"] += age_40_60
    csv_rank_dict[display_id]["age_60_above"] += age_60_above
