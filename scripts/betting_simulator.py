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
        # 1. 공격(타자) 기본 배당
        base_hitter = {
            'Single': 1.5, 'Double': 2.5, 'Triple': 4.0, 
            'Home Run': 6.0, 'Walk': 1.2, 'Hit By Pitch': 1.2
        }
        h_base = base_hitter.get(row['event'], 0)
        
        # 2. 수비(투수) 기본 배당 (아웃이면 1.2배)
        p_base = 1.2 if h_base == 0 else 0

        # [가중치] 점수차와 이닝 반영
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch_factor = 1.0 + (0.5 / (score_diff + 1))
        
        inning_weight = 1.0
        if row['inning'] >= 7:
            inning_weight = 1.0 + (row['inning'] - 6) * 0.2

        hitter_odds = round(h_base * clutch_factor * inning_weight, 2)
        pitcher_odds = round(p_base * clutch_factor * inning_weight, 2)

        return pd.Series([hitter_odds, pitcher_odds])

    df[['hitter_odds', 'pitcher_odds']] = df.apply(calculate_hybrid_odds, axis=1)
    df['payout_hitter'] = df['hitter_odds'] * 1000
    df['payout_pitcher'] = df['pitcher_odds'] * 1000

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    total_bets = len(df) * 1000
    
    # 리포트 생성
    report = f"""# 🏆 하이브리드 대결 시뮬레이션 리포트 ({now_str})

## 📊 공격(타자) vs 수비(투수) 밸런스 요약
| 구분 | 타자 배팅 (공격) | 투수 배팅 (수비) |
| :--- | :--- | :--- |
| **총 배팅액** | {total_bets:,} P | {total_bets:,} P |
| **총 환급액** | {df['payout_hitter'].sum():,.0f} P | {df['payout_pitcher'].sum():,.0f} P |
| **환급률(Return)** | {(df['payout_hitter'].sum()/total_bets)*100:.1f}% | {(df['payout_pitcher'].sum()/total_bets)*100:.1f}% |

## 🔥 주요 타석 결과 (상위 10개)
"""
    # 표 데이터 추가 (tabulate 에러 방지를 위해 간단한 방식으로 구현)
    top_10 = df.sort_values(by=['hitter_odds', 'pitcher_odds'], ascending=False).head(10)
    table_header = "| 이닝 | 타자 | 점수 | 결과 | 타자배당 | 투수배당 |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    table_rows = ""
    for _, r in top_10.iterrows():
        res = r['event'] if r['hitter_odds'] > 0 else "OUT"
        table_rows += f"| {r.inning}회 | {r.batter} | {r.score_home}:{r.score_away} | {res} | {r.hitter_odds}배 | {r.pitcher_odds}배 |\n"
    
    final_report = report + table_header + table_rows

    with open("data/simulation_report.md", "w", encoding="utf-8") as f:
        f.write(final_report)
    print("✅ 시뮬레이션 완료.")

if __name__ == "__main__":
    run_simulation()
