import traceback
import os
import json
import requests
from time import time
from datetime import datetime

# Management data by elasticsearch
from DataManager.server import DATABASE
from DataManager.jobseek import Jobseek

# Connection port
from flask import Flask, request
from utils.vietnamese_normalizer import clean_text, clean_keyword, search_stopword_arcnoyms, preprocessing
from utils.processing_time import updatetime, time_nop_minmax
from utils.processing_money import preprocessing_money_v2
from utils.search import SEARCH_JOBSEEK

# Xuất logging 
from model_api import *

# API sử dụng Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "secret key"

# Mở cổng elasticsearch
_SERVER_ = DATABASE()

# Lấy ra danh sách từ khóa viết tắt 
file_stopword = 'C:/Users/Vinh/Downloads/timviec365_elasticsearch-main/Mapping_keyword/search_stopword.txt'
file_acronyms = 'C:/Users/Vinh/Downloads/timviec365_elasticsearch-main/Mapping_keyword/acronyms.txt'
search_stopword, search_acronyms = search_stopword_arcnoyms(file_stopword, file_acronyms)


# Danh sách lấy key-value (tỉnh thành, quận huyện, mức lương, v.v.v) của site timviec365, vieclam24h, vieclam123 
information_search = {}
folder = 'C:/Users/Vinh/Downloads/timviec365_elasticsearch-main/Mapping_search'
try:
    for file_mapping in os.listdir(folder):
        filename = file_mapping.split('.')[0].split('_')[-1]
        abs_file_mapping = os.path.join(folder, file_mapping)
        information_search_site = {}
        with open(abs_file_mapping, encoding='utf-8') as f:
            info = json.load(f)
            for key, value in info.items():
                information_search_site[key] = value
        information_search[filename] = information_search_site
        f.close()
except FileNotFoundError:
    print('Please check the path job')


# Nhận diện tag ngành nghề dựa trên tiêu đề của nhà tuyển dụng
@app.route("/recognition_tag_tin", methods=["POST", "GET"])
def recognition_tag_tin():
    # Lấy tag ngành nghề
    data_body = dict(request.form)
    error = None
    data = None
    message = 'Không nhận diện được tag tin'
    remove_text_tags = ['nhân viên'] 
    try:
        cat_id = data_body.get('key_cat_lq')
        title = data_body.get('new_title')
        mota = data_body.get('new_mota')
        yeucau = data_body.get('new_yeucau')
        item = []
        name_tag = ''
        list_tag = [] # Danh sách tag ngành nghề
        list_full_tag = []
        list_item = [] # Danh sách id ngành nghề
        
        # Xử lý cat_id 
        if cat_id is None:
            message = 'Bạn chưa truyền trường ngành nghề'
            raise Exception
        
        if cat_id == '':
            message = 'Bạn truyền trường ngành nghề không đúng kiểu int'
            raise Exception
            
        # Xử lý new_title
        if title is None:
            message = 'Bạn chưa truyền trường tiêu đề'
            raise Exception
        
        if mota is None:
            mota = ''
        
        if yeucau is None:
            yeucau = ''
        
        list_cat_id = cat_id.split(',')
            
        
        # Làm sạch text ở trong tiêu đề, mô tả, yêu cầu của tin việc làm
        title = clean_text(title.lower())
        mota = clean_text(mota.lower())
        yeucau = clean_text(yeucau.lower())
    
        # Lưu danh sách tag đã được tinh chỉnh
        results_id = []
        results_name = []
        
        for cat_id in list_cat_id:
            api_get_tag = f"https://timviec365.vn/api_ai/get_tag.php?data={cat_id}"
            data = requests.get(api_get_tag).json() # Lấy data dạng list
            list_tag, list_item, list_full_tag = [], [], []
            for dt in data:
                key_name = dt['key_name'].lower()
                list_full_tag.append(key_name)
                for remove_tag in remove_text_tags:
                    if remove_tag in key_name:
                        key_name = key_name.replace(remove_tag, '')
                key_name = ' '.join(key_name.split())
                list_tag.append(key_name)
                list_item.append(dt['key_id'])
            
            # Kiểm tra theo thứ tự lần lượt : title, mô tả, yêu cầu đối với mỗi tag
            list_position_cat = [i for i, tag in enumerate(list_tag) if tag in title]
            if len(list_position_cat) == 0: # Kiểm tra xem trong mô tả có không
                list_position_cat = [i for i, tag in enumerate(list_tag) if tag in mota]
            if len(list_position_cat) == 0: # Kiểm tra xem trong yêu cầu có không
                list_position_cat = [i for i, tag in enumerate(list_tag) if tag in yeucau]
            if len(list_position_cat) != 0:
                list_results_item = [list_item[position] for position in list_position_cat]
                list_results_tag = [list_tag[position] for position in list_position_cat]
                # Lấy ra chuỗi có độ dài lớn nhất
                index_name_tag = max(enumerate(list_results_tag), key=lambda x: len(x[1]))[0]
                id = list_results_item[index_name_tag]
                results_id.append(id)
                results_name.append(list_full_tag[list_item.index(id)])
                
        
        if len(results_id) == 0:
            message = 'Không tồn tại id tag ngành nghề trong tiêu đề, mô tả, yêu cầu của việc làm.'
            items = []
            name_tag = ''
        else:
            message = 'Nhận diện thành công.'  
            items = []
            for position in range(len(results_id)):
                item = {
                    'id_tag': results_id[position],
                    'name_tag': results_name[position]
                }
                items.append(item)
            name_tag = ','.join(results_name)
            print(items)
        data = RecognitionModel(True, message, items, name_tag)
        error = None
    except Exception as err:
        print(traceback.print_exc())
        data = None
        error = ErrorModel(200, message)
    
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    response = ResponseModel(data, error)
    return json.loads(json.dumps(vars(response), ensure_ascii=False))


