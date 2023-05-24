import requests
import datetime
import os
import traceback
import json

"""_summary_
    Cách thức hoạt động của tìm kiếm mức lương theo mong muốn:
    Trường hợp 1: Thỏa thuận
    Trường hợp 2: trong khoảng tương ứng nm_type = 5
    - nm_max_value > min của trong khoảng (ví dụ 3 - 5 thì min là 3 ) và nm_min_value < max của trong khoảng (ví dụ 3 - 5 thì max là 5 )
    Trường hợp 3: từ mức
    - nm_max_value > từ mức (giá trị nhỏ nhất của từ mức)
    - cộng thêm id trong khoảng
    Trường hợp 4: Đến mức
    - nm_min_value <= đến mức (giá trị lớn nhất của đến mức)
    - Cộng thêm id trong khoảng
    Trường hợp 5: Từ mức - đến mức
    - nm_max_value > min của trong khoảng (ví dụ 3 - 5 thì min là 3) và nm_min_value < max của trong khoảng (ví dụ 3 - 5 thì max là 5 )
    - Cộng thêm id trong khoảng
Returns:
    _type_: _description_
"""


# money vnd tr
lg_money_type = {
    '2': [1000000, 3000000], # 1 triệu đến 3 triệu
    '3': [3000000, 5000000], # 3 triệu đến 5 triệu
    '4': [5000000, 7000000], # 5 triệu đến 7 triệu
    '5': [7000000, 10000000], # 7 triệu đến 10 triệu
    '6': [10000000, 15000000], # 10 triệu đến 15 triệu
    '7': [15000000, 20000000], # 15 triệu đến 20 triệu
    '8': [20000000, 30000000], # 20 triệu đến 30 triệu
    '9': [30000000, 50000000], # 30 triệu đến 50 triệu
    '10': [50000000, 100000000], # 50 triệu đến 100 triệu
    '11': [100000000, 10000000000000] # Trên 100 triệu
}

# Lấy tỷ lệ tiền tệ trên các sàn chứng khoán thế giới
class RealTimeCurrencyRates:
    
    
    def __init__(self, link_url):
        # link_url: Đường dẫn link API
        # from_currency: Tỷ giá cần đổi
        # Lấy các đường link API trả ra kết quả tiền tệ giữa các nước
        # https://api.exchangerate-api.com/v4/latest/
        self.link_url = link_url + 'VND'
        try:
            # Kiểm tra xem đã có file json lưu lại bảng giá chưa ?
            if os.path.exists('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json'):
                data_json = {}
                with open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'r') as file:
                    data_json = json.load(file)
                
                list_date_currencyRates, list_date_rate_currencyRates = list(data_json.keys()), list(data_json.values())
                now = str(datetime.date.today())
                if now in list_date_currencyRates:
                    self.data = list_date_rate_currencyRates[-1]
                    self.rates = self.data['rates']
                else:
                    self.data = requests.get(self.link_url).json()
                    self.rates = self.data['rates'] # Lấy tỷ giá VND so với các đồng tiền khác
                    self.update_currencyRates()
            else:
                file = open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'w')
                self.data = requests.get(self.link_url).json()
                self.rates = self.data['rates'] # Lấy tỷ giá VND so với các đồng tiền khác
                date = self.data['date']
                data_json = {}
                data_json[date] = self.data
                if self.data is not None and self.rates is not None:
                    json.dump(data_json, file)
                    file.write('\n')
                # Đóng lại file
                    file.close()
                
        except Exception as err:
            self.data = None
            self.rates = None
            print(traceback.print_exc())
        
        
    def convert_to_VND(self, amount, from_unit_currency):
        """_summary_
            Chuyển đổi từ tiền khác sang VND
        Args:
            amount_base_currency (_type_): Số tiền của đơn vị tiền tệ gốc
            target_currency (_type_): Đơn vị tiền tệ cần chuyển đổi
        
        Return (giá trị trả về): Tiền lúc sau khi đổi đơn vị tiền tệ
        """
        if self.data is not None and self.rates is not None:
            amount_target = float(amount) * (1 / self.rates[from_unit_currency]) 
            return int(amount_target)
        elif os.path.exists('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json'):
            file = open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'r')
            data_currencyRates = json.load(file)
            data_date_currencyRates, data_rates_currencyRates = list(data_currencyRates.keys()), list(data_currencyRates.values()) 
            if len(list(data_currencyRates.keys())):
                data_rates_currencyRates_last = data_rates_currencyRates[-1]
                amount_target = float(amount) * (1 / data_rates_currencyRates_last['rates'][from_unit_currency]) 
                return int(amount_target)
            else:
                raise Exception('Chưa có thông tin về tỷ giá tiền tệ trong file.')
        else:
            raise Exception('Không tồn tại file chứa tỷ giá tiền tệ')
        
    
    def convert_to_unit(self, amount_VND, to_unit_currency):
        """
            Chuyển đổi từ VND sang tiền khác
        """    
        if self.data is not None and self.rates is not None:
            amount_target = float(amount_VND) * self.rates[to_unit_currency] 
            return int(amount_target)
        elif os.path.exists('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json'):
            file = open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'r')
            data_currencyRates = json.load(file)
            data_date_currencyRates, data_rates_currencyRates = list(data_currencyRates.keys()), list(data_currencyRates.values()) 
            if len(list(data_currencyRates.keys())):
                data_rates_currencyRates_last = data_rates_currencyRates[-1]
                amount_target = float(amount_VND) * data_rates_currencyRates_last['rates'][to_unit_currency] 
                return int(amount_target)
            else:
                raise Exception('Chưa có thông tin về tỷ giá tiền tệ trong file.')
        else:
            raise Exception('Không tồn tại file chứa tỷ giá tiền tệ')
        
    def update_currencyRates(self):
        # Đọc dữ liệu dạng tỷ giá json
        data_json = {}
        with open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'r') as file:
            data_json = json.load(file)
        
        # Chỉ lấy số lượng date khoảng 1 tuần đổ lại
        dates = list(data_json.keys())
        rates = list(data_json.values())
        
        if len(dates) >= 7:
            data_json.pop(dates[0])
        
        with open('/home/hungha/timviec_elasticsearch/utils/' + 'currencyRates.json', 'w') as file:
            date = self.data['date']
            data_json[date] = self.data
            if self.data is not None and self.rates is not None:
                json.dump(data_json, file)
            
            file.write('\n')


