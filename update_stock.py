import requests
import pandas as pd

players = {
    "660271": "Ohtani",
    "673490": "Kim"
}

all_data = []

for p_id, p_name in players.items():
    # MLB gameLog API는 해당 경기 시점의 'season stats'를 이미 포함하고 있습니다.
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            
            # 과거부터 최신순으로 처리
            for game in reversed(splits):
                date = game['date']
                # 해당 경기 직후의 시즌 전체 누적 기록을 바로 가져옵니다.
                s = game['stat']
                accum_h = s.get('hits', 0)
                accum_hr = s.get('homeRuns', 0)
                accum_rbi = s.get('rbi', 0)
                accum_avg = float(s.get('avg', ".000")) # 당시 타율
                
                # --- [기획자님을 위한 '자본주의' 주가 로직] ---
                
                # 1. 시가총액 (누적의 힘): 안타/홈런이 쌓일수록 덩치가 커집니다.
                # 후반부로 갈수록 누적치가 커지므로 주가 하한선이 단단해집니다.
                market_cap = (accum_h * 50) + (accum_hr * 500) + (accum_rbi * 100)
                
                # 2. 실적 압박 (긴장감): 타율이 3할(.300)을 기준으로 주가를 곱합니다.
                # .300 이상이면 프리미엄, .250 이하면 주가가 무섭게 깎입니다.
                # (누적치가 커져도 타율이 폭락하면 주가도 같이 폭락하는 '곱하기' 로직 복구)
                performance_ratio = accum_avg / 0.280 
                
                # 3. 최종 주가 = (누적 가치 * 타율 비중) + 기본 상장가
                price = int((market_cap * performance_ratio) + 1000)
                # -------------------------------------------
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": max(price, 100),
                    "AVG": accum_avg
                })
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    new_df = pd.DataFrame(all_data)
    new_df = new_df.sort_values(by=['Player', 'Date'])
    new_df.to_csv('mlb_stock_history.csv', index=False)
    print("기획 로직 최종 적용 완료!")
