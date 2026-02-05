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
            
            # 주가 초기값 5,000원에서 시작 (변동성을 보여주기 위함)
            current_price = 5000
            t_h, t_ab = 0, 0
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                hits = s.get('hits', 0)
                hr = s.get('homeRuns', 0)
                rbi = s.get('rbi', 0)
                
                # --- [기획 밸런싱: '냉혹한 실적주의' 로직] ---
                
                # 1. 일일 유지비 (Time Decay)
                # 아무것도 안 해도 매일 주가가 200원씩 하락합니다. (기대치 반영)
                current_price -= 200
                
                # 2. 실적 보상
                # 안타 하나당 150원, 홈런은 1000원, 타점은 300원 추가
                daily_gain = (hits * 150) + (hr * 1000) + (rbi * 300)
                current_price += daily_gain
                
                # 3. 타율 페널티 (현재 폼)
                # 그날 안타를 못 치면(0안타) 추가로 300원을 더 깎습니다.
                if hits == 0:
                    current_price -= 300
                
                # 4. 상한/하한선 설정
                current_price = max(current_price, 500)  # 최소 500원
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": int(current_price)
                })
                
    except Exception as e:
        print(f"Error processing {p_name}: {e}")

if all_data:
    df = pd.DataFrame(all_data).sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("실적주의 하락 로직 적용 완료!")
