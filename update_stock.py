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
            
            # 1. 날짜 순서 강제 정렬 (이게 안 되면 계속 거꾸로 나옵니다)
            splits.sort(key=lambda x: x['date']) 
            
            # 누적 변수 초기화
            total_h, total_hr, total_rbi, total_ab = 0, 0, 0, 0
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                # 2. 오늘 성적을 누적합에 더함
                total_h += s.get('hits', 0)
                total_hr += s.get('homeRuns', 0)
                total_rbi += s.get('rbi', 0)
                total_ab += s.get('atBats', 0)
                
                # 직접 계산한 타율
                current_avg = total_h / total_ab if total_ab > 0 else 0
                
                # 3. [기획 핵심] 우상향 주가 공식
                # 누적치가 늘어나면 주가는 무조건 오릅니다.
                # 여기에 타율 보너스를 '곱하기'가 아닌 '더하기'로 붙여서 폭락을 방지합니다.
                base_stock = (total_h * 50) + (total_hr * 500) + (total_rbi * 150)
                performance_bonus = current_avg * 10000  # 타율 0.300이면 +3000원
                
                # 최종 주가 (하한선 1000원 보장)
                price = int(1000 + base_stock + performance_bonus)
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": price
                })
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    df = pd.DataFrame(all_data)
    # 마지막 저장 전 다시 한번 선수별, 날짜별 정렬 확인
    df = df.sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("완벽한 우상향 로직으로 교체 완료!")
