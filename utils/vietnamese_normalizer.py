# -*- coding: utf-8 -*-

import regex as reg
import re
import html
from urllib.parse import unquote
from ftfy import fix_encoding
from unidecode import unidecode
from vncorenlp import VnCoreNLP

# phân tách keyword thành cụm từ (ví dụ: nhân viên kinh doanh -> nhân_viên kinh_doanh)
vncorenlp_file = 'C:/Users/Vinh/Downloads/timviec365_elasticsearch-main/utils/VnCoreNLP-1.1.1.jar'
vncorenlp = VnCoreNLP(vncorenlp_file, annotators="wseg") # init vncorenlp server

def cleaning_text(text, keep_punct=True):
    """ 
    Removing non-latin chars
    But keeping numbers and punctuations as default
    """
    if keep_punct:
        return reg.sub(u'[^\p{Latin}0-9[:punct:]]+', u' ', text)
    return reg.sub(u'[^\p{Latin}0-9]+', u' ', text)

def tokenizing(text):
    """
    This function returns a list of VNese tokens 
    extracted from a full sentence
    """
    tokens = vncorenlp.tokenize(text)
    if any(isinstance(el, list) for el in tokens): # check if a list is multidimensional
        flat_tokens = [item for sublist in tokens for item in sublist] # flatten the list of lists
        return flat_tokens
    return tokens

def joining(tokens):
    return ' '.join(tokens)

def lowercasing(text):
    return text.lower()

def removing_accent(text):
    return unidecode(text)

def preprocessing(text, keep_punct=True):
    return lowercasing(joining(tokenizing(cleaning_text(text, keep_punct))))


uniChars = "àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆĐÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴÂĂĐÔƠƯ"
unsignChars = "aaaaaaaaaaaaaaaaaeeeeeeeeeeediiiiiooooooooooooooooouuuuuuuuuuuyyyyyAAAAAAAAAAAAAAAAAEEEEEEEEEEEDIIIOOOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYAADOOU"

def loaddicchar():
    dic = {}
    char1252 = 'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'.split(
        '|')
    charutf8 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ".split(
        '|')
    for i in range(len(char1252)):
        dic[char1252[i]] = charutf8[i]
    return dic


dicchar = loaddicchar()


def convert_unicode(txt):
    return reg.sub(
        r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ',
        lambda x: dicchar[x.group()], txt)


"""
    Start section: Chuyển câu văn về kiểu gõ telex khi không bật Unikey
    Ví dụ: thủy = thuyr, tượng = tuwowngj
"""
bang_nguyen_am = [['a', 'à', 'á', 'ả', 'ã', 'ạ', 'a'],
                  ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'aw'],
                  ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'aa'],
                  ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'e'],
                  ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ee'],
                  ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'i'],
                  ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'o'],
                  ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'oo'],
                  ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'ow'],
                  ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'u'],
                  ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'uw'],
                  ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'y']]
bang_ky_tu_dau = ['', 'f', 's', 'r', 'x', 'j']

nguyen_am_to_ids = {}

for i in range(len(bang_nguyen_am)):
    for j in range(len(bang_nguyen_am[i]) - 1):
        nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)


file_vn_dict = open('C:/Users/Vinh/Downloads/timviec365_elasticsearch-main/dict_lang/vi_char.txt', 'r', encoding = 'utf8')
list_vn_dict = []
for char_vn_dict in file_vn_dict:
    char_vn_dict = char_vn_dict.replace('\n', '')
    list_vn_dict.append(char_vn_dict)

def vn_word_to_telex_type(word):
    dau_cau = 0
    new_word = ''
    for char in word:
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            new_word += char
            continue
        if y != 0:
            dau_cau = y
        new_word += bang_nguyen_am[x][-1]
    new_word += bang_ky_tu_dau[dau_cau]
    return new_word


def vn_sentence_to_telex_type(sentence):
    """
    Chuyển câu tiếng việt có dấu về kiểu gõ telex.
    :param sentence:
    :return:
    """
    words = sentence.split()
    for index, word in enumerate(words):
        words[index] = vn_word_to_telex_type(word)
    return ' '.join(words)


