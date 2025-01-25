from utils.datetime_util import find_day


# csv  target 기준 카운팅 함수
def csv_count_age(key, csv_file, csv_data, csv_count_dict, target, month):
    date = csv_file.split("_")[-1].split(".")[0]
    # 성별에 따라 분류
    age_list = csv_data[target].to_list()
    # 각 연령대별 카운트를 날짜별로 업데이트
    if "age_0_20" not in csv_count_dict[key][month]:
        csv_count_dict[key][month] = {
            "age_0_20": {},
            "age_20_40": {},
            "age_40_60": {},
            "age_60_above": {},
        }

    age_0_20 = sum(1 for age in age_list if 0 <= age < 20)
    age_20_40 = sum(1 for age in age_list if 20 <= age < 40)
    age_40_60 = sum(1 for age in age_list if 40 <= age < 60)
    age_60_above = sum(1 for age in age_list if age >= 60)

    # 날짜별 카운트 업데이트
    csv_count_dict[key][month]["age_0_20"][date] = {
        "count": age_0_20,
        "date": find_day(date),
    }
    csv_count_dict[key][month]["age_20_40"][date] = {
        "count": age_20_40,
        "date": find_day(date),
    }
    csv_count_dict[key][month]["age_40_60"][date] = {
        "count": age_40_60,
        "date": find_day(date),
    }
    csv_count_dict[key][month]["age_60_above"][date] = {
        "count": age_60_above,
        "date": find_day(date),
    }
