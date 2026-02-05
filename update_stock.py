import requests
import pandas as pd
import os

# 1. 상장 선수 리스트 (ID: 이름)
players = {
    "660271": "Ohtani",
    "673490": "Kim"
}

all_data = []

for p_id, p_name in players.items():
    # MLB 공식 API: 선수의 게임별 로그 가져오기
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    response = requests.get(url).json()
    
    if 'stats' in response and response['stats']:
        splits = response['stats'][0]['splits']
        
        # 누적 변수 초기화
        total_hits = 0
        total_hr = 0
        total_rbi = 0
        total_at_bats = 0
        
        # 과거 데이터부터 순차적으로 계산 (그래프의 흐름을 만들기 위함)
        for game in reversed(splits):
            date = game['date']
            total_hits += game['stat']['hits']
            total_hr += game['stat']['homeRuns']
            total_rbi += game['stat']['rbi']
            total_at_bats += game['stat']['at_bats'] # 타수 추가
            
            # 현재 시점의 누적 타율 (0으로 나누기 방지)
            current_avg = total_hits / total_at_bats if total_at_bats > 0 else 0
            
            # --- [기획자님을 위한 밸런싱 로직] ---
            # A. 우상향 요인: 안타, 홈런, 타점이 쌓이면 주가는 계속 오릅니다.
            growth_value = (total_hits * 20) + (total_hr * 100) + (total_rbi * 40)
            
            # B. 변동(긴장감) 요인: 타율이 높으면 보너스, 낮으면 페널티
            # 타율 0.250을 기준으로 보너스 점수가 위아래로 움직입니다.
            avg_bonus = (current_avg - 0.250) * 3000 
            
            # C. 최종 주가 계산
            # 기본가 1000원에 성장치와 타율 보너스를 합산합니다.
            # 타율이 너무 낮아도 주가가 마이너스가 되지 않도록 최소 100원을 보장합니다.
            price = int(1000 + growth_value + avg_bonus)
            price = max(price, 100) 
            # ---------------------------------------
            
            all_data.append({
                "Date": date,
                "Player": p_name,
                "Price": price,
                "AVG": round(current_avg, 3)
            })

# 2. 데이터 프레임 생성 및 저장
new_df = pd.DataFrame(all_data)

# 날짜와 선수별로 정렬하여 저장
new_df = new_df.sort_values(by=['Player', 'Date'])
new_df.to_csv('mlb_stock_history.csv', index=False)

print("주가 업데이트 완료!")