# Nhận diện tag lĩnh vực công ty dựa trên tên công ty mà nhà tuyển dụng đã nhập
@app.route('/recognition_tag_company', methods=["POST", "GET"])
def recognition_tag_company():
    # Lấy tag ngành nghề
    data_body = dict(request.form)
    error = None
    data = None
    message = 'Không nhận diện được tag trong tên công ty'
    item = '0'
    remove_text_tags = ['chuyên viên', 'nhân viên'] 
    try:
        results = []
        list_id = []
        title_company = data_body.get('title_company') # Tiêu đề tên của công ty + lĩnh vực của công ty đó
        description_company = data_body.get('description_company') # Giới thiệu và mô tả về công ty đó
        number_tag = data_body.get('number') # Giới hạn số lượng tin cần phải lấy
        
        # Kiểm tra trường tên công ty
        if title_company is None:
            message = 'Bạn chưa truyền trường tên và lĩnh vực hoạt động của công ty'
            raise Exception
        
        # Kiểm tra mô tả chi tiết tên công ty
        if description_company is None:
            message = 'Bạn chưa truyền trường mô tả tên của công ty'
            raise Exception
        
        # Kiểm tra trường số lượng tag trả về và kiểm tra xem số lượng tag đó là int hay string hay float
        if number_tag is None or number_tag == '0':
            number_tag = '1' # Mặc định lấy tag đầu tiên
        if not number_tag.isdigit():
            number_tag = '1' # Mặc định lấy tag đầu tiên
            
        print(number_tag)
        # Làm sạch text (tiêu đề tên, mô tả của công ty)
        title_company = clean_text(title_company)
        description_company = clean_text(description_company)
        number_tag = int(number_tag)
        api_get_linhvuc = f'https://timviec365.vn/api_app/list_linh_vuc.php'
        data = requests.get(api_get_linhvuc).json() # Lấy data dạng list
        data = data['data']['data']
        
        for tag in data:
            # Kiểm tra tag xem có trong tiêu đề tên của công ty hay không ? 
            name_tag = tag['name_tag']
            id_tag = tag['id']
            if name_tag.lower() in title_company.lower():
                results.append(
                    {
                        'id_tag': id_tag,
                        'name_tag': name_tag 
                    }
                )
                list_id.append(id_tag)
                
        
        # Trong trường hợp không tìm thấy tên của công ty => Tìm kiếm tag ở trong phần mô tả của công ty đó
        if len(results) == 0:
            for tag in data:
                name_tag = tag['name_tag']
                id_tag = tag['id']
                if name_tag.lower() in description_company.lower():
                    results.append(
                        {
                            'id_tag': id_tag,
                            'name_tag': name_tag 
                        }
                    )
                    list_id.append(name_tag)
                    
        # Nếu number_tag > số lượng tag đang có trong cả tiêu đề, mô tả => max là số lượng tag
        # Nếu number_tag <= số lượng tag đang có trong cả tiêu đề, mô tả => max là number_tag
        
        if number_tag <= len(list_id):
            list_id = list_id[:number_tag]
            results = results[:number_tag]
        
        # Gửi kết quả cho bên nhận gồm message + item
        if len(results):
            message = 'Nhận diện thành công'
            list_id = ",".join(list_id)   
        else:
            message = 'Không tìm thấy lĩnh vực hoạt động của công ty ở cả trong tên và mô tả của công ty'
            list_id = ''
            results = [] 
        
        data = RecognitionModel(True, message, results, list_id)
        error = None
    except Exception as err:
        print(traceback.print_exc())
        data = None
        error = ErrorModel(200, message)
    
    # Trả ra kết quả cho bên web xử lý
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    response = ResponseModel(data, error)
    return json.loads(json.dumps(vars(response), ensure_ascii=False))


