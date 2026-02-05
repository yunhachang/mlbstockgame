import requests
import pandas as pd

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
        
        # 누적 변수
        total_hits = 0
        total_hr = 0
        total_rbi = 0
        total_at_bats = 0 # 타수 (타율 계산용)
        
        # 과거부터 현재 순으로 계산
        for game in reversed(splits):
            date = game['date']
            total_hits += game['stat']['hits']
            total_hr += game['stat']['homeRuns']
            total_rbi += game['stat']['rbi']
            total_at_bats += game['stat']['atBats']
            
            # 현재 시점의 누적 타율 계산
            current_avg = total_hits / total_at_bats if total_at_bats > 0 else 0
            
            # [비즈니스 로직] 
            # 1. 기본 점수: 누적 성적 (우상향 요인)
            base_value = (total_hits * 10) + (total_hr * 100) + (total_rbi * 20)
            
            # 2. 승수 효과: 타율이 높으면 프리미엄, 낮으면 페널티 (하락 요인)
            # 기준 타율을 0.250으로 잡고, 그보다 높으면 가산점, 낮으면 감점
            multiplier = current_avg / 0.250 
            
            # 최종 주가 = (기본 점수 * 타율 승수) + 시작가 1000
            price = int((base_value * multiplier) + 1000)
            
            all_data.append({
                "Date": date,
                "Player": p_name,
                "Price": price,
                "AVG": round(current_avg, 3) # 확인용
            })

new_df = pd.DataFrame(all_data)
new_df.to_csv('mlb_stock_history.csv', index=False)
