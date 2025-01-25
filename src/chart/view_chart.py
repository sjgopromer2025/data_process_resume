import matplotlib.pyplot as plt
from utils.datetime_util import get_month_name
from utils.env_path_util import report_path
import os
from utils.csv_features_util import target_list


def view_chart_valued_sort(csv_day_dict, year, display_name, month):
    display_ids = list(csv_day_dict.keys())
    # exposed, watched, attention
    exposed_list = []
    watched_list = []
    attention_list = []

    for display_id in display_ids:
        exposed_list.append(csv_day_dict[display_id]["exposed"])
        watched_list.append(csv_day_dict[display_id]["watched"])
        attention_list.append(csv_day_dict[display_id]["attention"])

    zipped_exposed_data = zip(exposed_list, display_ids)
    zipped_watched_data = zip(watched_list, display_ids)
    zipped_attention_data = zip(attention_list, display_ids)
    bar_chart_image_save(
        zipped_exposed_data, month, year, display_name, "exposed_count"
    )
    bar_chart_image_save(
        zipped_watched_data, month, year, display_name, "watched_count"
    )
    bar_chart_image_save(
        zipped_attention_data, month, year, display_name, "attention_count"
    )


def bar_chart_image_save(zipped_data, month, year, display_name, target_title):
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

    image_name = f"{display_name}_{year}_{month}_{target_title}_chart.png"
    # 이미지 파일로 저장
    image_save_path = os.path.join(report_path, display_name, "view_time", year, month)
    os.makedirs(image_save_path, exist_ok=True)

    plt.savefig(os.path.join(image_save_path, image_name), dpi=300, bbox_inches="tight")
    plt.close()
