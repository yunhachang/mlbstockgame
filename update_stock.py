import requests
import pandas as pd
import os

# 1. 상장 선수 리스트
players = {
    "660271": "Ohtani",
    "673490": "Kim"
}

all_data = []

for p_id, p_name in players.items():
    # MLB 공식 API 호출
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            
            total_hits = 0
            total_hr = 0
            total_rbi = 0
            total_at_bats = 0
            
            # 과거부터 순차 계산
            for game in reversed(splits):
                date = game['date']
                # API 데이터 추출 (Key 이름 주의: atBats)
                total_hits += game['stat'].get('hits', 0)
                total_hr += game['stat'].get('homeRuns', 0)
                total_rbi += game['stat'].get('rbi', 0)
                total_at_bats += game['stat'].get('atBats', 0) 
                
                # 누적 타율 계산
                current_avg = total_hits / total_at_bats if total_at_bats > 0 else 0
                
                # [주가 로직]
                growth_value = (total_hits * 20) + (total_hr * 100) + (total_rbi * 40)
                avg_bonus = (current_avg - 0.250) * 3000 
                
                price = int(1000 + growth_value + avg_bonus)
                price = max(price, 100) 
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": price,
                    "AVG": round(current_avg, 3)
                })
    except Exception as e:
        print(f"Error processing {p_name}: {e}")

# 2. 저장
if all_data:
    new_df = pd.DataFrame(all_data)
    new_df = new_df.sort_values(by=['Player', 'Date'])
    new_df.to_csv('mlb_stock_history.csv', index=False)
    print("성공적으로 업데이트되었습니다!")
else:
    print("데이터를 가져오지 못했습니다.")
