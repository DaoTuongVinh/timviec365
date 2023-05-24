"""
    Ví dụ: việc làm nhân viên kinh doanh biết tiếng anh 
    Thuật toán tìm kiếm như sau:
    Chỉ tìm những tin còn hạn tuyển dụng:
    1. Tìm trong title + mô tả + yêu cầu tất cả những tin tuyển dụng còn hạn có xuất hiện chính xác từ khóa “nhân viên kinh doanh biết tiếng anh” hiển thị ra ngoài. Or:
    Tin trong Tiêu để xuất hiện nhân viên kinh doanh biết tiếng anh thì hiển thị luôn không cần tìm kiếm “yêu cầu và mô tả nữa” nếu tiêu đề không xuất hiện thì mới tìm kiếm sang mô tả có cụm từ “nhân viên kinh doanh biết tiếng anh” nếu mô tả mà có thì cũng  hiển thị luôn tin đó mà không tìm trong yêu câu nữa, nếu mô tả cũng không có cụm từ đó thì tìm tiếp trong yêu cầu có thì hiện thị tin đó không có đúng cụm từ thì loại.
    {từ “việc làm” bị Lâm lọc ra vì bộ lọc cố định của Lâm bỏ các key tiền tố hiển nhiên như: việc làm; tuyển dụng; tìm việc làm}; sắp xếp theo thời gian cứ mới đăng lên trước, cũ lên sau. 
    2. Sau đó tiếp tục cắt từ để tìm kiếm theo cách bớt dần từ
    Cũng là hoặc or như ở trên
    Bớt 1 từ: K -1 = 6
    “nhân viên kinh doanh biết tiếng anh” có 7 từ cắt các key có 6 từ để tìm chính xác 6 từ đó chính xác liền nhau trong tiêu + yêu cầu + mô tả
    + nhân viên kinh doanh biết tiếng
    + viên kinh doanh biết tiếng anh
    Bớt 2 từ: K – 2 = 5
    + nhân viên kinh doanh biết
    + viên kinh doanh biết tiếng
    + kinh doanh biết tiếng anh
    + viên kinh doanh biết tiếng
    ……Ckk-i
    3. 

"""
from copy import deepcopy


def recruitment_page(num_tin_keyword: list, size_tin: int):
    # Tìm kiếm tin tuyển dụng cho mỗi page
    """_summary_
        Mục đích tổng quan của hàm này là mỗi page chứa các tin như thế nào
    Args:
        keyword (list): Số lượng tin tuyển dụng của mỗi từ khóa
        size_tin (int): Số lượng tin tuyển dụng của mỗi trang

    Returns:
        _type_: list of dict tin keyword
    """
    
    keyword = deepcopy(num_tin_keyword)
    
    # Bước 1
    i = 1
    dict_list_tin_keyword = []
    dict_tin_keyword = {}
    results = {}
    value = keyword[0]
    remainder = size_tin - keyword[0] % size_tin
    dict_tin_keyword['0'] = keyword[0]
    
    if len(keyword) > 1:
        if remainder == size_tin:
            dict_list_tin_keyword.append(dict_tin_keyword)
            dict_tin_keyword = {}
    else:
        dict_list_tin_keyword.append(dict_tin_keyword)
        dict_tin_keyword = {}
    
    #
    while i < len(keyword):
        if keyword[i] == 0:
            i += 1
            continue
        
        if keyword[i] <= remainder:
            remainder -= keyword[i]
            dict_tin_keyword[str(i)] = keyword[i]
        else:
            if remainder:
                dict_tin_keyword[str(i)] = remainder
            dict_list_tin_keyword.append(dict_tin_keyword)
            keyword[i] -= remainder
            remainder = size_tin - keyword[i] % size_tin
            dict_tin_keyword = {}
            dict_tin_keyword[str(i)] = keyword[i]
            
        if i ==  len(keyword) - 1:
            dict_list_tin_keyword.append(dict_tin_keyword)
        i += 1
    
    # Bước 2
    load_keyword = []
    load_from = {}
    page = 1

    for index, dict_keyword in enumerate(dict_list_tin_keyword):
        if len(dict_keyword.keys()) >= 2:
            if sum(dict_keyword.values()) <= size_tin:
                results[str(page)] = deepcopy(dict_keyword)
                for i_key, i_value in dict_keyword.items():
                    if i_key not in load_keyword:
                        results[str(page)]['from' + i_key] = 0
                        load_from['from' + i_key] = i_value
                        load_keyword.append(i_key)
                    else:
                        results[str(page)]['from' + i_key] = load_from['from' + i_key]
                        load_from['from' + i_key] += i_value
                page += 1
            else:
                # Nếu giá trị lớn hơn size_tin thì chỉ có thể là giá trị đầu
                value_first = dict_keyword[list(dict_keyword.keys())[0]]
                key_first = list(dict_keyword.keys())[0]
                dict_keyword[list(dict_keyword.keys())[0]] = value_first % size_tin
                dict1 = {key_first: value_first - value_first % size_tin}
                dict2 = dict_keyword
                
                # Chạy dict1
                page_after = dict1[key_first] // size_tin + page - 1
                results[f"{page},{page_after}"] = deepcopy(dict1)
                if key_first not in load_keyword:
                    results[f"{page},{page_after}"]['from' + key_first] = 0
                    load_from['from' + key_first] = dict1[key_first]
                    load_keyword.append(key_first)
                else:
                    results[f"{page},{page_after}"]['from' + key_first] = load_from['from' + key_first]
                    load_from['from' + key_first] += dict1[key_first]
                page = page_after
                page += 1
                
                # Chạy dict2
                results[str(page)] = deepcopy(dict2)
                for i_key, i_value in dict2.items():
                    if i_key not in load_keyword:
                        results[str(page)]['from' + i_key] = 0
                        load_from['from' + i_key] = i_value
                        load_keyword.append(i_key)
                    else:
                        results[str(page)]['from' + i_key] = load_from['from' + i_key]
                        load_from['from' + i_key] += i_value
                page += 1
        else:
            key = list(dict_keyword.keys())[0]
            if dict_keyword[key] <= size_tin:
                string_page = str(page)
            else:
                page_after = dict_keyword[key] // size_tin + page - 1
                if dict_keyword[key] % size_tin == 0:
                    string_page = f"{page}, {page_after}"
                else:
                    string_page = f"{page}, {page_after + 1}"
                page = page_after
                    
            results[string_page] = deepcopy(dict_keyword)
            if key not in load_keyword:
                results[string_page]['from' + key] = 0
                load_from['from' + key] = dict_keyword[key]
                load_keyword.append(key)
            else:
                results[string_page]['from' + key] = load_from['from' + key]
                load_from['from' + key] += dict_keyword[key]
            page += 1
    return results