"""
    End section: Chuyển câu văn về kiểu gõ telex khi không bật Unikey
"""

"""
    Start section: Chuyển câu văn về cách gõ dấu kiểu cũ: dùng òa úy thay oà uý
    Xem tại đây: https://vi.wikipedia.org/wiki/Quy_t%E1%BA%AFc_%C4%91%E1%BA%B7t_d%E1%BA%A5u_thanh_trong_ch%E1%BB%AF_qu%E1%BB%91c_ng%E1%BB%AF
"""


def chuan_hoa_dau_tu_tieng_viet(word):
    if not is_valid_vietnam_word(word):
        return word

    chars = list(word)
    dau_cau = 0
    nguyen_am_index = []
    qu_or_gi = False
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            continue
        elif x == 9:  # check qu
            if index != 0 and chars[index - 1] == 'q':
                chars[index] = 'u'
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == 'g':
                chars[index] = 'i'
                qu_or_gi = True
        if y != 0:
            dau_cau = y
            chars[index] = bang_nguyen_am[x][0]
        if not qu_or_gi or index != 1:
            nguyen_am_index.append(index)
    if len(nguyen_am_index) < 2:
        if qu_or_gi:
            if len(chars) == 2:
                x, y = nguyen_am_to_ids.get(chars[1])
                chars[1] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                if x != -1:
                    chars[2] = bang_nguyen_am[x][dau_cau]
                else:
                    chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
            return ''.join(chars)
        return word

    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            return ''.join(chars)

    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
        else:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    return ''.join(chars)


def is_valid_vietnam_word(word):
    chars = list(word)
    # nguyen_am_index = -1
    # for index, char in enumerate(chars):
    #     x, y = nguyen_am_to_ids.get(char, (-1, -1))
    #     if x != -1:
    #         if nguyen_am_index == -1:
    #             nguyen_am_index = index
    #         else:
    #             if index - nguyen_am_index != 1:
    #                 return False
    #             nguyen_am_index = index
    # return True
    for char in chars:
        if char not in list_vn_dict:
            return False
    return True
    
def is_valid_vietnam_text(text):
    # Kiểm tra text đó chỉ có giá trị là tiếng việt không ?
    list_word = text.split()
    for word in list_word:
        if not is_valid_vietnam_word(word):
            return False
    return True

def chuan_hoa_dau_cau_tieng_viet(sentence):
    """
        Chuyển câu tiếng việt về chuẩn gõ dấu kiểu cũ.
        :param sentence:
        :return:
    """
    sentence = sentence.lower()
    words = sentence.split()
    for index, word in enumerate(words):
        cw = reg.sub(r'(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)', r'\1/\2/\3', word).split('/')
        # print(cw)
        if len(cw) == 3:
            cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = ''.join(cw)
    return ' '.join(words)


def clean_text(text):
    # chuyển hết html number -> unicode. Ví dụ &#236; -> ì
    text = html.unescape(text)
    # Loại bỏ hết thẻ html tag trong text
    text = re.sub(re.compile('<.*?>'), '', text)
    # Loại bỏ các đường dẫn link url không cần thiết trong bài toán
    text = re.sub(r'http\S+', '', text)
    # Loại bỏ kí tự đặc biệt \t, \n
    text = re.sub(r'\s+', ' ', text)
    # Loại bỏ các kí tự đặc biệt như ,.[],{},()|?#
    text = re.sub(r'[^\w]', ' ', text)
    
    text = text.lower()
    text = chuan_hoa_dau_cau_tieng_viet(text)
    
    list_word = text.split()
    text = ' '.join(list_word)
    return text


