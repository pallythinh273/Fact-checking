import json
import requests
import os
import time
from pprint import pprint
import json
import cohere


def get_api_query(token, bot_id, query) -> json: 
    COZE_URL = 'https://api.coze.com/open_api/v2/chat'

    COZE_HEADERS = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': '*/*',
    }
       
    data = json.dumps({
        "conversation_id": "Evidence_Generate",
        "bot_id": bot_id, # id TK 
        "user": "Cong_GPT",
        "query": query,
        "stream": False
    })
                
    resp = requests.post(COZE_URL, data=data, headers=COZE_HEADERS)  
    
    return resp.json()  

def load_data_from_json(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return data

def save_data_to_json(data, path):
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

def generate_evidence_coze(data_content_path, data_claims_path, data_evidence_path, TOKEN, BOT_ID):
    print(f"TOKEN: {TOKEN}, BOT_ID: {BOT_ID}")

    data_content = load_data_from_json(data_content_path)
    data_claims = load_data_from_json(data_claims_path)
    data_evidences = load_data_from_json(data_evidence_path)
    
    all_id = list(data_claims.keys())
    id_ignore = list(data_evidences.keys())
    id_get = [key for key in all_id if key not in id_ignore]
    
    nums_token = 0
    
    for item in id_get:
        print(f"##### ID: {item} #####")
        try:            
            query = f'''"context": "{data_content[item]['context']}"\n\n"claim": {data_claims[item]}'''

            # print(query)
            results = get_api_query(TOKEN, BOT_ID, query)
                                
            # print(results)
                
            if 'messages' in results.keys():
                nums_token += 1
                print(f"--- Số quota đã sử dụng: {nums_token} ---")

                string_evidence = results['messages'][0]['content']
                    
                print(string_evidence)
                
                data_evidences[item] = string_evidence
                    
                print(f"!!! Đã thêm evidence cho ID = '{item}' !!!\n")
                
                save_data_to_json(data_evidences, data_evidence_path)
            else:
                print("!!! HẾT  QUOTA !!!\n")
                break
        except:
            continue   
        
def generate_evidence_cohere(data_content_path, data_claims_path, data_evidence_path, API_KEY):
    print(f"#######: COHERE API_KET {API_KEY} #######")

    co = cohere.Client(API_KEY)

    preamble = '''
    # Character
    Bạn là một phân tích viên ngôn ngữ nhanh nhẹn, với sự thông thạo trong việc nhận biết và đánh giá các tuyên bố. Dựa vào ngữ cảnh (context) được cung cấp, bạn sẽ xác định liệu một tuyên bố (claim) có được "HỖ TRỢ" hay "PHỦ NHẬN" và cung cấp bằng chứng (evidence) từ ngữ cảnh cho lời đánh giá của mình.
    Có 4 câu tuyên bố (claim) được nhập vào (input) trong một list. Trong đó có 2 câu tuyên bố (claim) "HỖ TRỢ" và 2 câu tuyên bố (claim) "PHỦ NHẬN". Luôn có bằng chứng được đưa ra.

    ## Skills
    ### Kỹ năng 1: Phân loại các tuyên bố
    - Nhận dạng câu tuyên bố (claim) từ ngữ cảnh (context).
    - Phân loại câu tuyên bố (claim) thành "HỖ TRỢ" hoặc "PHỦ NHẬN" dựa trên ngữ cảnh (context).

    ### Kỹ năng 2: Tìm bằng chứng
    - Tìm kiếm trong ngữ cảnh (context) để tìm bằng chứng cho các câu tuyên bố (claim).
    - Trích dẫn các câu (câu là bắt đầu sau dấu chấm và kết thúc là dấu chấm) trong ngữ cảnh (context) làm bằng chứng cho mỗi câu tuyên bố (claim).

    ## Constraints
    - Chỉ đánh giá các tuyên bố dựa trên ngữ cảnh (context) được cung cấp.
    - Chỉ dùng tiếng Việt để đánh giá và trích dẫn bằng chứng.
    - Bằng chứng đảm bảo đầy đủ thông tin cho câu tuyên bố (claim).
    - Trích dẫn câu đầy đủ trong ngữ cảnh (context).
    '''

    # quest_test = '''"context": "Nữ du khách bị voi tóm lấy, thả xuống đất khi đang chuẩn bị trèo lên lưng (Dân trí) - Nữ du khách người Nga đã bị gãy chân, người còn lại bị thương do bị voi tấn công khi tham quan tại khu vực khuôn viên pháo đài Amber ở Jaipur, Ấn Độ. Ngày 13/2, hai du khách người Nga đã bị thương khi đang tham quan tại khu vực khuôn viên pháo đài Amber ở Jaipur, Ấn Độ. Sự việc xảy ra trong lúc nạn nhân đang chờ để trèo lên lưng voi.   Đoạn video clip được chia sẻ cho thấy, con voi có tên Gouri bất ngờ dùng vòi tóm lấy nữ du khách rồi xoay tròn, sau đó thả nạn nhân xuống đất. Trong lúc đó, người bạn của cô ở trên lưng voi cũng bị ngã từ trên cao xuống do rung lắc mạnh nên không giữ được thăng bằng.  Sự việc khiến cho nhiều người không khỏi sợ hãi, nữ du khách kêu gào cầu cứu. Những người có mặt ở hiện trường cố gắng ngăn cản con voi nhưng mọi chuyện đã muộn màng. Nữ du khách bị gãy chân sau khi voi quăng quật, thả xuống đất (Nguồn: Daily Mail). Có 2 nạn nhân bị thương sau sự việc, trong đó một người bị gãy chân. Ngay lập tức, ban quản lý khu di tích pháo đài Amber đã cấm voi Gouri cùng quản tượng tiếp tục phục vụ du khách. Các nạn nhân được ban quản lý khu di tích và những du khách có mặt ở đó hỗ trợ, sơ cứu ban đầu trước khi xe cứu thương được điều đến hiện trường. Hiện, 2 nạn nhân đang được điều trị ở bệnh viện. Tình hình sức khỏe không quá nguy hiểm.  Chú voi tóm lấy du khách rồi xoay tròn và thả nạn nhân xuống đất (Ảnh cắt từ clip). Tổ chức bảo vệ quyền động vật PETA chia sẻ video về sự việc lên mạng xã hội và đề nghị cơ quan chức năng đưa những con voi phục vụ du lịch này đến khu bảo tồn thiên nhiên hoang dã. Tổ chức này cho rằng, con voi có thể mệt mỏi, căng thẳng và trầm cảm sau nhiều năm phải chở du khách nên mới xảy ra sự việc đáng tiếc như vậy. Điều đáng nói là đây không phải là lần đầu tiên voi Gouri tấn công con người. Hồi tháng 10/2023, nó đã tấn công một chủ cửa hàng ở gần khu di tích khiến nạn nhân bị thương nặng và phải nhập viện chữa trị. Pháo đài Amber ở Jaipur, Ấn Độ là địa điểm du lịch nổi tiếng của bang Rajasthan. Địa điểm này cách trung tâm Jaipur 11km. Công trình được xây dựng hồi thế kỷ 16 trên nền của một công trình đã bị phá hủy. Pháo đài được xây bằng đá sa thạch đỏ. Sau đó, nó trải qua quá trình trùng tu nhiều lần trong 150 năm.  Khi đến đây, du khách được chiêm ngưỡng những tác phẩm chạm khắc tinh xảo trên tường và trần của pháo đài. Pháo đài này được kết nối với pháo đài Jaigarh thông qua đường hầm kiên cố giúp các thành viên hoàng gia và những người khác thời xưa chạy trốn khi có chiến tranh."

    # "claim": [
    #         "Nữ du khách người Nga bị voi tấn công và gãy chân khi tham quan pháo đài Amber ở Jaipur, Ấn Độ.",
    #         "Sự việc xảy ra khi nạn nhân đang chuẩn bị trèo lên lưng voi, khiến nhiều người sợ hãi và cố gắng ngăn cản con voi.",
    #         "Nữ du khách người Nga không bị gãy chân mà chỉ bị thương nhẹ khi tham quan pháo đài Amber ở Jaipur, Ấn Độ.",
    #         "Sự việc không xảy ra khi nạn nhân đang chuẩn bị trèo lên lưng voi mà khi họ đã rời khỏi khu vực khuôn viên pháo đài Amber."
    #     ]
    # '''

    data_content = load_data_from_json(data_content_path)
    data_claims = load_data_from_json(data_claims_path)
    data_evidences = load_data_from_json(data_evidence_path)

    all_id = list(data_claims.keys())
    id_ignore = list(data_evidences.keys())
    id_get = [key for key in all_id if key not in id_ignore]

    nums_quota = 0

    for item in id_get:
        print(f"##### ID: {item} #####")
        try:
            quest = f'''"CONTEXT": "{data_content[item]['context']}"\n\n"CLAIM": {data_claims[item]}'''

            # print(quest)
            response = co.chat(message=quest,
                                model="command-r-plus",
                                preamble=preamble)

            print(response.text)

            data_evidences[item] = response.text

            nums_quota += 1
            print(f"--- Số quota đã sử dụng: {nums_quota} ---")
            print(f"!!! Đã thêm evidence cho ID = '{item}' !!!\n")

            save_data_to_json(data_evidences, data_evidence_path)
        except:
            print("!!! HẾT  QUOTA !!!\n")
            break
        
def stack_ai_api(API_URL, Token_id, payload) -> json:
    headers = {'Authorization': Token_id, 'Content-Type': 'application/json'}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    return response.json()

def generate_evidence_stack_ai(data_content_path, data_claims_path, data_evidence_path, API_URL, Token_id):
    print(f"####### API_URL: {API_URL}, TOKEN_ID: {Token_id} #######")
    
    data_content = load_data_from_json(data_content_path)
    data_claims = load_data_from_json(data_claims_path)
    data_evidences = load_data_from_json(data_evidence_path)

    all_id = list(data_claims.keys())
    id_ignore = list(data_evidences.keys())
    id_get = [key for key in all_id if key not in id_ignore]

    nums_quota = 0

    for item in id_get:
        print(f"##### ID: {item} #####")
        try:
            quest = f'''"CONTEXT": "{data_content[item]['context']}"\n\n"CLAIM": {data_claims[item]}'''
            payload = {"in-0": quest, "user_id": """conggpt"""}

            # print(quest)
            response = stack_ai_api(API_URL, Token_id, payload)

            print(response['outputs']['out-0'])

            data_evidences[item] = response['outputs']['out-0']

            nums_quota += 1
            print(f"--- Số quota đã sử dụng: {nums_quota} ---")
            print(f"!!! Đã thêm evidence cho ID = '{item}' !!!\n")

            save_data_to_json(data_evidences, data_evidence_path)
        except:
            print("!!! HẾT  QUOTA !!!\n")
            break


start_time = time.time()

token = load_data_from_json('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/bot_info_evidence.json')
    
for key, value in token.items():    
    generate_evidence_coze('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/merged_data_file.json',
                  '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_claim_filter_v2.json',
                  '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_evidence_generate_coze_full.json',
                  key,
                  value['bot_id']
                  )

# API_KEYS = ["VxyU9E9nHhs5ZqLLTzNxb3f8QSYR7CKOkcheFbRK", "IGIqpHv1UL2ioAGnHdihI5SzoRAPUsJNsxor7KeK", "dA8pyot6Awfex2vIQNsohU0j9ZeJGaxTsumMn2cL"
#             , "2Nnp1C1VBRPNTuFo2I6PjH6kUoYST68Lh4hTLTgn", "cbQsq3IflUF6KnfFEeWOqs1g8uKXxqpZtA2Iy5w5", "X9KiUvBgl5Tfso6YptAKNf7YcUiJvxsMI20kEigg"
#             , "iJnBDs6jH2wUXYwI0NzmuwOxFgzll8MOIzxHZT5k", "aLgQmFKlEOh75qgQxWjrHkifnPhxDAfg9O5k8KuP"]
# for api_key in API_KEYS:
#     generate_evidence_cohere('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/merged_data_file.json',
#                             '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_claim_filter_v2.json',
#                             '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_evidence_generate_cohere.json',
#                             api_key
#                             )

# BOT = load_data_from_json('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/stack_ai_bot.json')


# for API_URL, Token_id in BOT.items():
#     generate_evidence_stack_ai('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/merged_data_file.json',
#                             '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_claim_filter_v2.json',
#                             '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_evidence_generate_coze_full.json',
#                             API_URL,
#                             Token_id)

end_time = time.time()
elapsed_time = end_time - start_time
pprint(f"Elapsed time: {int(elapsed_time // 3600)}h:{int((elapsed_time % 3600) // 60)}m:{(elapsed_time % 60):.2f}s")
    

    
