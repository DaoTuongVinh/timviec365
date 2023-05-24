from requests import Response, Request, Session
import requests
import traceback
from time import sleep
from utils.vietnamese_normalizer import clean_text
from DataManager.candidate import Candidate
from DataManager.product import Product
from DataManager.jobseek import Jobseek
traceback.format_exc()


# Tạo data trong Elasticsearch từ site https://raonhanh365.vn/viec-lam.html
def create_data_product_raonhanh365(es, index: str, link_url: str):
    
    # Riêng đối với site raonhanh365 ta cần mapping trường new_cate_id nếu muốn tìm kiếm thành công
    mapping = {
        "mappings": {
            "dynamic": True,
            "properties": {
                "new_cate_id": {
                    "type": "nested"
                }
            }
        },
        "settings": {
            "index.mapping.total_fields.limit": 10000
        }
    }
    
    #es.indices.delete(index=index, ignore=[400, 404])
    try:
        es.indices.create(index=index, ignore=[400, 404], body=mapping)
        page = 870
        while True:
            form_data = {'page': str(page)}
            request = Request('POST', link_url, files = {'page': (None, form_data['page'])}).prepare()
            response = Session().send(request)
            data = response.json()
            if len(data['data']['items']) > 0:
                print(f"Loading tin san pham {page}")
                for i_data in data['data']['items']:
                    try:
                        product = Product(data=i_data, index=index).get_data()
                        resp = es.index(index=index, id=i_data['new_id'], document=product)
                    except Exception as err:
                        print(err, i_data['new_id'])
                sleep(1)
                print(f"Loaded tin san pham {page}")
            else:
                break
            page += 1
    except Exception:
        print(traceback.format_exc()
)


# Tạo data trong Elasticsearch từ site vieclam24h và vieclam123
def create_data_job_vieclam(es, index: str, link_url, from_parameter: bool = True):
    """_summary_
        Tạo data từ các site timviec365, vieclam24h, v.v.v
    Args:
        es (_type_): Khởi tạo es
        index (str): Index trong elasticsearch
        link_url (_type_): Đường dẫn link
        from_parameter (bool): Truyền tham số trên url hay là trong form-body
    """
    # es.indices.delete(index=index, ignore=[400, 404])
    
    mapping = {
        "properties": {
            "nm_min_value": {
                "type": "long",
            },
            "nm_max_value": {
                "type": "long",
            }
        }
    }
    
    # es.indices.create(index="tin_timviec365", ignore=[400, 404], body=mapping)
    # es.indices.put_mapping(index="tin_timviec365", body=mapping)
    
    page = 1
    while True:
        if from_parameter:
            response = requests.get(link_url + str(page))
            data = response.json()
        else:
            form_data = {'page': str(page)}
            request = Request('POST', link_url, files = {'page': (None, form_data['page'])}).prepare()
            response = Session().send(request)
            data = response.json()
        if len(data):
            print(f"Loading tin tuyen dung {page}")
            for i_data in data:
                jobseek = Jobseek(data=i_data, index=index).get_data()
                resp = es.index(index=index, id=i_data['new_id'], document=jobseek)
            print(f"Loaded tin tuyen dung {page}")
        else:
            break
        page += 1


