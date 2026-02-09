import pandas as pd
from datetime import datetime
import os

def run_simulation():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path):
        print("데이터 파일이 없습니다.")
        return

    df = pd.read_csv(data_path)

    def calculate_hybrid_odds(row):
        # 1. 공격(타자) 배당 로직
        base_hitter = {
            'Single': 1.5, 'Double': 2.5, 'Triple': 4.0, 
            'Home Run': 6.0, 'Walk': 1.2, 'Hit By Pitch': 1.2
        }
        hitter_event = base_hitter.get(row['event'], 0)
        
        # 2. 수비(투수) 배당 로직 (아웃 상황일 때)
        # 기본적으로 아웃은 안타보다 자주 일어나므로 배당이 낮음 (1.2배)
        is_out = 1 if hitter_event == 0 else 0
        pitcher_event = 1.2 if is_out == 1 else 0

        # [공통 가중치] 긴장감 지수
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch_factor = 1.0 + (0.5 / (score_diff + 1)) # 박빙일수록 상승
        
        inning_weight = 1.0
        if row['inning'] >= 7:
            inning_weight = 1.0 + (row['inning'] - 6) * 0.2 # 후반일수록 상승

        # 3. 최종 배당 결정
        # 타자 배팅 시 받을 배당
        hitter_odds = round(hitter_event * clutch_factor * inning_weight, 2)
        # 투수 배팅 시 받을 배당
        pitcher_odds = round(pitcher_event * clutch_factor * inning_weight, 2)

        return pd.Series([hitter_odds, pitcher_odds])

    # 시뮬레이션 적용
    df[['hitter_odds', 'pitcher_odds']] = df.apply(calculate_hybrid_odds, axis=1)
    
    # 모든 타석에 1,000P씩 각각 걸었다고 가정 (분산 투자 시뮬레이션)
    df['payout_hitter'] = df['hitter_odds'] * 1000
    df['payout_pitcher'] = df['pitcher_odds'] * 1000

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    total_bets = len(df) * 1000
    
    report = f"""# 🏆 하이브리드 대결 시뮬레이션 리포트 ({now_str})

## 📊 공격(타자) vs 수비(투수) 밸런스 요약
| 구분 | 타자 배팅 (공격) | 투수 배팅 (수비) |
| :--- | :--- | :--- |
| **총 배팅액** | {total_bets:,} P | {total_bets:,} P |
| **총 환급액** | {df['payout_hitter'].sum():,.0f