# Thêm mới bản tin vào trong elasticsearch
@app.route("/new_tin", methods=["POST"])
def new_tin():
    # Lấy toàn bộ thông tin từ trường form-data
    data_body = dict(request.form)
    print(data_body)
    # Index được sử dụng mặc định là tin tuyển dụng
    site = data_body.get('site')
    index = None
    error = None
    data = None
    message = "Không tạo được tin tuyển dụng"
    try:
        
        # Kiểm tra xem đã nhập site tin tuyển dụng chưa
        if site is None:
            message = "Chưa nhập site để chỉnh sửa tin tuyển dụng"
            raise ErrorSite
        else:
            index = 'tin_' + site
        
        data_body.pop('site')
        
        # Xử lý các trường bên trong tin việc làm trước khi lưu vào trong base elasticsearch
        obj_jobseek = Jobseek(data=data_body, index=index).get_data()
            
        # Create document
        _SERVER_.create_document(site=index, id_document=obj_jobseek['new_id'], document=obj_jobseek)
        # Trả về data thành công
        message = "Tạo mới bàn tin thành công"
        data = DataModel(True, message, item=obj_jobseek)
        error = None           
    except Exception as e:
        print(traceback.print_exc())
        error = ErrorModel(200, message)
        data = None
        
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    
    response = ResponseModel(data, error)
    return json.dumps(vars(response))


# Chỉnh sửa bản tin tuyển dụng trogn elasticsearch
@app.route("/update_tin", methods=["POST"])
def update_tin():
    # Lấy toàn bộ thông tin từ trường form-data
    data_body = dict(request.form)
    print(data_body)
    site = data_body.get('site')
    id_document = data_body.get('new_id')
    index = None
    error = None
    data = None
    message = "Không chỉnh sửa được tin tuyển dụng"
    try:
        # Kiểm tra xem đã nhập trường site hay chưa ?
        if site is None:
            message = "Chưa nhập site để chỉnh sửa tin tuyển dụng"
            raise ErrorSite
        else:
            index = 'tin_' + site
            
        # Kiểm tra xem id của tin tuyển dụng đó có tồn tại trong database elasticsearch hay không ?
        if id_document is None:
            message = f'Không tồn tại tin tuyển dụng'
            raise ErrorID
        
        id_document = data_body.get('new_id')
        
        # Bỏ đi key - value bao gồm site (tên index của elasticsearch), new_id (id của tin việc làm trong site đó)
        data_body.pop('site')
        data_body.pop('new_id')
        
        # Lấy thông tin document từ id đã được lấy ở trên
        document = _SERVER_.get_document(site=index, id_document=id_document)
        
        # Duyệt các trường được truyền vào 
        for key, value in data_body.items():
            document['_source'][key] = value
        
        # Phân tích, chỉnh sửa lỗi cú pháp trong trường hợp đối tượng là ứng viên
        obj_jobseek = Jobseek(data=document['_source'], index=index).get_data()
        # Chỉnh sửa lại document
        
        message = "Cập nhật bản tin thành công" 
        _SERVER_.update_document(site=index, id_document=id_document, document=obj_jobseek)
        error = None
        data = DataModel(True, message, item=obj_jobseek)

            
    except Exception as e:
        print(traceback.print_exc())
        error = ErrorModel(200, message)
        data = None
    except ErrorSite as e:
        data = None
        error = ErrorModel(200, message)
    except ErrorID as e:
        data = None
        error = ErrorModel(200, message)
    
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    
    response = ResponseModel(data, error)
    return json.dumps(vars(response))


# Chỉnh sửa tên công ty
@app.route("/update_name_company", methods=["POST"])
def update_name_company():
    data_body = request.form
    error = None
    data = None
    results = []
    message = 'Không cập nhật được tên của công ty'
    try:
        list_id_document = data_body.get('list_new_id') # List id việc làm
        update_name_company = data_body.get('update_name_company') # Tên công ty cần chỉnh sửa
        site = data_body.get('site')
        
        if not data_body:
            message = 'Chưa nhập trường nào phục vụ cho mục đích chỉnh sửa tên công ty'
            raise ErrorField
        
        # Check trường site nhập chưa
        if site is None:
            message = 'Chưa có nhập index site để cập nhật chỉnh sửa tên công ty'
            raise ErrorSite
        else:
            site = 'tin_' + site
        
        # Phân tách list id
        list_id_document = list_id_document.split(',')
        
        for id_document in list_id_document:
            # Check xem tin đó có tồn tại không ?
            if _SERVER_.base.exists(index=site, id=id_document):
                document = _SERVER_.get_document(site=site,id_document=id_document)
                document['_source']['usc_company'] = update_name_company
                _SERVER_.update_document(site=site, id_document=id_document, document=document['_source'])
                results.append(document['_source'])
            else:
                results.append(f'Không tồn tại id {id_document} trong site {site}')
        message = 'Chỉnh sửa tệp tin thành công'
        data = DataModel(True, message, item=results)
        error = None
        
    except Exception as e:
        print(traceback.print_exc())
        data = None
        error = ErrorModel(200, message)
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))


