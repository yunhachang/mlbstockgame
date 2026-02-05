import requests
import pandas as pd

players = {"660271": "Ohtani", "673490": "Kim"}
all_data = []

for p_id, p_name in players.items():
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            # 1. 데이터를 먼저 리스트로 받아서 날짜순으로 뒤집기
            splits = response['stats'][0]['splits']
            splits.sort(key=lambda x: x['date']) # 날짜 오름차순 정렬 (중요!)
            
            c_hits, c_hr, c_rbi, c_ab = 0, 0, 0, 0
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                # 누적 데이터 갱신
                c_hits += s.get('hits', 0)
                c_hr += s.get('homeRuns', 0)
                c_rbi += s.get('rbi', 0)
                c_ab += s.get('atBats', 0)
                c_avg = c_hits / c_ab if c_ab > 0 else 0
                
                # 2. [주가 로직] 우상향을 보장하는 누적 가치 산정
                # 누적 성적이 쌓일수록 베이스 점수가 강력하게 상승합니다.
                base_value = (c_hits * 50) + (c_hr * 500) + (c_rbi * 100)
                
                # 3. [긴장감] 타율이 높으면 추가 보너스, 낮으면 보너스 반납 (하지만 베이스는 유지)
                # 곱하기가 아닌 '더하기' 방식을 써서 우하향을 방어합니다.
                avg_bonus = (c_avg * 5000) 
                
                # 최종 주가 = 기본 1000 + 누적치 + 타율보너스 + 타수(경험치)
                price = int(1000 + base_value + avg_bonus + (c_ab * 10))
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": price,
                    "AVG": round(c_avg, 3)
                })
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    new_df = pd.DataFrame(all_data)
    # 마지막으로 한 번 더 날짜와 선수별 정렬
    new_df = new_df.sort_values(by=['Player', 'Date'])
    new_df.to_csv('mlb_stock_history.csv', index=False)
    print("날짜 정렬 및 우상향 로직 적용 완료!")
