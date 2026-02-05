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
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            
            t_hits, t_hr, t_rbi, t_ab = 0, 0, 0, 0
            
            for game in reversed(splits):
                date = game['date']
                t_hits += game['stat'].get('hits', 0)
                t_hr += game['stat'].get('homeRuns', 0)
                t_rbi += game['stat'].get('rbi', 0)
                t_ab += game['stat'].get('atBats', 0)
                
                cur_avg = t_hits / t_ab if t_ab > 0 else 0
                
                # --- [수정된 기획 로직] ---
                # 1. 누적 가속도 (Exponential Growth): 
                # 누적 안타가 많아질수록 가치가 더 가파르게 오릅니다.
                # (단순 합산이 아니라, 쌓인 데이터에 가산점을 더 줌)
                accumulation_value = (t_hits * 30) + (t_hr * 200) + (t_rbi * 50)
                
                # 2. 타율 보정 (안정 장치):
                # 타율이 깎여도 누적치를 다 갉아먹지 못하게 '더하기' 방식으로만 처리
                # 타율이 0.300이면 +1500점, 0.200이면 +1000점 식으로 '보너스 폭'만 조절
                avg_impact = cur_avg * 5000 
                
                # 3. 시간/경기수 가산점: 
                # 경기를 치를수록(누적 타수가 늘수록) 주가의 하한선(Floor) 자체가 높아집니다.
                consistency_bonus = t_ab * 5 
                
                # 최종 주가 계산
                price = int(1000 + accumulation_value + avg_impact + consistency_bonus)
                # -------------------------
                
                all_data.append({
                    "Date": date, "Player": p_name, "Price": price, "AVG": round(cur_avg, 3)
                })
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    new_df = pd.DataFrame(all_data)
    new_df = new_df.sort_values(by=['Player', 'Date'])
    new_df.to_csv('mlb_stock_history.csv', index=False)
    print("밸런싱 업데이트 완료!")