# Xem một bản tin bất kì trong elasticsearch
@app.route("/view_tin", methods=["GET", "POST"])
def view_tin():
    # Truyền 2 trường gồm index và id document ứng với index đó
    error = None
    data = None
    data_body = request.form
    id_document = data_body.get('new_id')
    site = data_body.get('site') 
    index = 'tin_' + site
    message = "Không mở được tệp tin"
    try:
        # Lấy toàn bộ index trong elasticsearch để check xem có trong đó không ?
        indexes = _SERVER_.get_all_index()
        if index in indexes:
            tin_tuyen_dung = _SERVER_.get_document(site=index, id_document=id_document)
            message = "Mở tệp tin thành công"
            data = DataModel(True, message, item=tin_tuyen_dung['_source'])
            error = None
    except Exception as e:
        print(traceback.print_exc())
        error = ErrorModel(200, message)
        
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))


# Xóa một bản tin trong index
@app.route("/delete_tin", methods=["POST"])
def delete_tin():
    error = None
    data = None
    data_body = request.form
    list_id_document = data_body.get('list_new_id') # Ngăn cách nhau bởi dấu phẩy
    index = 'tin_' + data_body.get('site')
    message = "Lỗi chương trình"
    try:
        # Lấy toàn bộ index trong elasticsearch để check xem có trong đó không ?
        indexes = _SERVER_.get_all_index()
        if index in indexes:
            # Xóa document từ id đã được nhập
            list_id_document = list_id_document.replace(' ', '') # Xóa kí tự khoảng trắng
            list_id_document = list_id_document.split(',') # Phân tách bởi dấu phẩy
            results = []
            for id_document in list_id_document:
                result = {}
                result['id_document'] = id_document
                if _SERVER_.check_document_index(index, id_document):
                    tin_tuyen_dung = _SERVER_.delete_document(site=index, id_document=id_document)
                    result['message'] = f'Xóa thành công tệp tin {id_document} trong base elasticsearch' 
                else:
                    result['message'] = f'Không xóa được tệp tin {id_document} do không tồn tại trong base elasticsearch' 
                results.append(result)
            message = "Chạy chương trình thành công."
            data = DataModel(True, message, item=results)
            error = None
    except Exception as e:
        print(e)
        error = ErrorModel(200, message)

    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    response = ResponseModel(data, error)
    return json.dumps(vars(response))


