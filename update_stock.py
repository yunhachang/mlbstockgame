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
            
            # 상장가 10,000원에서 시작
            current_price = 10000
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                h = s.get('hits', 0)
                hr = s.get('homeRuns', 0)
                rbi = s.get('rbi', 0)
                avg = float(s.get('avg', 0)) # 시즌 타율
                
                # --- [기획 밸런싱: '기대치 허들' 로직] ---
                
                # 1. 일일 기본 하락 (기대치 유지 비용)
                # 매 경기마다 주가는 기본적으로 -300원씩 하락합니다. (공짜 상향 방지)
                change = -300
                
                # 2. 성과 보너스
                # 안타를 치면 하락분을 상쇄하고 주가를 올립니다.
                # 홈런은 강력한 '상한가' 요인입니다.
                change += (h * 200) + (hr * 800) + (rbi * 100)
                
                # 3. 타율 페널티 (냉혹한 잣대)
                # 시즌 타율이 0.250 미만인 선수는 매 경기 추가로 -200원 감점
                if avg < 0.250:
                    change -= 200
                
                # 4. 주가 갱신 (어제 가격 + 오늘의 변동분)
                current_price += change
                
                # 5. 하한선 방어
                current_price = max(current_price, 500)
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": int(current_price)
                })
                
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    df = pd.DataFrame(all_data).sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("허들 누적 로직 적용 완료!")
