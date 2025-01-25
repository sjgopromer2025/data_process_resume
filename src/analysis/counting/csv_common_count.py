import pandas as pd
import json
import os
import traceback
from targets.count.month import csv_count_month
from targets.count.gender import csv_count_gender
from targets.count.age import csv_count_age
from targets.count.age_and_gender import csv_count_age_gender
from utils.directroy_util import directory_total_read
from utils.env_path_util import processed_path
from chart.count_chart import count_chart_valued_sort

# csv  target 기준 카운팅 함수
def csv_count(display_name, year, display_id, target, gender=None):
    json_file_path = directory_total_read(display_name, year)
    
    # print(json_file_path)
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    
    # print(json_data)
    if not json_data:
        raise ValueError(f"{display_name}의 {year}데이터가 없습니다.")
    
    display_months = list(json_data[display_id].keys())
    error_file_dict = {}
    csv_count_dict = {}
    # print(display_months)
    
    error_file_dict[display_id] = []
    csv_count_dict[display_id] = {}
    
    for month in display_months:
        csv_files = json_data[display_id][month]
        if len(csv_files) == 0 :
            continue
        # print(csv_files)
        csv_count_dict[display_id][month] = {}
        #해당 월 csv 파일 리스트
        for csv_file in csv_files:
            # 파일 자체 사이즈 0이면 pass
            if os.path.getsize(csv_file) == 0:
                error_file_dict[display_id].append(csv_file)
                # print("CSV 파일이 비어 있습니다.")
                continue
            #csv read
            try:
                csv_data = pd.read_csv(csv_file ,encoding="utf-8",on_bad_lines="skip").dropna()
                # 속성 공백 제거
                csv_data.columns =csv_data.columns.str.strip()
                # 중복 행 삭제
                csv_data = csv_data.drop_duplicates(subset="person_id", keep="first")
                
                # 데이터 유무 체크
                if csv_data.empty:
                    error_file_dict[display_id].append(csv_file)
                    continue
                # target에 따라 구분 처리
                target_title = targeting(display_id,csv_file, csv_data, csv_count_dict,month, target, gender)
                
            except Exception as e:
                print("에러 발생:", e)
                # traceback.print_exc()  # 에러의 상세 내용을 출력
                error_file_dict[display_id].append(csv_file)

    
    # 에러 파일 json 파일 저장
    json_file_path = f'{processed_path}/error_csv_day_{display_name}_{display_id}_{year}.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4) 


    json_file_path = f'{processed_path}/csv_count_{display_name}_{display_id}_{year}_{target_title}.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(csv_count_dict, f, ensure_ascii=False, indent=4) 
    count_chart_valued_sort(csv_count_dict,display_id,target,year,display_name,target_title)
    

# target에 따라 처리 구분
def targeting(key,csv_file, csv_data, csv_count_dict, month, target, gender):
    target_list = ["person_id", "gender", "age","age_and_gender"]
    if target == target_list[0]:
        csv_count_month(key,csv_file, csv_data, csv_count_dict, target, month)
        return "person_id"
    elif target == target_list[1] and gender is not None:
        csv_count_gender(key,csv_file, csv_data, csv_count_dict, target,gender, month)
        if gender == "M":
            return "gender_Males"
        elif gender == "F":
            return "gender_Females"
        else:
            raise ValueError
    elif target == target_list[2]:
        csv_count_age(key,csv_file, csv_data, csv_count_dict, target, month)  
        return "age"
    elif target == target_list[3]:
        csv_count_age_gender(key,csv_file, csv_data, csv_count_dict, month)  
        return "age_and_gender"