# Tìm kiếm tin tuyển dụng theo từ khóa trên site timviec365, vieclam24h, vieclam123
@app.route("/search_tin", methods=["POST", "GET"])
def search_tin():
    error = None
    data = None
    infor_search = None
    # Khai báo danh sách keyword phục vụ cho việc tìm kiếm trong tiêu đề, mô tả và yêu cầu của nhà tuyển dụng
    list_keyword = None
    message = 'Lỗi tìm kiếm'
    data_body = request.form
    
    
    # Lấy các trường đầu vào
    keyword = data_body.get('keyword') # Từ khóa
    keyword_linhvuc = data_body.get('new_lv') # Lấy từ khóa id lĩnh vực để tìm kiếm
    city = data_body.get('new_city') # Tỉnh thành, thành phố
    exp = data_body.get('new_exp') # Số năm kinh nghiệm
    hinh_thuc = data_body.get('new_hinh_thuc') # Hình thức làm việc
    cap_bac = data_body.get('new_cap_bac') # Cấp bậc (nhân viên, trưởng phòng, v.v.v)
    money = data_body.get('new_money') # Mức lương mong muốn
    gender = data_body.get('new_gioi_tinh') # Yêu cầu về giới tính
    quanhuyen = data_body.get('new_qh_id') # Quận huyện, phường xã
    hocvan = data_body.get('new_bang_cap') # Bằng cấp
    cat = data_body.get('new_cat_id') # Ngành nghề mong muốn
    type_search = data_body.get('type_search') # Kiểu loại search
    usc_company = data_body.get('usc_company') # Tên của công ty
    area_north = data_body.get('new_north_id') # Miền bắc
    area_centeral = data_body.get('new_centeral_id') # Miền trung
    area_south = data_body.get('new_south_id') # Miền nam
    present = data_body.get('new_present') # Thời gian cập nhật
    han_nop = data_body.get('han_nop') # Lấy tin tuyển dụng dựa vào thời gian hạn nộp
    page = data_body.get('pagination') # Phân trang
    size_tin = data_body.get('size') # Số lượng tin tuyển dụng mỗi page
    site = data_body.get('site') # Index của elasticsearch
    print(data_body)
    
    
    # Các điều kiện phục vụ tìm kiếm gồm: filter, match, multi_match, must, must_not, and v.v.v.v
    related_cond = []
    filter_cond = []
    negative_related_cond = []
    sort = []
    results = []
    num_tin = 0 # Tổng số lượng tin
    
    # Tìm kiếm theo từ khóa
    try:
        # Check điều kiện chưa nhập bất kỳ trường thông tin nào        
        if not data_body:
            message = "Chưa nhập trường nào phục vụ tìm kiếm"
            raise ErrorField
        
        # Trường site là lấy tin tuyển dụng từ size nào để tìm kiếm tin tuyển dụng trong site đó
        if site is None:
            message = 'Chưa có trường site để lấy tin tuyển dụng'
            raise ErrorSite
        else:
            # Thông tin giá trị của các trường có trong site đã được lấy từ đầu vào
            infor_search = information_search[site]
            site = 'tin_' + site
        
        # Mặc định trong trường hợp chưa có trường page và size_tin thì khởi tạo hằng số cho 2 trường
        if page is None:
            page = 1
        if size_tin is None:
            size_tin = 20
        if present is None:
            present = 3
        if han_nop is None or han_nop == '':
            han_nop = 0
        else:
            if not han_nop.isdigit():
                han_nop = 0
            else:
                han_nop = int(han_nop)
        if keyword is None:
            keyword = ''
        if type_search is None:
            type_search = '1'
        
        # Chuyển các trường present, page, size từ kiểu string sang int
        if isinstance(present, str):
            present = int(present)
        if isinstance(page, str) and page is not None and page != '':
            page = int(page)
            if page <=  0:
                page = 1
        if isinstance(size_tin, str):
            size_tin = int(size_tin)
        
        if gender == "Nam":
            gender = "1"
        elif gender == 'Nữ':
            gender = "2"
        elif gender == 'Khác':
            gender = "3"
        
        # Lấy khoảng thời gian là 1 ngày, 1 tuần hay 1 tháng đổ lại
        timestart = updatetime(present)
        
        # Lọc bỏ đi tỉnh thành trong câu
        for key in infor_search['tinhthanh'].keys():
            if infor_search['tinhthanh'][key].lower() in keyword.lower():
                city = key
                keyword = keyword.lower().replace(infor_search['tinhthanh'][key].lower(), '')
        
        # Lọc bỏ đi quận huyện trong câu
        for key in infor_search['quanhuyen'].keys():
            if infor_search['quanhuyen'][key].lower() in keyword.lower():
                quanhuyen = key
                keyword = keyword.lower().replace(infor_search['quanhuyen'][key].lower(), '')

        # Tìm kiếm theo địa điểm, công việc, kinh nghiệm, mức lương mong muốn, giới tính v.v.v
        if city != '0' and city is not None:
            should_cond_city = []
            should_cond_city.append({'wildcard': {'new_city': city}})
            should_cond_city.append({'wildcard': {'new_city': '0'}})
            should_cond_city.append({'match_phrase': {'new_city': 'Toàn quốc'}})
            related_cond.append({'bool': {'should': should_cond_city}})
        if quanhuyen != '0' and quanhuyen is not None:
            related_cond.append({'wildcard': {'new_qh_id': quanhuyen}})
        if exp != '0' and exp is not None:
            related_cond.append({'wildcard': {'new_exp': exp}})
        if hinh_thuc != '0' and hinh_thuc is not None:
            related_cond.append({'wildcard': {'new_hinh_thuc': hinh_thuc}})
        if cap_bac != '0' and cap_bac is not None:
            related_cond.append({'wildcard': {'new_cap_bac': cap_bac}})
        if money != '0' and money is not None:
            
            should_cond_money = []
            # Lấy trong khoảng id, trong khoảng tiền nhỏ nhất và lớn nhất do người dùng nhập
            # Ngoài ra còn chuyển đổi tiền tệ
            dict_type_money = preprocessing_money_v2(id_money_kg=money,
                                                money_type='5',
                                                money_unit='VND',
                                                money_min='0',
                                                money_max='0')
            
            list_id_kg_luong = dict_type_money['id_kg_luong']
            units_min_money, amounts_min_money = list(dict_type_money['min_money'].keys()), list(dict_type_money['min_money'].values())
            units_max_money, amounts_max_money = list(dict_type_money['max_money'].keys()), list(dict_type_money['max_money'].values())
            
            # Trong khoảng (ví dụ [1 - 3 triệu => id là 2], [3 - 5 triệu => id là 3], v.v.v)
            for id_lg in list_id_kg_luong:
                should_cond_money.append({'wildcard': {'new_money': id_lg}})
            
            # Tìm kiếm trong khoảng min_money và max_money (đơn vị tính theo vnđ, usd, eur)
            if len(units_min_money) != 0 and len(units_max_money) != 0: # Từ mức - đến mức
                for i in range(len(units_min_money)):
                    must_cond_money = []
                    must_cond_money.append({'wildcard': {'nm_unit': units_min_money[i]}})
                    must_cond_money.append({'range': {'nm_max_value': {'gte': amounts_min_money[i]}}})
                    must_cond_money.append({'range': {'nm_min_value': {'lt': amounts_max_money[i], 'gt': 0}}})
                    should_cond_money.append({'bool': {'must': must_cond_money}})
            elif len(units_min_money) != 0 and len(units_max_money) == 0:
                for i in range(len(units_min_money)):
                    must_cond_money = []
                    must_cond_money.append({'wildcard': {'nm_unit': units_min_money[i]}})
                    must_cond_money.append({'range': {'nm_max_value': {'gte': amounts_min_money[i]}}})
                    should_cond_money.append({'bool': {'must': must_cond_money}})
            elif len(units_min_money) == 0 and len(units_max_money) != 0:
                for i in range(len(units_min_money)):
                    must_cond_money = []    
                    must_cond_money.append({'wildcard': {'nm_unit': units_max_money[i]}})
                    must_cond_money.append({'range': {'nm_min_value': {'lt': amounts_max_money[i], 'gt': 0}}})
                    should_cond_money.append({'bool': {'must': must_cond_money}})
            else:
                pass
            
            related_cond.append({'bool': {'should': should_cond_money}})
        if hocvan != '0' and hocvan is not None:
            related_cond.append({'wildcard': {'new_bang_cap': hocvan}})
        if cat != '0' and cat is not None:
            related_cond.append({'wildcard': {'new_cat_id': cat}})
        if gender != '0' and gender is not None:
            should_cond_gender = []
            should_cond_gender.append({'match_phrase': {'new_gioi_tinh': infor_search['gioitinh'][gender]}})
            should_cond_gender.append({'match_phrase': {'new_gioi_tinh': 'Không yêu cầu'}})
            related_cond.append({'bool': {'should': should_cond_gender}})
        
        # Tìm kiếm theo vùng miền
        if area_south != '0' and area_south is not None:
            related_cond.append({'wildcard': {'new_south_id': area_south}})
        if area_centeral != '0' and area_centeral is not None:
            related_cond.append({'wildcard': {'new_centeral_id': area_centeral}})
        if area_north != '0' and area_north is not None:
            related_cond.append({'wildcard': {'new_north_id': area_north}})
        
        # Tìm kiếm theo lĩnh vực
        if keyword_linhvuc is not None:
            related_cond.append({'wildcard': {'new_lv': keyword_linhvuc}})
        
        # Tìm kiếm theo tên của công ty
        if usc_company != '' and usc_company is not None:
            usc_company = usc_company.lower() # Chuyển đổi chữ in hoa thành chữ in thường
            related_cond.append({'match_phrase': {'usc_company': usc_company}})
        
        # Lọc theo trường thời gian cập nhật và thời gian hạn nộp
        if site == 'tin_timviec365':
            filter_cond.append({'range': {'new_update_time': {'gte': timestart}}})
            filter_cond.append({'range': {'new_han_nop': {'lte': time_nop_minmax(value=3)}}})
            if han_nop:
                filter_cond.append({'range': {'new_han_nop': {'gte': int(round(datetime.now().timestamp())) - 31536000*han_nop}}})
            else:
                filter_cond.append({'range': {'new_han_nop': {'gte': 0}}})
                
        
        # Sắp xếp
        if type_search == '1':
            if site == 'tin_timviec365': 
                sort = [{
                    "new_hot.keyword": {"order": "desc"}, # Sắp xếp theo new_hot 
                    "new_cao.keyword": {"order": "desc"}, # Sau new_hot thì đến new_cao
                    "new_gap.keyword": {"order": "desc"}, # Sau new_cao thì đến new_gap
                    "new_ghim.keyword": {"order": "desc"}, # Cho những tin ghim lên đầu rồi mới đến những tin không ghim
                    "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                    "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
                }]
            else:
                sort = [{
                    "new_ghim.keyword": {"order": "desc"}, # Cho những tin ghim lên đầu rồi mới đến những tin không ghim
                    "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                    "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
                }]
        elif type_search == '0':
            sort = [{
                "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
            }]
        elif type_search == '2':
            sort = [{
                "new_money.keyword": {"order": "desc"}, # Sắp xếp theo lương tốt nhất
                "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
            }]
        
        # Tìm kiếm tin tuyển dụng
        
        if keyword is None or keyword == '':
            # Trong trường hợp không nhập keyword hoặc keyword bằng rỗng thì không xét đến điều kiện keyword nữa
            results, all_tin = SEARCH_JOBSEEK(filter=filter_cond,
                                    related=related_cond,
                                    sort=sort,
                                    index=site,
                                    list_keyword=[],
                                    size=size_tin,
                                    page=page,
                                    server=_SERVER_).search()
        else:
            # Tiền xử lý keyword (xóa các kí tự dạng số, kí tự đặc biệt và chuyển đổi từ viết tắt thành từ bình thường)
            # list_keyword = clean_keyword(keyword, search_stopword, search_acronyms)
            # list_word = list_keyword[0].split()
            # search_list_keyword = []
            # for i in range(len(list_word)):
            #     search_list_keyword.append(' '.join(list_word[0:len(list_word) - i]))
            
            # print(search_list_keyword)
            key_moi = clean_keyword(keyword,search_stopword, search_acronyms)
            list_word = preprocessing(key_moi[0], keep_punct=False).split()
            list_word_processing = []
            for word in list_word:
                res = word.replace('_', ' ')
                list_word_processing.append(res)
            
            # Tạo đối tượng tìm kiếm (tìm kiếm theo danh sách từ khóa)
            # Ví dụ : keyword = [hành chính nhân sự] => ['hành chính nhân sự', 'hành chính nhân', 'hành chính', 'hành']
            results, all_tin = SEARCH_JOBSEEK(filter=filter_cond,
                                    related=related_cond,
                                    sort=sort,
                                    index=site,
                                    list_keyword=list_word_processing,
                                    size=size_tin,
                                    page=page,
                                    server=_SERVER_).search()
                    
        # Đổ dữ liệu tin (dữ liệu trả về gồm có new_id, new_title, new_yeucau, new_mota)
        tin = []
        id_tin = []
        for tin_tuyen_dung in results:
            new = {
                    'new_id': tin_tuyen_dung['_source']['new_id'],
                    'new_title': tin_tuyen_dung['_source']['new_title'],
                    'new_yeucau': tin_tuyen_dung['_source']['new_yeucau'],
                    'new_mota': tin_tuyen_dung['_source']['new_mota'],
                    'new_money': tin_tuyen_dung['_source']['new_money'],
                    'new_cat_id': tin_tuyen_dung['_source']['new_cat_id'],
                    'new_city': tin_tuyen_dung['_source']['new_city'],
                    'new_lv': tin_tuyen_dung['_source']['new_lv'],
                    'new_han_nop': tin_tuyen_dung['_source']['new_han_nop'],
                    # 'usc_company': tin_tuyen_dung['_source']['usc_company']
            }
            id_tin.append(tin_tuyen_dung['_source']['new_id'])
            tin.append(new)
            
        id_tin = ','.join(id_tin)    
        data = DataModel(True, 'Tìm kiếm thành công', tin, all_tin, id_tin)
        
    except Exception as err:
        print(traceback.print_exc())
        data = None
        error = ErrorModel(200, message)
    except ErrorField as err:
        data = None
        error = ErrorModel(200, message)
    except ErrorSite as err:
        data = None
        error = ErrorModel(200, message)
    
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    
    # Trả về kiểu dữ liệu json
    response = ResponseModel(data, error)
    return json.dumps(vars(response), ensure_ascii=False)


