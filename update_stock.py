import requests
import pandas as pd
from datetime import datetime
import os

# 1. 상장 선수 명단 (ID: 이름)
players = {
    "660271": "Ohtani",
    "673490": "Kim"
}

all_data = []

# 기존 데이터 로드 (파일이 있으면 읽어옴)
file_name = 'mlb_stock_history.csv'
if os.path.exists(file_name):
    old_df = pd.read_csv(file_name)
else:
    old_df = pd.DataFrame()

for p_id, p_name in players.items():
    # 2. MLB API 호출 (2024년 정규시즌 성적)
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    response = requests.get(url).json()
    
    if 'stats' in response and response['stats']:
        splits = response['stats'][0]['splits']
        for game in splits:
            date = game['date']
            hits = game['stat']['hits']
            hr = game['stat']['homeRuns']
            rbi = game['stat']['rbi']
            
            # 주가 산정식: (안타*10) + (홈런*50) + (타점*20) + 기본가 100
            price = 100 + (hits * 10) + (hr * 50) + (rbi * 20)
            
            all_data.append({
                "Date": date,
                "Player": p_name,
                "Price": price
            })

# 3. 데이터 통합 및 중복 제거
new_df = pd.DataFrame(all_data)
combined_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['Date', 'Player'], keep='last')
combined_df = combined_df.sort_values(by=['Player', 'Date'])

# 4. 저장
combined_df.to_csv(file_name, index=False)
