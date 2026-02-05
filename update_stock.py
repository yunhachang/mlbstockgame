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
            
            # 1. 과거 데이터부터 순차 처리 (반드시 정렬)
            splits.sort(key=lambda x: x['date']) 
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                # API가 제공하는 '해당 경기 시점'의 시즌 누적 데이터
                # (우리가 직접 더하는 게 아니라 MLB 공식 기록을 그대로 사용)
                season_h = s.get('hits', 0)
                season_hr = s.get('homeRuns', 0)
                season_rbi = s.get('rbi', 0)
                # 타율이 문자열(".250")로 올 수 있어 변환 처리
                try:
                    season_avg = float(s.get('avg', 0))
                except:
                    season_avg = 0
                
                # --- [기획 밸런싱: '냉혹한 성적표' 로직] ---
                # 누적 안타/홈런이 아무리 많아도 타율이 낮으면 점수가 '폭락'하게 설계
                # 타율 0.260 미만은 '낙제점'으로 취급하여 가치를 깎습니다.
                
                base_score = (season_h * 10) + (season_hr * 200) + (season_rbi * 30)
                
                # 타율 보정 (지수함수 사용: 타율이 조금만 낮아도 점수가 처참해짐)
                # 0.300 타자는 1.5배 보너스, 0.200 타자는 0.3배로 토막
                performance_ratio = pow(season_avg / 0.260, 4) 
                
                price = int((base_score * performance_ratio) + 1000)
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": max(price, 500)
                })
                
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    df = pd.DataFrame(all_data).sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("절대평가 로직 적용 완료! 이제 Springer는 살아남지 못합니다.")
