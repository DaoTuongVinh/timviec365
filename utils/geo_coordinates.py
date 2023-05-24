"""_summary_
    File này mục đích xử lý liên quan đến tọa độ 
"""
from geopy.geocoders import Nominatim


# Khởi tạo vùng miền bắc trung nam
regions = {
    'north': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25'],
    'centeral': ['26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36',
                '37', '38', '39', '40', '41', '42', '43', '44'],
    'south': ['45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55',
            '56', '57', '58', '59', '60', '61', '62', '63']
}

tinhthanh = {
    "1": "Hà Nội",
    "2": "Hải Phòng",
    "3": "Bắc Giang",
    "4": "Bắc Kạn",
    "5": "Bắc Ninh",
    "6": "Cao Bằng",
    "7": "Điện Biên",
    "8": "Hòa Bình",
    "9": "Hải Dương",
    "10": "Hà Giang",
    "11": "Hà Nam",
    "12": "Hưng Yên",
    "13": "Lào Cai",
    "14": "Lai Châu",
    "15": "Lạng Sơn",
    "16": "Ninh Bình",
    "17": "Nam Định",
    "18": "Phú Thọ",
    "19": "Quảng Ninh",
    "20": "Sơn La",
    "21": "Thái Bình",
    "22": "Thái Nguyên",
    "23": "Tuyên Quang",
    "24": "Vĩnh Phúc",
    "25": "Yên Bái",
    "26": "Đà Nẵng",
    "27": "Thừa Thiên Huế",
    "28": "Khánh Hòa",
    "29": "Lâm Đồng",
    "30": "Bình Định",
    "31": "Bình Thuận",
    "32": "Đắk Lắk",
    "33": "Đắk Nông",
    "34": "Gia Lai",
    "35": "Hà Tĩnh",
    "36": "Kon Tum",
    "37": "Nghệ An",
    "38": "Ninh Thuận",
    "39": "Phú Yên",
    "40": "Quảng Bình",
    "41": "Quảng Nam",
    "42": "Quảng Ngãi",
    "43": "Quảng Trị",
    "44": "Thanh Hóa",
    "45": "Hồ Chí Minh",
    "46": "Bình Dương",
    "47": "Bà Rịa Vũng Tàu",
    "48": "Cần Thơ",
    "49": "An Giang",
    "50": "Bạc Liêu",
    "51": "Bình Phước",
    "52": "Bến Tre",
    "53": "Cà Mau",
    "54": "Đồng Tháp",
    "55": "Đồng Nai",
    "56": "Hậu Giang",
    "57": "Kiên Giang",
    "58": "Long An",
    "59": "Sóc Trăng",
    "60": "Tiền Giang",
    "61": "Tây Ninh",
    "62": "Trà Vinh",
    "63": "Vĩnh Long"
}


def check_region(city_id: str):
    """_summary_
        Kiểm tra xem tỉnh thành đó thuộc vùng miền nào
    Args:
        city_id (str): Id của tỉnh thành cần kiểm tra
    """
    for name_region, city_region in regions.items():
        if city_id in city_region:
            return name_region
    return ''


def get_location(latitude: float, longitude: float):
    """_summary_
        Trả về tỉnh thành phố dựa vào kinh độ và vĩ độ
    Args:
        latitude (float): kinh độ
        longitude (float): vĩ độ
    """
    geolocator = Nominatim(user_agent="geoapiExcercises")
    location = str(geolocator.reverse(str(latitude) + ", " + str(longitude)))
    location = location.lower()
    list_id_tinhthanh, list_name_tinhthanh = list(tinhthanh.keys()), list(tinhthanh.values())
    
    for index, name_tinhthanh in enumerate(list_name_tinhthanh):
        name_tinhthanh = name_tinhthanh.lower()
        if name_tinhthanh in location:
            return list_id_tinhthanh[index]
    return '0'