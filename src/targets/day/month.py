# csv  target 기준 카운팅 함수
def csv_day_month(display_id, csv_data, csv_rank_dict, target):
    count = len(csv_data[target].to_list())

    csv_rank_dict[display_id]["count"] += count
