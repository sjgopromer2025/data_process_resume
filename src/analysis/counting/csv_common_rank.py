import json
import os
import pandas as pd
import traceback
from utils.directroy_util import directory_month_total_read
from utils.init_dict_util import init_dict
from utils.env_path_util import processed_path
from utils.csv_features_util import target_list
from targets.rank.month import csv_rank_month
from targets.rank.gender import csv_rank_gender
from targets.rank.age import csv_rank_age
from targets.rank.age_and_gender import csv_rank_age_gender
from chart.rank_chart import rank_chart_valued_sort

def csv_rank(display_name, year, month, target):
    json_file_path = directory_month_total_read(display_name, year, month)

    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        
    # print(json_data)
    if not json_data:
        raise ValueError(f"{display_name}의 {year}데이터가 없습니다.")

    display_ids = list(json_data.keys())
    
    error_file_dict = {}
    csv_rank_dict = {}
    for display_id in display_ids:
        csv_files = json_data[display_id]
        if len(csv_files) == 0 :
            continue
        
        init_dict(display_id, target, csv_rank_dict)
        
        error_file_dict[display_id] = []
        for csv_file in csv_files:
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
                # print(df_unique)
                targeting(display_id,csv_data,csv_rank_dict,target)
                
            except Exception as e:
                print("에러 발생:", e)
                # traceback.print_exc()  # 에러의 상세 내용을 출력
                error_file_dict[display_id].append(csv_file)
                
    
    # 에러 파일 json 파일 저장
    json_file_path = f'{processed_path}/error_csv_rank_{display_name}_{display_id}_{year}_{month}.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4) 
        
    # 전처리 데이터 파일 저장
    json_file_path = f'{processed_path}/csv_rank_{display_name}_{display_id}_{year}_{month}_{target}.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(csv_rank_dict, f, ensure_ascii=False, indent=4) 
    rank_chart_valued_sort(csv_rank_dict,target,year,display_name,month)
    



# target에 따라 처리 구분
def targeting(display_id,csv_data, csv_rank_dict,  target):
    if target == target_list[0]:
        csv_rank_month(display_id, csv_data, csv_rank_dict, target )
        return "person_id"
    elif target == target_list[1]:
        csv_rank_gender(display_id, csv_data, csv_rank_dict, target )
        return "gender"
    elif target == target_list[2]:
        csv_rank_age(display_id, csv_data, csv_rank_dict, target )  
        return "age"
    elif target == target_list[3]:
        csv_rank_age_gender(display_id, csv_data, csv_rank_dict )  
        return "age_and_gender"

    
        
# csv_rank("BrandDP", "2024", "10", "age_and_gender")