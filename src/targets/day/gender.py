# csv  target 기준 카운팅 함수
def csv_day_gender(display_id, csv_data, csv_rank_dict, target):

    gender_list = csv_data[target].to_list()

    male_count = sum(1 for gender in gender_list if gender > 0)
    female_count = sum(1 for gender in gender_list if gender < 0)

    csv_rank_dict[display_id]["M"] += male_count
    csv_rank_dict[display_id]["F"] += female_count