def clean_keyword(keyword: str, list_search_stopword, list_search_acronyms):
    """_summary_
        Làm sạch từ khóa tìm kiếm
    Args:
        keyword (str): keyword nhập vào 
        list_search_stopword (_type_): Danh sách từ khóa không cần thiết trong lúc tìm kiếm
        list_use_acroyms (_type_): Danh sách từ viết tắt - nghĩa của từ viết tắt
        list_city (_type_): Danh sách tỉnh thành
        list_quanhuyen (_type_)
        # Lọc một số từ nhiễu
    Returns:
        _type_: Kết quả trả về là keyword đã được làm sạch
    """
    
    # Decode url từ tìm kiếm trong trường hợp dạng mã khác
    keyword = unquote(keyword)
    keyword = fix_encoding(keyword)
    # Loại bỏ đi thẻ html tag trong keyword
    keyword = re.sub(re.compile('<.*?>'), '', keyword)
    # Loại bỏ đi số (chưa cần thiết)
    keyword = re.sub(r'[0-9]', '', keyword)
    
    # Kiểm tra xem keyword đó có phải từ việt nam hay không ??
    # if is_valid_vietnam_text(keyword):
    keyword = re.sub(r'[^\w]', ' ', keyword)
    # Chuyển hết chữ hoa về chữ thường
    
    list_word = keyword.split()
    keyword = ' '.join(list_word)
    keyword = keyword.lower()
    
    # # Bỏ đi các từ không cần thiết trong tìm kiếm
    for stopword in list_search_stopword:
        if stopword in keyword:
            keyword = keyword.replace(stopword, '')
            
    # Chuyển đổi từ viết tắt thành từ có nghĩa
    # Chuyển từ viết tắt thành từ hoàn chỉnh
    replaces = {}
    for word in list_word:
        if word in list_search_acronyms.keys():
            replaces[word] = list_search_acronyms[word]
                    
    for key, value in replaces.items():
        keyword_details = keyword.replace(key, value)
    
    # Sử dụng cả keyword có từ khóa và keyword không có từ khóa
    if replaces:    
        keyword_details = keyword_details.strip()      
        keyword = keyword.strip()    
        return [keyword_details, keyword]
    else:
        keyword = keyword.strip()
        return [keyword]


def no_accent_vietnamese(string):
    # Chuyển đổi từ tiếng việt có dấu sang tiếng việt không có dấu
    string = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', string)
    string = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', string)
    string = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', string)
    string = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', string)
    string = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', string)
    string = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', string)
    string = re.sub(r'[ìíịỉĩ]', 'i', string)
    string = re.sub(r'[ÌÍỊỈĨ]', 'I', string)
    string = re.sub(r'[ùúụủũưừứựửữ]', 'u', string)
    string = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', string)
    string = re.sub(r'[ỳýỵỷỹ]', 'y', string)
    string = re.sub(r'[ỲÝỴỶỸ]', 'Y', string)
    string = re.sub(r'[Đ]', 'D', string)
    string = re.sub(r'[đ]', 'd', string)
    return string


def search_stopword_arcnoyms(file_stopword, file_acronyms):
    """_summary_
        Lấy toàn bộ từ khóa viết tắt, từ dừng không cần thiết
    Args:
        file_stopword (_type_): File chứa các từ dừng
        file_acronyms (_type_): File chứa từ khóa viết tắt và nghĩa của từ khóa viết tắt
    """

    # Lưu từ khóa (danh sách từ không cần thiết) vào trong list
    search_stopword = []
    try:
        with open(file_stopword, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                search_stopword.append(line.replace('\n', '').lower())
        f.close()
    except FileNotFoundError:
        print('Please check the path job')
        
    # Lưu từ viết tắt vào file .json
    search_acronyms = {}
    try:
        with open(file_acronyms, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                # Loại bỏ đi kí tự xuống dòng
                line = line.replace('\n', '').lower()
                acronyms, mean_acronyms = line.split('#')
                search_acronyms[acronyms] = mean_acronyms
            f.close()
    except FileNotFoundError:
        print('Please check the path job')
        
        
    # Trả về kết quả
    return search_stopword, search_acronyms