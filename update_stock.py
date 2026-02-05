import requests
import pandas as pd

players = {"660271": "Ohtani", "673490": "Kim"}
all_data = []

for p_id, p_name in players.items():
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            
            # 1. 날짜순 정렬 (과거 -> 최신)
            splits.sort(key=lambda x: x['date']) 
            
            total_h, total_hr, total_rbi = 0, 0, 0
            prev_price = 1000  # 상장가 1000원 시작
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                # 2. 성적 누적 (이 수치는 절대 줄어들지 않음)
                h = s.get('hits', 0)
                hr = s.get('homeRuns', 0)
                rbi = s.get('rbi', 0)
                
                total_h += h
                total_hr += hr
                total_rbi += rbi
                
                # 3. 주가 산정: [오늘의 활약 점수]
                # 안타치면 오르고, 홈런치면 폭등합니다. 못하면 0점이지만 '감점'은 없습니다.
                daily_score = (h * 50) + (hr * 300) + (rbi * 100)
                
                # 4. 핵심 로직: [어제 주가 + 오늘 점수]
                # 이 방식은 수학적으로 절대 우하향할 수 없습니다. (전고점 돌파형)
                current_price = prev_price + daily_score
                
                # 보너스: 안타 못 친 날은 주가가 유지되거나 아주 미세하게(+1)만 오름
                if daily_score == 0:
                    current_price = prev_price + 1 
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": current_price
                })
                
                # 내일 계산을 위해 오늘 주가를 저장
                prev_price = current_price
                
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv('mlb_stock_history.csv', index=False)
    print("경제 부흥 로직 적용 완료! 이제 하락은 없습니다.")
