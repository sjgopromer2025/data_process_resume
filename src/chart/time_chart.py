import matplotlib.pyplot as plt
from utils.datetime_util import get_month_name
from utils.env_path_util import report_path
import os
from utils.datetime_util import current_time


# display_name, display_id, year, month, zipped_data, target, target_title
def bar_chart_image_save(
    display_name, display_id, year, month, zipped_data, target, target_title
):
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
    plt.xlabel(f"{display_id} display")
    plt.ylabel("Count")
    plt.title(f"{display_name} {display_id} {target_title} {get_month_name(month)}")
    # plt.ylim(min_count - 100, max_count + 100)  # 여유를 두고 설정
    plt.xticks(rotation=85)
    plt.tight_layout()

    image_name = f"{display_name}_{display_id}_{year}_{month}_{target_title}_chart.png"
    # 이미지 파일로 저장
    image_save_path = os.path.join(
        report_path,
        display_name,
        "time_filter",
        display_id,
        year,
        month,
        current_time,
        target,
    )
    os.makedirs(image_save_path, exist_ok=True)

    plt.savefig(os.path.join(image_save_path, image_name), dpi=300, bbox_inches="tight")
    plt.close()


def time_chart_valued_sort(
    display_name,
    display_id,
    year,
    month,
    time_range_dict,
    interval_minutes,
    interval_seconds,
):

    # interval_text 생성
    if interval_minutes > 0 and interval_seconds > 0:
        interval_text = f"every_{interval_minutes}_minutes_{interval_seconds}_seconds"
    elif interval_minutes > 0:
        interval_text = f"every_{interval_minutes}_minutes"
    elif interval_seconds > 0:
        interval_text = f"every_{interval_seconds}_seconds"
    else:
        interval_text = "None"
    # 인구수
    zip_for_person_id(
        display_name, display_id, year, month, time_range_dict, interval_text
    )
    # 성별
    zip_for_gender(
        display_name, display_id, year, month, time_range_dict, interval_text
    )
    # 시청수
    zip_for_view(display_name, display_id, year, month, time_range_dict, interval_text)
    # 연령대
    zip_for_age(display_name, display_id, year, month, time_range_dict, interval_text)
    # 성별과 연령
    zip_for_age_gender(
        display_name, display_id, year, month, time_range_dict, interval_text
    )


def zip_for_person_id(
    display_name, display_id, year, month, time_range_dict, interval_text
):
    time_range_key_list = time_range_dict.keys()
    # exposed, watched, attention
    person_list = []

    for time_range in time_range_key_list:
        person_list.append(time_range_dict[time_range]["person_id"])
    zipped_person_data = zip(person_list, time_range_key_list)

    # display_name, display_id, year, month, zipped_data, target, target_title
    target = "person_id"
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_person_data,
        target,
        f"{interval_text}_person_id_count",
    )


def zip_for_gender(
    display_name, display_id, year, month, time_range_dict, interval_text
):
    time_range_key_list = time_range_dict.keys()

    # exposed, watched, attention
    male_list = []
    female_list = []

    for time_range in time_range_key_list:
        male_list.append(time_range_dict[time_range]["gender"]["M"])
        female_list.append(time_range_dict[time_range]["gender"]["F"])

    zipped_male_data = zip(male_list, time_range_key_list)
    zipped_female_data = zip(female_list, time_range_key_list)

    # display_name, display_id, year, month, zipped_data, target, target_title
    target = "gender"
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_male_data,
        target,
        f"{interval_text}_male_count",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_female_data,
        target,
        f"{interval_text}_female_count",
    )


def zip_for_view(display_name, display_id, year, month, time_range_dict, interval_text):
    time_range_key_list = time_range_dict.keys()

    # exposed, watched, attention
    exposed_list = []
    watched_list = []
    attention_list = []

    for time_range in time_range_key_list:
        exposed_list.append(time_range_dict[time_range]["time"]["exposed"])
        watched_list.append(time_range_dict[time_range]["time"]["watched"])
        attention_list.append(time_range_dict[time_range]["time"]["attention"])
    zipped_exposed_data = zip(exposed_list, time_range_key_list)
    zipped_watched_data = zip(watched_list, time_range_key_list)
    zipped_attention_data = zip(attention_list, time_range_key_list)

    # display_name, display_id, year, month, zipped_data, target, target_title
    target = "time"
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_exposed_data,
        target,
        f"{interval_text}_exposed_count",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_watched_data,
        target,
        f"{interval_text}_watched_count",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        zipped_attention_data,
        target,
        f"{interval_text}_attention_count",
    )


