import matplotlib.pyplot as plt
from utils.datetime_util import get_month_name
from utils.env_path_util import report_path
import os
from utils.csv_features_util import target_list


def count_chart_valued_sort(
    json_data, display_id, target, year, display_name, target_title
):
    months = list(json_data[display_id].keys())

    for month in months:
        # 필요한 데이터 추출
        counts = []
        dates = []

        # 타겟이 age 일 경우
        if target == target_list[2] or target == target_list[3]:
            age_list = list(json_data[display_id][month].keys())
            for age in age_list:
                for age_data in json_data[display_id][month][age].values():
                    counts.append(age_data["count"])
                    dates.append(age_data["date"])

                zipped_data = zip(counts, dates)
                bar_chart_image_save(
                    zipped_data, display_id, target, month, year, display_name, age
                )
                counts.clear()
                dates.clear()
        # 그 외 gender, month 일 경우
        else:
            for date_data in json_data[display_id][month].values():
                counts.append(date_data["count"])
                dates.append(date_data["date"])
            zipped_data = zip(counts, dates)
            bar_chart_image_save(
                zipped_data, display_id, target, month, year, display_name, target_title
            )


def bar_chart_image_save(
    zipped_data, display_id, target, month, year, display_name, target_title
):
    # y값을 기준으로 내림차순 정렬
    sorted_data = sorted(zipped_data, reverse=True, key=lambda x: x[0])
    sorted_counts, sorted_dates = zip(*sorted_data)

    # 바 차트 생성
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_dates, sorted_counts, color="skyblue")

    # 축 레이블 설정
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.title(
        f"{display_id} Display {target_title} {get_month_name(month)} Count per Date (Sorted)"
    )
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_name = f"{display_id}_{year}_{month}_{target_title}_count_per_date_chart.png"
    # 이미지 파일로 저장
    image_save_path = os.path.join(
        report_path, display_name, "count", display_id, year, month, target
    )
    os.makedirs(image_save_path, exist_ok=True)

    plt.savefig(os.path.join(image_save_path, image_name), dpi=300, bbox_inches="tight")
    plt.close()