# Tìm kiếm tin tuyển dụng theo tag ngành nghề
@app.route("/search_tin_tag", methods=["POST", "GET"])
def search_tin_tag():
    error = None
    data = None
    infor_search = None
    # Khai báo danh sách keyword phục vụ cho việc tìm kiếm trong tiêu đề, mô tả và yêu cầu của nhà tuyển dụng
    message = 'Lỗi tìm kiếm'
    data_body = request.form
    
    # Lấy các trường đầu vào
    keyword = data_body.get('keyword') # Từ khóa tag tìm kiếm
    keyword_linhvuc = data_body.get('new_lv') # Lấy id lĩnh vực tìm kiếm
    capbac_id = data_body.get('new_cap_bac') # Lấy id cấp bậc
    city_id = data_body.get('new_city') # Lấy id tỉnh thành
    cat_id = data_body.get('new_cat_id') # Lấy id ngành nghề
    quanhuyen_id = data_body.get('new_qh_id') # Lấy id quận huyện
    page = data_body.get('pagination') # Phân trang
    type_search = data_body.get('type_search') # Chọn loại search (phù hợp nhất, mới nhất, lương tốt nhất)
    size_tin = data_body.get('size') # Số lượng tin tuyển dụng mỗi page
    site = data_body.get('site') # Index của elasticsearch
    print(data_body)
    # Các điều kiện phục vụ tìm kiếm gồm: filter, match, multi_match, must, must_not, and v.v.v.v
    related_cond = [] # Điều kiện tổng: keyword + keyword lĩnh vực + tỉnh thành + v.v
    key_cond = []
    filter_cond = []
    sort = []
    results = []
    all_tin = 0 # Tổng số lượng tin
    
    # Tìm kiếm theo từ khóa và id lĩnh vực
    try:
        # Check điều kiện chưa nhập bất kỳ trường thông tin nào        
        if not data_body:
            message = "Chưa nhập trường nào phục vụ tìm kiếm"
            raise ErrorField
        
        # Trường site là lấy tin tuyển dụng từ size nào để tìm kiếm tin tuyển dụng trong site đó
        if site is None:
            message = 'Chưa có trường site để lấy tin tuyển dụng'
            raise ErrorSite
        else:
            # Thông tin giá trị của các trường có trong site đã được lấy từ đầu vào
            infor_search = information_search[site]
            site = 'tin_' + site
        
        # Mặc định trong trường hợp chưa có trường page và size_tin thì khởi tạo hằng số cho 2 trường
        if page is None:
            page = 1
        if size_tin is None:
            size_tin = 20
        if type_search is None:
            type_search = '1'
        
        # Chuyển các trường page, size từ kiểu string sang int
        if isinstance(page, str) and page is not None and page != '':
            page = int(page)
            if page <=  0:
                page = 1
        if isinstance(size_tin, str):
            size_tin = int(size_tin)
        
        # Tìm kiếm theo lĩnh vực và đẩy lên đầu danh sách khi tìm kiếm
        if city_id != '0' and city_id is not None:
            related_cond.append({'term': {'new_city': city_id}})
        if quanhuyen_id != '0' and quanhuyen_id is not None:
            related_cond.append({'term': {'new_qh_id': quanhuyen_id}})
        if capbac_id != '0' and capbac_id is not None:
            related_cond.append({'term': {'new_cap_bac': capbac_id}})
        if cat_id != '0' and cat_id is not None:
            related_cond.append({'term': {'new_cat_id': cat_id}})
        
        # Tìm kiếm theo lĩnh vực
        if keyword_linhvuc is not None and keyword_linhvuc != '':
            # key_cond.append({'match_phrase': {'new_lv': ' ' + keyword_linhvuc}})
            key_cond.append({'term': {'new_lv': keyword_linhvuc}})
        # Tìm kiếm theo title
        if keyword is not None and keyword != '':
            keyword = keyword.lower()
            key_cond.append({'match_phrase': {'new_title': keyword}})
        
        # Tìm kiếm kết hợp cả title và lĩnh vực
        related_cond.append({'bool': {'should': key_cond}})
        
        if type_search == '1': # Phù hợp nhất
            sort = [{
                "new_hot.keyword": {"order": "desc"}, # Sắp xếp theo new_hot 
                "new_cao.keyword": {"order": "desc"}, # Sau new_hot thì đến new_cao
                "new_gap.keyword": {"order": "desc"}, # Sau new_cao thì đến new_gap
                "new_ghim.keyword": {"order": "desc"}, # Cho những tin ghim lên đầu rồi mới đến những tin không ghim
                "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
            }]
        elif type_search == '2': # Mới nhất
            sort = [{
                "new_update_time": {"order": "desc"}, # Sắp xếp theo thời gian cập nhật
                "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
            }]
        elif type_search == '3': # Lương tốt nhất
            sort = [{
                "new_money.keyword": {"order": "desc"}, # Sắp xếp theo lương tốt nhất
                "new_han_nop": {"order": "desc"} # Sắp xếp theo thời gian hạn nộp
            }]
        
        results, all_tin = SEARCH_JOBSEEK(filter=filter_cond,
                                    related=related_cond,
                                    sort=sort,
                                    index=site,
                                    list_keyword=[],
                                    size=size_tin,
                                    page=page,
                                    server=_SERVER_).search()
        
        # Đổ dữ liệu tin (dữ liệu trả về gồm có new_id, new_title, new_yeucau, new_mota)
        tin = []
        id_tin = []
        for tin_tuyen_dung in results:
            new = {
                    'new_id': tin_tuyen_dung['_source']['new_id'],
                    'new_title': tin_tuyen_dung['_source']['new_title'],
                    'new_yeucau': tin_tuyen_dung['_source']['new_yeucau'],
                    'new_mota': tin_tuyen_dung['_source']['new_mota'],
                    'new_money': tin_tuyen_dung['_source']['new_money'],
                    'new_cat_id': tin_tuyen_dung['_source']['new_cat_id'],
                    'new_city': tin_tuyen_dung['_source']['new_city'],
                    'new_lv': tin_tuyen_dung['_source']['new_lv'],
                    'new_update_time': tin_tuyen_dung['_source']['new_update_time'],
                    'new_han_nop': tin_tuyen_dung['_source']['new_han_nop'],
                    # 'new_ghim': tin_tuyen_dung['_source']['new_ghim'],
            }
            id_tin.append(tin_tuyen_dung['_source']['new_id'])
            tin.append(new)
    
        id_tin = ','.join(id_tin)    
        data = DataModel(True, 'Tìm kiếm thành công', tin, all_tin, id_tin)
    except Exception as err:
        print(traceback.print_exc())
        data = None
        error = ErrorModel(200, message)
    except ErrorField as err:
        data = None
        error = ErrorModel(200, message)
    except ErrorSite as err:
        data = None
        error = ErrorModel(200, message)
    
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)
    
    # Trả về kiểu dữ liệu json
    response = ResponseModel(data, error)
    return json.dumps(vars(response), ensure_ascii=False)


if __name__ == '__main__':
    # Bật host và port để chạy API
    app.run(host='0.0.0.0', port=5001)