def zip_for_age(display_name, display_id, year, month, time_range_dict, interval_text):
    time_range_key_list = time_range_dict.keys()

    # 연령대별 리스트 초기화
    age_0_20_counts = []
    age_20_40_counts = []
    age_40_60_counts = []
    age_60_above_counts = []

    # time_range_key_list 목록에서 각 연령대 값 추가
    for time_range in time_range_key_list:
        age_0_20_counts.append(time_range_dict[time_range]["age"]["age_0_20"])
        age_20_40_counts.append(time_range_dict[time_range]["age"]["age_20_40"])
        age_40_60_counts.append(time_range_dict[time_range]["age"]["age_40_60"])
        age_60_above_counts.append(time_range_dict[time_range]["age"]["age_60_above"])

    # zip을 통해 각 연령대와 time_range_key_list 묶기
    age_0_20_zipped_data = zip(age_0_20_counts, time_range_key_list)
    age_20_40_zipped_data = zip(age_20_40_counts, time_range_key_list)
    age_40_60_zipped_data = zip(age_40_60_counts, time_range_key_list)
    age_60_above_zipped_data = zip(age_60_above_counts, time_range_key_list)

    # 각 연령대에 대해 bar_chart_image_save 호출
    target = "age"
    # display_name, display_id, year, month, zipped_data, target, target_title
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_0_20_zipped_data,
        target,
        f"{interval_text}_age_0_20",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_20_40_zipped_data,
        target,
        f"{interval_text}_age_20_40",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_40_60_zipped_data,
        target,
        f"{interval_text}_age_40_60",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_60_above_zipped_data,
        target,
        f"{interval_text}_age_60_above",
    )


def zip_for_age_gender(
    display_name, display_id, year, month, time_range_dict, interval_text
):
    time_range_key_list = time_range_dict.keys()
    # 연령대-성별별 리스트 초기화
    age_0_20_male_counts = []
    age_0_20_female_counts = []
    age_20_40_male_counts = []
    age_20_40_female_counts = []
    age_40_60_male_counts = []
    age_40_60_female_counts = []
    age_60_above_male_counts = []
    age_60_above_female_counts = []

    # time_range_key_list 목록에서 각 연령대-성별 값 추가
    for time_range in time_range_key_list:
        age_0_20_male_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_0_20_Male"]
        )
        age_0_20_female_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_0_20_Female"]
        )
        age_20_40_male_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_20_40_Male"]
        )
        age_20_40_female_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_20_40_Female"]
        )
        age_40_60_male_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_40_60_Male"]
        )
        age_40_60_female_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_40_60_Female"]
        )
        age_60_above_male_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_60_above_Male"]
        )
        age_60_above_female_counts.append(
            time_range_dict[time_range]["age_and_gender"]["age_60_above_Female"]
        )

    # zip을 통해 각 연령대-성별 데이터와 time_range_key_list 묶기
    age_0_20_male_zipped = zip(age_0_20_male_counts, time_range_key_list)
    age_0_20_female_zipped = zip(age_0_20_female_counts, time_range_key_list)
    age_20_40_male_zipped = zip(age_20_40_male_counts, time_range_key_list)
    age_20_40_female_zipped = zip(age_20_40_female_counts, time_range_key_list)
    age_40_60_male_zipped = zip(age_40_60_male_counts, time_range_key_list)
    age_40_60_female_zipped = zip(age_40_60_female_counts, time_range_key_list)
    age_60_above_male_zipped = zip(age_60_above_male_counts, time_range_key_list)
    age_60_above_female_zipped = zip(age_60_above_female_counts, time_range_key_list)

    # 각 연령대-성별 조합에 대해 bar_chart_image_save 호출
    target = "age_and_gender"
    # display_name, display_id, year, month, zipped_data, target, target_title
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_0_20_male_zipped,
        target,
        f"{interval_text}_age_0_20_Male",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_0_20_female_zipped,
        target,
        f"{interval_text}_age_0_20_Female",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_20_40_male_zipped,
        target,
        f"{interval_text}_age_20_40_Male",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_20_40_female_zipped,
        target,
        f"{interval_text}_age_20_40_Female",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_40_60_male_zipped,
        target,
        f"{interval_text}_age_40_60_Male",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_40_60_female_zipped,
        target,
        f"{interval_text}_age_40_60_Female",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_60_above_male_zipped,
        target,
        f"{interval_text}_age_60_above_Male",
    )
    bar_chart_image_save(
        display_name,
        display_id,
        year,
        month,
        age_60_above_female_zipped,
        target,
        f"{interval_text}_age_60_above_Female",
    )
