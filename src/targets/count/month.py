from utils.datetime_util import find_day


# csv  target 기준 카운팅 함수
def csv_count_month(key, csv_file, csv_data, csv_count_dict, target, month):
    date = csv_file.split("_")[-1].split(".")[0]
    count = len(csv_data[target].to_list())
    csv_count_dict[key][month][date] = {"count": count, "date": find_day(date)}
