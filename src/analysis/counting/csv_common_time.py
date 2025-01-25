import json
import os
import pandas as pd
import traceback
from utils.directroy_util import directory_pick_one_day_read
from utils.env_path_util import processed_path
from targets.time.time_filter import generate_time_intervals
from targets.time.time_filter import init_time_range
from targets.time.time_filter import filter_data_by_time_range
from chart.time_chart import time_chart_valued_sort




def csv_time(display_name, display_id, year, month, one_day, start_hour, hour_range, interval_minutes, interval_seconds):
    json_file_path = \
        directory_pick_one_day_read(display_name, display_id,year, month, one_day)
    
    if(not json_file_path):
        raise ValueError(f"{display_name}의 {display_id} 매체 {year}년도 {month}월 데이터가 없습니다.")
    
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    if not json_data:
        raise ValueError(f"{display_name}의 {display_id} 매체 {year}년도 {month}월 데이터가 없습니다.")
    
    time_interval_list = generate_time_intervals(start_hour, hour_range, interval_minutes,interval_seconds)
    time_range_dict = init_time_range(time_interval_list)
    error_file_dict = {}
    
    csv_files = json_data[display_id]
    if len(csv_files) == 0 :
        raise ValueError(f"{display_name}의 {display_id} 매체 {year}년도 {month}월 데이터가 없습니다.")
    
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
            csv_data['appear_timing'] = pd.to_datetime(csv_data['appear_timing'], format='%H:%M:%S').dt.time
            
            # 데이터 유무 체크
            if csv_data.empty:
                error_file_dict[display_id].append(csv_file)
                continue
            
            filter_data_by_time_range(csv_data,time_range_dict)
            
        except Exception as e:
            print("에러 발생:", e)
            # traceback.print_exc()  # 에러의 상세 내용을 출력
            error_file_dict[display_id].append(csv_file)
    # 에러 파일 json 파일 저장
    json_file_path = f'{processed_path}/error_csv_time_{display_name}_{display_id}_{year}_{month}_{one_day}.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(error_file_dict, f, ensure_ascii=False, indent=4) 
        
    # 전처리 데이터 파일 저장
    json_file_path = f'{processed_path}/csv_time_{display_name}_{display_id}_{year}_{month}_{one_day}_{hour_range}_duration.json'
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(time_range_dict, f, ensure_ascii=False, indent=4) 
    time_chart_valued_sort(display_name,display_id,year,month,time_range_dict,interval_minutes, interval_seconds)


