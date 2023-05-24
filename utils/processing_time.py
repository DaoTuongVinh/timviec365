from datetime import datetime

# Chuyển dữ liệu từ int sang ngày - tháng - năm
def int2date(value: int):
    """_summary_
        Chuyển đổi giá trị dạng value thành dạng string là:  năm - tháng - ngày giờ:phút:giây
    Args:
        value (int): giá trị ở kiểu int đang muốn đưa về kiểu dạng ngày/tháng/năm
        return : Year - Month - Day Hour:Minute:Second 
    """
    timestamp = datetime.datetime.fromtimestamp(value)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def updatetime(value):
    """
        Chọn thời gian để tìm kiếm bản tin
    """
    # Kiểm tra xem value được nhập là int or str
    if isinstance(value, str):
        value = int(value)
    
    if value == 0: # Tìm kiếm tin 1 ngày trở lại đây
        return int(round(datetime.now().timestamp())) - 86400
    elif value == 1: # Tìm kiếm tin 1 tuần trở lại đây
        return int(round(datetime.now().timestamp())) - 604800
    elif value == 2: # Tìm kiếm tin 1 tháng đổ lại
        return int(round(datetime.now().timestamp())) - 2592000
    else:
        return 0
        

# Chỉ lấy các tin có thời gian hạn nộp là khoảng từ các mốc thời gian đổ lại
def time_nop_minmax(value):
    time_now = int(round(datetime.now().timestamp()))
    if value == 1: # 1 năm đổ lại
        time_nop_max = time_now + 31536000
    elif value == 2: #  6 tháng đổ lại
        time_nop_max = time_now + 15552000
    elif value == 3: # 3 tháng đổ lại
        time_nop_max = time_now + 7776000
    return time_nop_max


def get_int_year(value):
    # year_old = year_now - value
    return value * 31536000


def is_leap_year(year):
    """Xác định năm đó là năm nhuận hay không nhuận"""

    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
