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
            
            # 0. 누적을 직접 계산하기 위해 변수 설정
            c_hits, c_hr, c_rbi, c_ab = 0, 0, 0, 0
            
            # 과거(시즌 초)부터 최신순으로 정렬하여 누적합 계산
            for game in reversed(splits):
                date = game['date']
                s = game['stat']
                
                # 그날의 성적을 계속 더해줌 (확실한 누적)
                c_hits += s.get('hits', 0)
                c_hr += s.get('homeRuns', 0)
                c_rbi += s.get('rbi', 0)
                c_ab += s.get('atBats', 0)
                c_avg = c_hits / c_ab if c_ab > 0 else 0
                
                # --- [기획자님을 위한 '황금 밸런스' 로직] ---
                # 1. 시가총액 (기초 체력): 누적이 될수록 무조건 커짐
                # 가중치를 높여서 시즌 후반으로 갈수록 덩치가 커지게 함
                base_power = (c_hits * 100) + (c_hr * 1000) + (c_rbi * 200)
                
                # 2. 시장 지수 (타율 비중): 
                # 단순히 나누는게 아니라, 0.250을 기준으로 '가산/감산' 비율 적용
                # 타율이 높으면 최대 2배까지 증폭, 낮으면 0.5배까지 축소
                performance_multiplier = 0.5 + (c_avg / 0.500) 
                
                # 3. 최종 주가: (기본 체력 * 타율 지수) + 기본가
                price = int((base_power * performance_multiplier) + 1000)
                # ------------------------------------------
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": max(price, 1000), # 하한선 1000원 설정
                    "AVG": round(c_avg, 3)
                })
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    new_df = pd.DataFrame(all_data)
    new_df = new_df.sort_values(by=['Player', 'Date'])
    new_df.to_csv('mlb_stock_history.csv', index=False)
    print("오타니 우상향 로직 적용 완료!")