def check_page(results_tin, query_tin, page, size, index, server):
    """_summary_
        Kiểm tra xem page đó ở đâu trong tổng số lượng tin tuyển dụng (chỉ lấy kết quả mỗi page đó)
    Args:
        results_tin (_type_): _description_
        query_tin (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    resp = []
    for idx, (key, value) in enumerate(results_tin.items()):
        list_key = key.split(',')
        if len(key.split(',')) > 1:
            if int(page) <= int(list_key[1]) and int(page) >= int(list_key[0]):
                query_tin[int(list(value.keys())[0])]['size'] = size
                query_tin[int(list(value.keys())[0])]['from'] = (page - int(list_key[0])) * size + value['from' + list(value.keys())[0]]
                resp = server.base.search(index=index, body=query_tin[int(list(value.keys())[0])])['hits']['hits']
        else:
            if page == int(key):
                for idx_keyword, (keyword, keyword_value) in enumerate(value.items()):
                    if idx_keyword < len(value.items()) // 2:
                        query_tin[int(keyword)]['size'] = keyword_value
                        query_tin[int(keyword)]['from'] = value['from' + keyword]
                        resp_idx_keyword = server.base.search(index=index, body=query_tin[int(keyword)])
                        resp += list(resp_idx_keyword['hits']['hits'])
    return resp


# Tìm kiếm tin việc làm trên sitr timviec365, vieclam24h, vieclam123
class SEARCH_JOBSEEK:
    
    def __init__(self,
                filter: list,
                related: list,
                sort: list,
                list_keyword: list,
                index: str,
                size: int,
                page: int,
                server) -> None:
        """_summary_
            Một số điều kiện để tìm kiếm tin việc làm dựa theo tiêu chí nào đó
        """
        self.filter = filter
        self.related = related
        self.negative_related = []
        self.sort = sort
        self.index = index
        self.list_keyword = list_keyword
        self.size = size
        self.page = page
        self.server = server
        
    
    def step1(self):
        # Tìm kiếm tin việc làm dựa vào 3 trường sau: tiêu đề, mô tả, yêu cầu công việc của tin tuyển dụng
        self.negative_related = []
        
        # priority_level được coi thứ tự ưu tiên được tìm kiếm  (tiêu đề trước rồi đến mô tả, cuối cùng là yêu cầu)
        priority_level = {
            '0': ['new_title'],
            '1': ['new_mota'],
            '2': ['new_yeucau']
        }
        
        query = []
        num_tin = []
        
        related_content = deepcopy(self.related)
        
        if len(self.list_keyword):
            # for idx, keyword in enumerate(self.list_keyword):
            #     i = 0
            #     while i < len(priority_level):
            #         levels = priority_level[str(i)]
            #         match_phrase_level = []
            #         related_content = deepcopy(self.related)
            #         if idx > 0:
            #             for level in levels:
            #                 self.negative_related.append({'match_phrase': {level: self.list_keyword[idx - 1]}})
            #         for level in levels:
            #             match_phrase_level.append({'match_phrase': {level: self.list_keyword[idx]}})
            #         related_content.append({'bool': {'should': match_phrase_level}})
            #         query_content = {
            #             'query': {'bool' : {'must': related_content, 'filter': self.filter, 'must_not': self.negative_related}},
            #             'sort': self.sort,
            #             'track_scores': True,
            #             'size': 1,
            #             'from': 0,
            #         }
            #         qr_cp = deepcopy(query_content)
            #         resp_by_content = self.server.base.search(index=self.index, body=qr_cp)
            #         if resp_by_content['hits']['total']['value'] > 0:
            #             query.append(qr_cp)
            #             num_tin.append(resp_by_content['hits']['total']['value'])
            #             break
            #         i += 1
            
            
            for idx, keyword in enumerate(self.list_keyword):
                match_phrase_level = []
                for i in range(len(priority_level)):
                    levels = priority_level[str(i)]
                    for level in levels:
                        match_phrase_level.append({'match_phrase': {level: self.list_keyword[idx]}}) 
                related_content.append({'bool': {'should': match_phrase_level}})
            query_content = {
                        'query': {'bool' : {'must': related_content, 'filter': self.filter, 'must_not': self.negative_related}},
                        'sort': self.sort,
                        'track_scores': True,
                        'size': 1,
                        'from': 0,
                    }
            qr_cp = deepcopy(query_content)
            resp_by_content = self.server.base.search(index=self.index, body=qr_cp)
            if resp_by_content['hits']['total']['value'] > 0:
                query.append(qr_cp)
                num_tin.append(resp_by_content['hits']['total']['value'])
        else:
            related_content = deepcopy(self.related)
            query_content = {
                'query': {'bool' : {'must': related_content, 'filter': self.filter, 'must_not': self.negative_related}},
                'sort': self.sort,
                'track_scores': True,
                'size': 1,
                'from': 0,
            }
            qr_cp = deepcopy(query_content)
            resp_by_content = self.server.base.search(index=self.index, body=qr_cp)
            if resp_by_content['hits']['total']['value'] > 0:
                query.append(qr_cp)
                num_tin.append(resp_by_content['hits']['total']['value'])
        
        return num_tin, query
        
        
    def search(self):
        
        # Thuật toán tìm kiếm sản phẩm trên site timviec365, vieclam24h, vieclam123 thực hiện như sau:
        
        # Bước 1: Tìm kiếm theo các điều kiện để lọc (như tỉnh thành, quận huyện, phường xã, còn hoạt động hay không ? v.v.v)
        
        # Bước 2: Tìm kiếm theo danh sách từ khoá sau khi đã lọc ở bước 1 (đúng nhiều từ hơn thì sẽ lên đầu)
        
        # Bước 3: Sau khi có được kết quả trả về thì phân trang tin và tìm kiếm theo từng page 1, 2, 3, v.v.
        
        resp = []
        num_tin, query = self.step1()
        if len(num_tin):
            results_step1 = recruitment_page(num_tin, self.size)
            resp = check_page(results_step1, query, self.page, self.size, self.index, self.server)

        return resp, sum(num_tin)


# Tìm kiếm ứng viên trên site timviec365
class SEARCH_CANDIDATE:
    """_summary_
    Luồng hoạt động của tìm kiếm ứng viên như sau:
    - Đầu tiên là tìm kiếm các bước:
        + Bước 1: Tìm kiếm theo tiêu đề (việc làm mong muốn của ứng viên)
        + Bước 2: Nếu từ khóa nhập vào mà tiêu đề không có mục tiêu nghề nghiệp của ứng viên
        + Bước 3: Nếu từ khóa nhập vào không có ở bước 1 và bước 2 => Đi tiếp vào trong trường kỹ năng của ứng viên
        + Bước 4: Sau đó mới tìm kiếm theo tên ứng viên nếu từ khóa nhập theo tên
        - Ngoài ra thêm các điều kiện bên ngoài như: độ tuổi, tỉnh thành, quận huyện, bằng cấp, cấp bậc, v.v.v
    """
    def __init__(self,
                filter: list,
                related: list,
                sort: list,
                list_keyword: str,
                index: str,
                size: int,
                page: int,
                server) -> None:
        """_summary_
            Một số điều kiện để tìm kiếm ứng viên phù hợp tiêu chí nào đó
        Args:
            filter (_type_): 
            related (_type_): Tìm kiếm ứng viên dựa theo yếu tố như vị trí (Tỉnh thành, quận huyện), mức lương, v.v.v
            sort (_type_): Sắp xếp theo thòi gian cập nhật
        """
        self.filter = filter
        self.related = related
        self.negative_related = []
        self.sort = sort
        self.index = index
        self.list_keyword = list_keyword
        self.size = size
        self.page = page
        self.server = server
        

    def step1(self):
        self.negative_related = []
        if self.index == 'tin_uvvieclam123':
            priority_level = ['cv_vitriut', 'cv_kynang', 'cv_muctieu', 'cv_kinhnghiem']
        elif self.index == 'tin_uvtimviec365' or self.index == 'tin_ungvientimviec365':
            # Ưu tiên tìm kiếm trong tiêu đề sau đó đến mục tiêu và cuối cùng là kỹ năng của ứng viên
            priority_level = {
                '0': ['cv_title', 'cv_pdf_title'],
                '1': ['cv_muctieu', 'cv_pdf_muctieu'],
                '2': ['cv_kynang', 'cv_pdf_kynang']
            }
        query = []
        num_tin = []
        
        # Thiết lập query phục vụ mục đích tìm kiếm
        if len(self.list_keyword):
            for idx, keyword in enumerate(self.list_keyword):
                i = 0
                while i < len(priority_level):
                    levels = priority_level[str(i)]
                    match_phrase_level = []
                    related_content = deepcopy(self.related)
                    if idx > 0:
                        for level in levels:
                            self.negative_related.append({'match_phrase': {level: self.list_keyword[idx - 1]}})
                    for level in levels:
                        match_phrase_level.append({'match_phrase': {level: self.list_keyword[idx]}})
                    related_content.append({'bool': {'should': match_phrase_level}})
                    query_content = {
                        'query': {'bool' : {'must': related_content, 'filter': self.filter, 'must_not': self.negative_related}},
                        'sort': self.sort,
                        'track_scores': True,
                        'size': 1,
                        'from': 0,
                    }
                    qr_cp = deepcopy(query_content)
                    resp_by_content = self.server.base.search(index=self.index, body=qr_cp)
                    if resp_by_content['hits']['total']['value'] > 0:
                        query.append(qr_cp)
                        num_tin.append(resp_by_content['hits']['total']['value'])
                        break
                    i += 1
        else:
            related_content = deepcopy(self.related)
            query_content = {
                'query': {'bool' : {'must': related_content, 'filter': self.filter, 'must_not': self.negative_related}},
                'sort': self.sort,
                'track_scores': True,
                'size': 1,
                'from': 0,
            }
            qr_cp = deepcopy(query_content)
            resp_by_content = self.server.base.search(index=self.index, body=qr_cp)
            if resp_by_content['hits']['total']['value'] > 0:
                query.append(qr_cp)
                num_tin.append(resp_by_content['hits']['total']['value'])
        return num_tin, query
    
    
    def search(self):
        
        # Thuật toán tìm kiếm sản phẩm trên site timviec365 thực hiện như sau
        
        # Bước 1: Tìm kiếm theo các điều kiện để lọc (như tỉnh thành, quận huyện, phường xã, còn hoạt động hay không ? v.v.v)
        
        # Bước 2: Tìm kiếm theo danh sách từ khoá sau khi đã lọc ở bước 1 (đúng nhiều từ hơn thì sẽ lên đầu)
        
        # Bước 3: Sau khi có được kết quả trả về thì phân trang tin và tìm kiếm theo từng page 1, 2, 3, v.v.
        
        resp = []
        num_tin, query = self.step1()
        if len(num_tin):
            results_step1 = recruitment_page(num_tin, self.size)
            # resp = self.step2(results_step2, query)   
            resp = check_page(results_step1, query, self.page, self.size, self.index, self.server)
        
        return resp, sum(num_tin)
        

# Tìm kiếm sản phẩm trên site raonhanh365
class SEARCH_PRODUCT:
    def __init__(self,
                filter: list,
                related: list,
                negative_related: list,
                sort:list,
                list_keyword: str,
                index: str,
                size: int,
                page: int,
                server):
        """_summary_
            Một số điều kiện để tìm kiếm ứng viên phù hợp tiêu chí nào đó
        Args:
            filter (_type_): 
            related (_type_): Tìm kiếm ứng viên dựa theo yếu tố như vị trí (Tỉnh thành, quận huyện), mức lương, v.v.v
            sort (_type_): Sắp xếp theo thòi gian cập nhật
        """
        self.filter = filter
        self.related = related
        self.negative_related = negative_related
        self.sort = sort
        self.index = index
        self.list_keyword = list_keyword
        self.size = size
        self.page = page
        self.server = server
    
    
    def step1(self):
        # Khởi tạo kết quả trả về gồm tổng số lượng tin tại query và câu truy vấn query đó
        num_tin = []
        query = []
        
        if len(self.negative_related):
            query_name = {
                    'query': {
                        'bool' : {
                            'must': self.related,
                            'filter': self.filter,
                        }
                    },
                    'sort': self.sort,
                    'track_scores': True,
                    'size': 1,
                    'from': 0,
                }
            qr_cp = deepcopy(query_name)
            resp_by_name = self.server.base.search(index=self.index, body=qr_cp)
            if resp_by_name['hits']['total']['value'] > 0:
                query.append(qr_cp)
                num_tin.append(resp_by_name['hits']['total']['value'])
            for i in range(len(self.negative_related)):
                self.related.pop(0)
    
        if len(self.list_keyword):
            # Trong trường hợp danh sách keyword lớn hơn 0
            for idx, keyword in enumerate(self.list_keyword):
                related_name = deepcopy(self.related)
                if idx > 0:
                    # Khi bước vào tìm kiếm các từ sau từ khóa đầu tiên, ta cần kiểm tra xem có trùng nhau kết quả của các từ khóa đó có trùng nhau hay không ? 
                    self.negative_related.append({'match_phrase': {'new_title': self.list_keyword[idx-1]}})
                
                related_name.append({'match_phrase': {'new_title': self.list_keyword[idx]}})
                # Câu truy vấn
                query_name = {
                    'query': {
                        'bool' : {
                            'must': related_name,
                            'filter': self.filter,
                            'must_not': self.negative_related
                        }
                    },
                    'sort': self.sort,
                    'track_scores': True,
                    'size': 1,
                    'from': 0,
                }
                qr_cp = deepcopy(query_name)
                resp_by_name = self.server.base.search(index=self.index, body=qr_cp)
                # Kết quả trả về chỉ có 1 tin (để tối ưu thời gian thực thi)
                if resp_by_name['hits']['total']['value'] > 0:
                    query.append(qr_cp)
                    num_tin.append(resp_by_name['hits']['total']['value'])
        
        # Nếu không có keyword và không truyền bất kì tham số nào 
        if len(self.list_keyword) == 0 and len(self.negative_related) == 0:
            query_name = {
                    'query': {
                        'bool' : {
                            'must': self.related,
                            'filter': self.filter,
                        }
                    },
                    'sort': self.sort,
                    'track_scores': True,
                    'size': 1,
                    'from': 0,
                }
            qr_cp = deepcopy(query_name)
            resp_by_name = self.server.base.search(index=self.index, body=qr_cp)
            if resp_by_name['hits']['total']['value'] > 0:
                query.append(qr_cp)
                num_tin.append(resp_by_name['hits']['total']['value'])
        return num_tin, query
        
            
    def search(self):
        # Thuật toán tìm kiếm sản phẩm trên site raonhanh365 thực hiện như sau
        
        # Bước 1: Tìm kiếm theo các điều kiện để lọc (như tỉnh thành, quận huyện, phường xã, còn hoạt động hay không ? v.v.v)
        
        # Bước 2: Tìm kiếm theo danh sách từ khoá sau khi đã lọc ở bước 1 (đúng nhiều từ hơn thì sẽ lên đầu)
        
        # Bước 3: Sau khi có được kết quả trả về thì phân trang tin và tìm kiếm theo từng page 1, 2, 3, v.v.
        
        num_tin, query = self.step1()
        
        resp = []
        if sum(num_tin) > 0:
            results_step1 = recruitment_page(num_tin, self.size) # Quá trình phân trang tin tuyển dụng
            resp = check_page(results_step1, query, self.page, self.size, self.index, self.server)
        return resp, sum(num_tin)
