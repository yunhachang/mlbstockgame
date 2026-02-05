import requests
import pandas as pd
import os

players = {
    "660271": "Ohtani",
    "673490": "Kim"
}

all_data = []

for p_id, p_name in players.items():
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    response = requests.get(url).json()
    
    if 'stats' in response and response['stats']:
        splits = response['stats'][0]['splits']
        
        # 누적 변수 초기화
        total_hits = 0
        total_hr = 0
        total_rbi = 0
        
        # 과거부터 현재 순으로 데이터가 오므로, 누적합 계산 가능
        for game in reversed(splits): # 최신순에서 과거순으로 올 경우 뒤집기
            date = game['date']
            total_hits += game['stat']['hits']
            total_hr += game['stat']['homeRuns']
            total_rbi += game['stat']['rbi']
            
            # 주가 산정식: (누적 안타*5) + (누적 홈런*20) + (누적 타점*10) + 기본가 1000
            # 누적이라 숫자가 커지므로 가중치를 조절했습니다.
            price = 1000 + (total_hits * 5) + (total_hr * 20) + (total_rbi * 10)
            
            all_data.append({
                "Date": date,
                "Player": p_name,
                "Price": price
            })

new_df = pd.DataFrame(all_data)
new_df.to_csv('mlb_stock_history.csv', index=False)
