import os
from data_class.display_data import DisplayInfo
from utils.env_path_util import src_path


def get_road_file(display_info: DisplayInfo):
    # 매체 정보
    display_name = display_info.display_name
    display_id = display_info.display_id
    year = display_info.year
    month = display_info.month
    day = display_info.day

    # road 파일 검사 후 리스트 리턴
    # 최초 루트 경로
    root_path = os.path.join(
        src_path, "roads", display_name, display_id, year, month, day, "coordinate"
    )

    if os.path.exists(root_path):
        road_files = os.listdir(root_path)

        return [os.path.join(root_path, road_file) for road_file in road_files]
    else:
        return []


def get_total_road_file():
    # road 파일 검사 후 리스트 리턴
    # 최초 루트 경로
    root_path = os.path.join(src_path, "roads", "total_coordinate")

    if os.path.exists(root_path):
        road_files = os.listdir(root_path)

        return [os.path.join(root_path, road_file) for road_file in road_files]
    else:
        return []