# Chuyển đổi tiền các nước trên thế giới về tiền việt nam để phục vụ tìm kiếm, gợi ý
def convertVND(from_value_money, from_money_unit):
    # money_vnd: Tiền việt
    # Chuyển đổi qua các loại tiền khác
    link_url = 'https://api.exchangerate-api.com/v4/latest/'
    c = RealTimeCurrencyRates(link_url)
    return c.convert_to_VND(from_value_money, from_money_unit)


# Chuyển đổi tiền việt nam sang tiền các nước trên thế giới để phục vụ tìm kiếm, gợi ý
def convertunit(from_value_money, to_money_unit):
    # money_vnd: Tiền việt
    # Chuyển đổi qua các loại tiền khác
    link_url = 'https://api.exchangerate-api.com/v4/latest/'
    c = RealTimeCurrencyRates(link_url)
    return c.convert_to_unit(from_value_money, to_money_unit)


# Chuyển đổi mức lương từ đến thành các id lg_money_type phục vụ cho tìm kiếm
def convert_money_type(kg_money: list):
    """_summary_
        Chuyển đổi mức lương từ mức, đến mức, từ mức - đến mức -> Sang dạng mức lương trong khoảng
    Args:
        kg_money (list): List money kiểu dạng từ mức, đến mức, từ mức - đến mức
        type (int): Cho biết từ mức (2), đến mức (3), từ mức - đến mức (4)
        
        Ở đây ta có thể coi đến mức, từ mức - đến mức đều thuộc trong khoảng [a, b]
        + Đến mức: [0, đến mức]
        + Từ mức - đến mức: [từ mức, đến mức]
    """
    
    # Kiểm tra xem dữ liệu đầu vào là kiểu gì ?
    
    list_id_money_type = []
    kg_money = [int(float(value)) for value in kg_money] # Chuyển hết về kiểu dữ liệu là int
    key_lg_money_type, value_lg_money_type = list(lg_money_type.keys()), list(lg_money_type.values())
    if len(kg_money) == 1: # Xử lý xong phần từ mức -> vô hạn tiền
        for i in range(len(value_lg_money_type)):
            if kg_money[0] < max(value_lg_money_type[i]):
                list_id_money_type.append(key_lg_money_type[i])
    elif len(kg_money) == 2:
        if kg_money in value_lg_money_type: # Trong trường hợp có trong các trường trong khoảng thì chỉ trả ra 1 kết quả
            list_id_money_type = [key_lg_money_type[value_lg_money_type.index(kg_money)]]
        else:
            # Dùng 2 vòng for 
            # Vòng for đầu tiên thì sẽ thêm vào list
            for i in range(len(value_lg_money_type)):
                if kg_money[0] < max(value_lg_money_type[i]) and kg_money[1] >= min(value_lg_money_type[i]):
                    list_id_money_type.append(key_lg_money_type[i])
    else:
        raise Exception('Chỉ nhận giá trị là dạng list có 1 phần tử hoặc 2 phần tử')
    
    return list_id_money_type


