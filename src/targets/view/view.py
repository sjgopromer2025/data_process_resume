# exposed_time 노출 시간
# watched_time 시청 시간
# attention_time 주목 시간
from utils.env_path_util import attention_time
from utils.env_path_util import exposed_time
from utils.env_path_util import watched_time


def csv_attention(display_id, csv_data, csv_view_dict):
    count = (csv_data["attention_time"] > attention_time).sum()

    csv_view_dict[display_id]["attention"] += int(count)


def csv_exposed(display_id, csv_data, csv_view_dict):
    count = (csv_data["exposed_time"] > exposed_time).sum()

    csv_view_dict[display_id]["exposed"] += int(count)


def csv_watched(display_id, csv_data, csv_view_dict):
    count = (csv_data["watched_time"] > watched_time).sum()

    csv_view_dict[display_id]["watched"] += int(count)
