import matplotlib.pyplot as plt
from utils.datetime_util import get_month_name
from utils.env_path_util import report_path
import os
from utils.csv_features_util import target_list


def pick_day_chart_valued_sort(csv_day_dict, target, year, display_name, month):
    display_ids = list(csv_day_dict.keys())

    if target == target_list[0]:
        counts = []
        for display_id in display_ids:
            counts.append(csv_day_dict[display_id]["count"])

        zipped_data = zip(counts, display_ids)
        bar_chart_image_save(
            zipped_data, target, month, year, display_name, "person_id"
        )

    elif target == target_list[1]:
        male_count = []
        female_count = []
        for display_id in display_ids:
            # print(json_data[display_id]["M"]["count"])
            male_count.append(csv_day_dict[display_id]["M"])
            female_count.append(csv_day_dict[display_id]["F"])
        male_zipped_data = zip(male_count, display_ids)
        female_zipped_data = zip(female_count, display_ids)
        bar_chart_image_save(
            male_zipped_data, target, month, year, display_name, "gender_male"
        )
        bar_chart_image_save(
            female_zipped_data, target, month, year, display_name, "gender_female"
        )

    elif target == target_list[2]:
        zip_for_age(csv_day_dict, target, year, display_name, month)
    elif target == target_list[3]:
        zip_for_age_gender(csv_day_dict, target, year, display_name, month)


def bar_chart_image_save(zipped_data, target, month, year, display_name, target_title):
    # y값을 기준으로 내림차순 정렬
    sorted_data = sorted(zipped_data, reverse=True, key=lambda x: x[0])
    sorted_counts, sorted_ids = zip(*sorted_data)
    # min_count = min(sorted_counts)
    # max_count = max(sorted_counts)

    # 바 차트 생성
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_ids, sorted_counts, color="skyblue")

    # x축 눈금 위치와 간격 조정
    plt.xticks(sorted_ids, fontsize=8)  # x축 눈금의 크기와 간격 조정

    # 축 레이블 설정
    plt.xlabel("Display_id")
    plt.ylabel("Count")
    plt.title(
        f"{display_name} {target_title} {get_month_name(month)} Count per Date (Sorted)"
    )
    # plt.ylim(min_count - 100, max_count + 100)  # 여유를 두고 설정
    plt.xticks(rotation=85)
    plt.tight_layout()

    image_name = f"{display_name}_{year}_{month}_{target_title}_pick_day_chart.png"
    # 이미지 파일로 저장
    image_save_path = os.path.join(
        report_path, display_name, "pick_day", year, month, target
    )
    os.makedirs(image_save_path, exist_ok=True)

    plt.savefig(os.path.join(image_save_path, image_name), dpi=300, bbox_inches="tight")
    plt.close()


def zip_for_age(csv_day_dict, target, year, display_name, month):

    display_ids = list(csv_day_dict.keys())

    # 연령대별 리스트 초기화
    age_0_20_counts = []
    age_20_40_counts = []
    age_40_60_counts = []
    age_60_above_counts = []

    # display_ids 목록에서 각 연령대 값 추가
    for display_id in display_ids:
        age_0_20_counts.append(csv_day_dict[display_id]["age_0_20"])
        age_20_40_counts.append(csv_day_dict[display_id]["age_20_40"])
        age_40_60_counts.append(csv_day_dict[display_id]["age_40_60"])
        age_60_above_counts.append(csv_day_dict[display_id]["age_60_above"])

    # zip을 통해 각 연령대와 display_ids 묶기
    age_0_20_zipped_data = zip(age_0_20_counts, display_ids)
    age_20_40_zipped_data = zip(age_20_40_counts, display_ids)
    age_40_60_zipped_data = zip(age_40_60_counts, display_ids)
    age_60_above_zipped_data = zip(age_60_above_counts, display_ids)

    # 각 연령대에 대해 bar_chart_image_save 호출
    bar_chart_image_save(
        age_0_20_zipped_data, target, month, year, display_name, "age_0_20"
    )
    bar_chart_image_save(
        age_20_40_zipped_data, target, month, year, display_name, "age_20_40"
    )
    bar_chart_image_save(
        age_40_60_zipped_data, target, month, year, display_name, "age_40_60"
    )
    bar_chart_image_save(
        age_60_above_zipped_data, target, month, year, display_name, "age_60_above"
    )


def zip_for_age_gender(csv_day_dict, target, year, display_name, month):
    display_ids = list(csv_day_dict.keys())
    # 연령대-성별별 리스트 초기화
    age_0_20_male_counts = []
    age_0_20_female_counts = []
    age_20_40_male_counts = []
    age_20_40_female_counts = []
    age_40_60_male_counts = []
    age_40_60_female_counts = []
    age_60_above_male_counts = []
    age_60_above_female_counts = []

    # display_ids 목록에서 각 연령대-성별 값 추가
    for display_id in display_ids:
        age_0_20_male_counts.append(csv_day_dict[display_id]["age_0_20_Male"])
        age_0_20_female_counts.append(csv_day_dict[display_id]["age_0_20_Female"])
        age_20_40_male_counts.append(csv_day_dict[display_id]["age_20_40_Male"])
        age_20_40_female_counts.append(csv_day_dict[display_id]["age_20_40_Female"])
        age_40_60_male_counts.append(csv_day_dict[display_id]["age_40_60_Male"])
        age_40_60_female_counts.append(csv_day_dict[display_id]["age_40_60_Female"])
        age_60_above_male_counts.append(csv_day_dict[display_id]["age_60_above_Male"])
        age_60_above_female_counts.append(
            csv_day_dict[display_id]["age_60_above_Female"]
        )

    # zip을 통해 각 연령대-성별 데이터와 display_ids 묶기
    age_0_20_male_zipped = zip(age_0_20_male_counts, display_ids)
    age_0_20_female_zipped = zip(age_0_20_female_counts, display_ids)
    age_20_40_male_zipped = zip(age_20_40_male_counts, display_ids)
    age_20_40_female_zipped = zip(age_20_40_female_counts, display_ids)
    age_40_60_male_zipped = zip(age_40_60_male_counts, display_ids)
    age_40_60_female_zipped = zip(age_40_60_female_counts, display_ids)
    age_60_above_male_zipped = zip(age_60_above_male_counts, display_ids)
    age_60_above_female_zipped = zip(age_60_above_female_counts, display_ids)

    # 각 연령대-성별 조합에 대해 bar_chart_image_save 호출
    bar_chart_image_save(
        age_0_20_male_zipped, target, month, year, display_name, "age_0_20_Male"
    )
    bar_chart_image_save(
        age_0_20_female_zipped, target, month, year, display_name, "age_0_20_Female"
    )
    bar_chart_image_save(
        age_20_40_male_zipped, target, month, year, display_name, "age_20_40_Male"
    )
    bar_chart_image_save(
        age_20_40_female_zipped, target, month, year, display_name, "age_20_40_Female"
    )
    bar_chart_image_save(
        age_40_60_male_zipped, target, month, year, display_name, "age_40_60_Male"
    )
    bar_chart_image_save(
        age_40_60_female_zipped, target, month, year, display_name, "age_40_60_Female"
    )
    bar_chart_image_save(
        age_60_above_male_zipped, target, month, year, display_name, "age_60_above_Male"
    )
    bar_chart_image_save(
        age_60_above_female_zipped,
        target,
        month,
        year,
        display_name,
        "age_60_above_Female",
    )
