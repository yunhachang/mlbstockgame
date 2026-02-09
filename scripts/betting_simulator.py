import pandas as pd
from datetime import datetime
import os

def run_simulation():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path):
        print("데이터 파일이 없습니다.")
        return

    df = pd.read_csv(data_path)

    def calculate_dynamic_margin_odds(row):
        # 1. 타자 기본 배당 (기존보다 아주 살짝 하향하여 밸런스 조정)
        base_hitter = {
            'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 
            'Home Run': 5.5, 'Walk': 1.1, 'Hit By Pitch': 1.1
        }
        h_base = base_hitter.get(row['event'], 0)
        
        # 2. 투수 기본 배당 (1.2 -> 1.05로 하향: 아웃은 매우 흔하므로)
        p_base = 1.05 if h_base == 0 else 0

        # [가중치 계산]
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch_factor = 1.0 + (0.5 / (score_diff + 1))
        
        inning_weight = 1.0
        if row['inning'] >= 7:
            inning_weight = 1.0 + (row['inning'] - 6) * 0.2

        # 3. 동적 마진 적용 (Dynamic Margin)
        # 타자는 가중치를 100% 적용하여 '대박' 가능성 유지
        hitter_odds = round(h_base * clutch_factor * inning_weight, 2)
        
        # 투수는 가중치 영향력을 40%로 줄여서 환급률 폭주 방지 (시스템 마진 확보)
        pitcher_clutch = 1.0 + ((clutch_factor - 1.0) * 0.4)
        pitcher_inning = 1.0 + ((inning_weight - 1.0) * 0.4)
        pitcher_odds = round(p_base * pitcher_clutch * pitcher_inning, 2)

        return pd.Series([hitter_odds, pitcher_odds])

    df[['hitter_odds', 'pitcher_odds']] = df.apply(calculate_dynamic_margin_odds, axis=1)
    df['payout_hitter'] = df['hitter_odds'] * 1000
    df['payout_pitcher'] = df['pitcher_odds'] * 1000

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    total_bets = len(df) * 1000
    
    # 리포트 생성
    report = f"""# 📉 동적 마진(Dynamic Margin) 적용 리포트 ({now_str})

## 📊 밸런스 최적화 요약
| 구분 | 타자 배팅 (공격) | 투수 배팅 (수비) |
| :--- | :--- | :--- |
| **총 배팅액** | {total_bets:,} P | {total_bets:,} P |
| **총 환급액** | {df['payout_hitter'].sum():,.0f} P | {df['payout_pitcher'].sum():,.0f} P |
| **환급률(Return)** | {(df['payout_hitter'].sum()/total_bets)*100:.1f}% | {(df['payout_pitcher'].sum()/total_bets)*100:.1f}% |

> **기획자 메모:** 투수 배팅에 '동적 마진'을 적용하여, 상황이 급박해져도 배당이 과하게 오르지 않도록 설계했습니다. 
> 타자 환급률은 80~90%대로, 투수 환급률은 100% 근처로 수렴시키는 것이 1차 목표입니다.

## 🔥 동적 마진 적용 결과 (상위 10개)
"""
    top_10 = df.sort_values(by=['hitter_odds', 'pitcher_odds'], ascending=False).head(10)
    table_header = "| 이닝 | 타자 | 점수 | 결과 | 타자배당 | 투수배당 |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    table_rows = ""
    for _, r in top_10.iterrows():
        res = r['event'] if r['hitter_odds'] > 0 else "OUT"
        table_rows += f"| {r.inning}회 | {r.batter} | {r.score_home}:{r.score_away} | {res} | {r.hitter_odds}배 | {r.pitcher_odds}배 |\n"
    
    with open("data/simulation_report.md", "w", encoding="utf-8") as f:
        f.write(report + table_header + table_rows)
    print("✅ 동적 마진 시뮬레이션 완료.")

if __name__ == "__main__":
    run_simulation()