def preprocessing_money_v2(id_money_kg, money_type, money_unit, money_min, money_max):
    """_summary_
        Tiền xử lý giá tiền được nhập vào
        Giá tiền nhập vào gồm các loại như sau:
        + Thỏa thuận 
        + Từ mức
        + Đến mức
        + Từ mức - đến mức
        + Trong khoảng
    Args:
        id_money_kg (_type_): _description_
        money_type (_type_): _description_
        money_unit (_type_): _description_
        money_min (_type_): _description_
        money_max (_type_): _description_
    """
    results = {
        'id_kg_luong': [],
        'min_money': {},
        'max_money': {}
    }
    string_money_unit = 'VND'
    
    # Kiểm tra đơn vị tiền tệ thuộc loại nào
    if money_unit == '1':
        string_money_unit = 'VND'
    elif money_unit == '2':
        string_money_unit = 'USD'
    elif money_unit == '3':
        string_money_unit = 'EUR'

    # Kiểm tra xem có cv_money_id có nằm trong khoảng lương đã được cho trước không
    if id_money_kg not in list(lg_money_type.keys()):
        results['id_kg_luong'] = ['', '0', '1']
        return results

    # Xét các khoảng mức lương
    if money_type == '1' or money_type == '0' or money_type == '' or money_type is None:
        results['id_kg_luong'] = ['', '0', '1']
        return results # Trả ra đúng Id là thỏa thuận
    elif money_type == '2': # Từ mức
        money_min_vnd = int(convertVND(int(float(money_min)), string_money_unit))
        money_min_usd = convertunit(money_min_vnd, 'USD')
        money_min_eur = convertunit(money_min_vnd, 'EUR')
        list_id_kg = convert_money_type(kg_money=[money_min_vnd]) # Danh sách khoảng lương.
        results['min_money']['1'] = money_min_vnd
        results['min_money']['2'] = money_min_usd
        results['min_money']['3'] = money_min_eur
        results['id_kg_luong'] = list_id_kg
        return results
    elif money_type == '3':
        money_max_vnd = int(convertVND(int(float(money_max)), string_money_unit))
        money_max_usd = convertunit(money_max_vnd, 'USD')
        money_max_eur = convertunit(money_max_vnd, 'EUR')
        results['max_money']['1'] = money_max_vnd
        results['max_money']['2'] = money_max_usd
        results['max_money']['3'] = money_max_eur
        list_id_kg = convert_money_type(kg_money=['0', money_max_vnd])
        results['id_kg_luong'] = list_id_kg
        return results
    elif money_type == '4': # Từ mức - đến mức
        money_min_vnd = int(convertVND(int(float(money_min)), string_money_unit))
        money_max_vnd = int(convertVND(int(float(money_max)), string_money_unit))
        money_min_usd, money_max_usd = convertunit(money_min_vnd, 'USD'), convertunit(money_max_vnd, 'USD')
        money_min_eur, money_max_eur = convertunit(money_min_vnd, 'EUR'), convertunit(money_max_vnd, 'EUR')
        list_id_kg = convert_money_type(kg_money=[money_min_vnd, money_max_vnd])
        results['id_kg_luong'] = list_id_kg
        results['min_money']['1'] = money_min_vnd
        results['max_money']['1'] = money_max_vnd
        results['min_money']['2'] = money_min_usd
        results['max_money']['2'] = money_max_usd
        results['min_money']['3'] = money_min_eur
        results['max_money']['3'] = money_max_eur
        return results
    else:
        print(id_money_kg)
        if id_money_kg == '1':
            results['id_kg_luong'] = ['', '0', '1']
            return results
        else:
            money_kg = lg_money_type[id_money_kg]
            money_min_vnd, money_max_vnd = money_kg[0], money_kg[1]
            money_min_usd, money_max_usd = convertunit(money_min_vnd, 'USD'), convertunit(money_max_vnd, 'USD')
            money_min_eur, money_max_eur = convertunit(money_min_vnd, 'EUR'), convertunit(money_max_vnd, 'EUR')
            results['id_kg_luong'] = [id_money_kg]
            results['min_money']['1'] = money_min_vnd
            results['max_money']['1'] = money_max_vnd
            results['min_money']['2'] = money_min_usd
            results['max_money']['2'] = money_max_usd
            results['min_money']['3'] = money_min_eur
            results['max_money']['3'] = money_max_eur
            return results