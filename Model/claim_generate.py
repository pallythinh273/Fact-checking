import json
import requests
import os
import time
from pprint import pprint
import json

def get_api_query(token, bot_id, query) -> json: 
    COZE_URL = 'https://api.coze.com/open_api/v2/chat'

    COZE_HEADERS = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': '*/*',
    }
       
    data = json.dumps({
        "conversation_id": "CongGpt",
        "bot_id": bot_id, # id TK 
        "user": "Co_test",
        "query": query,
        "stream": False
    })
                
    resp = requests.post(COZE_URL, data=data, headers=COZE_HEADERS)  
    
    return resp.json()   


def generate_claims(data_content_path, data_claims_path, TOKEN, BOT_ID):
    print(f"TOKEN: {TOKEN}, BOT_ID: {BOT_ID}")
    with open(data_content_path, 'r') as f:
        data_content = json.load(f)

    with open(data_claims_path, 'r') as fp:
        data_claims = json.load(fp)
    
    all_id = list(data_content.keys())
    id_ignore = list(data_claims.keys())
    id_get = [key for key in all_id if key not in id_ignore]
    
    nums_token = 0
    
    for item in id_get:
        print(f"### content id: {item} ###")
        try:            
            query = f"context: {data_content[item]['context']}"

            results = get_api_query(TOKEN, BOT_ID, query)
                                
            # print(results)
                
            if 'messages' in results.keys():
                nums_token += 1
                print(f"--- Số quota đã sử dụng: {nums_token} ---")

                string_claims = results['messages'][0]['content']
                    
                print(string_claims)
                
                data_claims[item] = string_claims 
                    
                print(f"!!! Đã thêm nội dung cho id = '{item}' !!!\n")
                    
                with open(data_claims_path, 'w', encoding='utf-8') as fp:
                    json.dump(data_claims, fp, ensure_ascii=False, indent=4)
            else:
                print("!!! HẾT  QUOTA !!!\n")
                break
        except:
            continue    

start_time = time.time()

with open('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/bot_info.json', 'r') as f:
    token = json.load(f)
    
for key, value in token.items():    
    generate_claims('/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/merged_data_file.json',
                  '/Users/tranhuuchicong/Documents/Hoc_tap/HK2_2023-2024/kltn/thesis/data/all_claim_generate_v2.json',
                  key,
                  value['bot_id']
                  )

end_time = time.time()
elapsed_time = end_time - start_time
pprint(f"Elapsed time: {int(elapsed_time // 3600)}h:{int((elapsed_time % 3600) // 60)}m:{(elapsed_time % 60):.2f}s")
    

    
