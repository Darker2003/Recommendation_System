import argparse
import json

from config import *


def main():
    parser = argparse.ArgumentParser(description='Load JSON data from a file.')
    parser.add_argument('file_path', nargs='?', default=DEFAULT_TEXT_ANNOTATION_FILE, type=str, help='Path to the text data annotation file')
    parser.add_argument('line_pass', nargs='?', default=5, type=int, help='How many line will be passed - not in the prompt')
    parser.add_argument('save_path', nargs='?', default=prompt_path, type=int, help='Saved prompt path')
    args = parser.parse_args()

    json_data = load_json_file(args.file_path)

    # Now, json_data contains the parsed JSON data as a Python dictionary
    # You can access its elements like you would with any Python dictionary
    # print(json_data)
    
    #Creat the prompt
    message = []
    message.append({"role": "system", "content": "You are a helpful assistant designed to output JSON."})
    message.append({"role": "system", "content": "Only follow general tags: ['ẨM THỰC', 'BÃI CỎ', 'BẠN BÈ', 'BẢO TÀNG', 'BẢO TỒN', 'BÍ ẨN', 'BIỂN', 'BIỂU DIỄN', 'BÌNH DÂN', 'BÌNH MINH', 'BƠI LỘI', 'CÀ PHÊ', 'CAO CẤP', 'CÁT', 'CẮM TRẠI', 'CẶP ĐÔI', 'CÂU CÁ', 'CHỢ', 'CHÙA', 'CHỤP ẢNH', 'CON ĐƯỜNG', 'CỔ XƯA', 'CỘNG ĐỒNG', 'CUỐI TUẦN', 'CỬA HÀNG', 'DÂN GIAN', 'DÂN TỘC', 'DI CHUYỂN', 'DI SẢN', 'DI TÍCH', 'DU LỊCH', 'ĐÁ', 'ĐẶC BIỆT', 'ĐẶC SẢN', 'ĐÈO', 'ĐẸP', 'ĐÊM', 'ĐỀN THỜ', 'ĐI BỘ', 'ĐỊA ĐIỂM', 'ĐỊA PHƯƠNG', 'ĐỘC ĐÁO', 'ĐỘNG VẬT', 'GIA ĐÌNH', 'HẢI SẢN', 'HANG ĐỘNG', 'HẤP DẪN', 'HIỆN ĐẠI', 'HOÀNG HÔN', 'HOANG SƠ', 'HOẠT ĐỘNG', 'HÒN ĐẢO', 'HỒ THỦY ĐIỆN', 'HỘI THẢO', 'HÙNG VĨ', 'KHÁCH SẠN', 'KHÓ QUÊN', 'KHOA HỌC', 'KIẾN TRÚC', 'LÀNG', 'LÀNG CHÀI', 'LÃNG MẠN', 'LẶN', 'LEO NÚI', 'LỄ HỘI', 'LỊCH SỬ', 'LƯỚT SÓNG', 'MẠO HIỂM', 'NGHỆ THUẬT', 'NGHỈ DƯỠNG (SPA)', 'NGOẠI Ô', 'NGOÀI TRỜI', 'NGON', 'NHÀ HÀNG', 'NHÀ NGHỈ', 'NHỘN NHỊP', 'NỔI TIẾNG', 'NÚI', 'PHONG CẢNH', 'PHƯỢT', 'QUẢNG TRƯỜNG', 'QUỐC TẾ', 'RESORT', 'SAN HÔ', 'SÂN BAY', 'SUỐI', 'SỰ KIỆN', 'TÂM LINH', 'THÁC NƯỚC', 'THÀNH PHỐ', 'THỂ THAO', 'THIÊN NHIÊN', 'THUYỀN', 'THƯ GIÃN', 'THƯỞNG THỨC', 'TOUR', 'TÔN GIÁO', 'TRẢI NGHIỆM', 'TRẺ EM', 'TRUYỀN THỐNG', 'TỰ TÚC', 'VĂN HÓA', 'VUI CHƠI', 'VƯỜN HOA', 'YÊN BÌNH', 'RIÊNG TƯ', 'CÔNG VIÊN']"})
    index = 0
    for data in json_data['annotations']:
        if index%args.line_pass == 0:
            message.append({"role": "user", "content": data[0]})
            message.append({"role": "assistant", "content": f'{data[1]}'})
        index += 1

    with open(prompt_path, 'w', encoding='utf-8') as file:
        json.dump(message, file, ensure_ascii=False)
        print(f"Save: {prompt_path}")
    
    
if __name__ == "__main__":
    main()