def create_data_ungvien(es, index: str, link_url, from_parameter: bool = True):
    """_summary_
        Tạo data từ các site timviec365, vieclam24h, v.v.v
    Args:
        es (_type_): Khởi tạo es
        index (str): Index trong elasticsearch
        link_url (_type_): Đường dẫn link
        from_parameter (bool): Truyền tham số trên url hay là trong form-body
    """
    page = 1
    while True:
        if from_parameter:
            response = requests.get(link_url + str(page))
            data = response.json()
        else:
            form_data = {'page': str(page)}
            request = Request('POST', link_url, files = {'page': (None, form_data['page'])}).prepare()
            response = Session().send(request)
            data = response.json()
            
        # check số lượng tin được trả về
        if len(data):
            print(f"Loading danh sách ứng viên {page}")
            for i_data in data:
                i_data['use_create_time'] = int(i_data['use_create_time'])
                i_data['use_update_time'] = int(i_data['use_update_time'])
                if i_data['use_first_name'] is not None:
                    i_data['use_first_name'] = clean_text(i_data['use_first_name'])
                if i_data['cv_vitriut'] is not None:
                    i_data['cv_vitriut'] = clean_text(i_data['cv_vitriut'])
                if i_data['cv_kynang'] is not None:
                    i_data['cv_kynang'] = clean_text(i_data['cv_kynang'])
                if i_data['cv_muctieu'] is not None:
                    i_data['cv_muctieu'] = clean_text(i_data['cv_muctieu'])
                if i_data['cv_kinhnghiem'] is not None:
                    i_data['cv_kinhnghiem'] = clean_text(i_data['cv_kinhnghiem'])
                
                resp = es.index(index=index, id=i_data['use_id'], document=i_data)
            print(f"Loaded danh sách ứng viên {page}")
        else:
            break
        page += 1


def create_data_ungvien_timviec365(es, index: str, link_url: str):
    """_summary_

    Args:
        es (_type_): Elasticsearch
        index (str): Index trong elasticsearch
        link_url (str): Link url
    """
    es.indices.delete(index=index, ignore=[400, 404])
    # es.indices.create(index=index, ignore=[400, 404])
    parameter = {
        'start': 0, # Bắt đầu từ 0
        'current': 100 # Đến số lượng 20 tin tiếp theo
    }
    
    page = 1
    while True:
        print(f"Loading page {page}.")
        start = (page - 1) * parameter['current'] + parameter['start'] + 1
        current = parameter['current']
        url = link_url + f'?start={start}&current={current}'
        response = requests.get(url=url,
                            headers={"User-Agent":"Mozilla/5.0"},
                            timeout=3600)
        sleep(1)
        data = response.json()
        if data['data']['items'] is not None:
            for i_data in data['data']['items']:
                if not es.exists(index=index, id=i_data['use_id']):
                    candidate = Candidate(data=i_data, index=index).get_data()
                    resp = es.index(index=index, id=candidate['use_id'], document=candidate)
                # # else:
                # #     document = es.get(index=index, id=i_data['use_id'])
                    
                # #     if 'um_min_value' in document['_source'].keys():
                # #         if document['_source']['um_min_value'] is None:
                # #             document['_source']['um_min_value'] = 0
                # #         else:
                # #             document['_source']['um_min_value'] = int(document['_source']['um_min_value'])
                # #     else:
                # #         document['_source']['um_min_value'] = '0'
                            
                # #     if 'um_max_value' in document['_source'].keys():
                # #         if document['_source']['um_max_value'] is None:
                # #             document['_source']['um_max_value'] = 0
                # #         else:
                # #             document['_source']['um_max_value'] = int(document['_source']['um_max_value'])                            
                        
                # #     if 'um_min_value' in document['_source'].keys():
                # #         if document['_source']['um_min_value'] is None:
                # #             document['_source']['um_min_value'] = 0
                # #         else:
                # #             document['_source']['um_min_value'] = 0
                            
                # #     if 'um_unit' in document['_source'].keys():
                # #         if document['_source']['um_max_value'] is None:
                # #             document['_source']['um_max_value'] = '0'
                # #     else:
                # #         document['_source']['um_max_value'] = '0'
                        
                # #     if 'um_type' in document['_source'].keys():
                # #         if document['_source']['um_type'] is None:
                # #             document['_source']['um_type'] = '0'
                # #     else:
                # #         document['_source']['um_type'] = '0'
                        
                # #     if 'um_unit' in document['_source'].keys():
                # #         if document['_source']['um_unit'] is None:
                # #             document['_source']['um_unit'] = '0'
                # #     else:
                # #         document['_source']['um_unit'] = '0'
        
                    
                #     candidate = Candidate(data=i_data, index=index).get_data()
                #     resp = es.update(index=index, id=candidate['use_id'], doc=candidate)
                    
            print(f"Loaded page {page}.")
        else:
            break
        
        page += 1