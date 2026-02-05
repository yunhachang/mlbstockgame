import requests
import pandas as pd

players = {
    "660271": "Ohtani",
    "673490": "Kim",
    "543807": "Springer"
}

all_data = []

for p_id, p_name in players.items():
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            splits.sort(key=lambda x: x['date']) 
            
            t_h, t_hr, t_rbi, t_ab = 0, 0, 0, 0
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                t_h += s.get('hits', 0)
                t_hr += s.get('homeRuns', 0)
                t_rbi += s.get('rbi', 0)
                t_ab += s.get('atBats', 0)
                
                c_avg = t_h / t_ab if t_ab > 0 else 0
                
                # --- [기획 밸런싱: '지옥에서 온 페널티' 로직] ---
                
                # 1. 시가총액 (기본 체력)
                market_cap = (t_h * 50) + (t_hr * 500) + (t_rbi * 150)
                
                # 2. 타율 페널티 (지수 적용)
                # 기준 타율을 0.260으로 설정. 
                # (c_avg / 0.260)에 '3제곱'을 합니다. 
                # 이렇게 하면 0.260보다 조금만 낮아도 주가가 기하급수적으로 깎입니다!
                # 예: 타율 0.200이면 (0.200/0.260)^3 = 약 0.45 (누적치의 절반 이상이 날아감)
                form_multiplier = pow(c_avg / 0.260, 3) 
                
                # 3. 최종 주가: (기본 체력 * 무서운 멀티플라이어) + 기본 상장가
                price = int((market_cap * form_multiplier) + 1000)
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": max(price, 100), # 하한선을 100으로 낮춰 공포 극대화
                    "AVG": round(c_avg, 3)
                })
                
    except Exception as e:
        print(f"Error processing {p_name}: {e}")

if all_data:
    df = pd.DataFrame(all_data).sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("지수형 하락 로직 적용 완료! 이제 스프링어는 고전할 겁니다.")
