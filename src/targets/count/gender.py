from utils.datetime_util import find_day


# csv  target 기준 카운팅 함수
def csv_count_gender(key, csv_file, csv_data, csv_count_dict, target, gender, month):
    date = csv_file.split("_")[-1].split(".")[0]
    # 성별에 따라 분류
    gender_list = csv_data[target].to_list()

    if gender == "M":
        count = sum(1 for gender in gender_list if gender > 0)
    elif gender == "F":
        count = sum(1 for gender in gender_list if gender < 0)
    else:
        raise ValueError

    csv_count_dict[key][month][date] = {"count": count, "date": find_day(date)}
