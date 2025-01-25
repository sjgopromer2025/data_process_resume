import datetime
import calendar
from datetime import datetime


days_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

days_dict = {
    "월": "Monday",
    "화": "Tuesday",
    "수": "Wednesday",
    "목": "Thursday",
    "금": "Friday",
    "토": "Saturday",
    "일": "Sunday",
}


# 현재 날짜와 시간을 원하는 형식으로 포맷
current_time = datetime.now().strftime("%Y-%m-%d-%H")


# 요일 정의
def find_day(date_string):
    # 날짜 정의
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    # 요일
    weekday = date_object.strftime("%A")  # %A는 요일을 풀어 쓴 형식입니다.
    return f"{date_string}_{weekday}"


# 월
def get_month_name(month_number):

    if 1 <= int(month_number) <= 12:
        return calendar.month_name[int(month_number)]
    else:
        raise ValueError("Month number must be between 1 and 12.")


# 요일 체크 후 분리
def check_day(csv_files, day_list):
    match_csv_files = []
    for csv_file in csv_files:
        # 날짜 추출 및 요일 구하기
        date_str = csv_file.split("_")[2].split(".")[0]
        weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        if weekday in day_list:
            match_csv_files.append(csv_file)

    return match_csv_files


# 지정 날짜 체크 후 분리
def check_pick_days(csv_files, check_pick_day):
    match_csv_files = []
    for csv_file in csv_files:
        date_str = csv_file.split("_")[2].split(".")[0]
        if date_str in check_pick_day:
            match_csv_files.append(csv_file)

    return match_csv_files


# 지정 날짜 체크 후 분리``
def check_pick_one_day(csv_files, check_pick_day):
    match_csv_files = []
    for csv_file in csv_files:
        date_str = csv_file.split("_")[2].split(".")[0]
        if date_str == check_pick_day:
            match_csv_files.append(csv_file)
    return match_csv_files
