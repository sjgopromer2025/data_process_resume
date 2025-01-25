from data_class.display_data import DisplayInfo


def generate_error_message(display_info: DisplayInfo, road_name: str = None) -> str:
    """
    에러 메시지를 동적으로 생성하는 함수.

    Args:
        display_info (DisplayInfo): 디스플레이 정보 객체
        road_name (str, optional): 도로명

    Returns:
        str: 생성된 에러 메시지
    """
    message = f"{display_info.display_name}의 {display_info.display_id} 매체"
    if display_info.year:
        message += f" {display_info.year}년"
    if display_info.month:
        message += f" {display_info.month}월"
    if display_info.day:
        message += f" {display_info.day}일"
    if road_name:
        message += f" {road_name}"
    message += " 데이터가 없습니다."
    return message


def json_file_check(json_file_path, display_info: DisplayInfo):
    if not json_file_path:
        error_message = generate_error_message(display_info)
        raise ValueError(error_message)


def json_data_check(json_data, display_info: DisplayInfo):
    if not json_data:
        error_message = generate_error_message(display_info)
        raise ValueError(error_message)


def csv_list_check(csv_files: list, display_info: DisplayInfo):
    if len(csv_files) == 0:
        error_message = generate_error_message(display_info)
        raise ValueError(error_message)


def road_file_check(json_file_path, display_info: DisplayInfo, road_name: str = None):
    if not json_file_path:
        error_message = generate_error_message(display_info, road_name)
        raise ValueError(error_message)
