import pandas as pd
from datetime import datetime
import os

# 1. 데이터 불러오기
def run_simulation():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path):
        print("데이터 파일이 없습니다. 먼저 데이터 수집 액션을 실행해주세요.")
        return

    df = pd.read_csv(data_path)

    # 2. 정교화된 배당률 계산 함수 (기획자님의 승리기여도 로직)
    def calculate_clutch_odds(row):
        # [A] 베이스 배당 (안타의 종류별 기본 가치)
        base_map = {
            'Single': 2.0, 
            'Double': 3.0, 
            'Triple': 5.0, 
            'Home Run': 8.0, 
            'Walk': 1.5, 
            'Hit By Pitch': 1.5
        }
        event_base = base_map.get(row['event'], 0)
        
        # 안타가 아니면(아웃 등) 배당은 0
        if event_base == 0:
            return 0
        
        # [B] 긴장감 지수 (Leverage) 계산
        # 1. 점수차 보너스: 점수차가 0점이나 1점차일 때 최대 2배까지 상승
        score_diff = abs(row['score_home'] - row['score_away'])
        score_bonus = 2.0 / (score_diff + 1)
        
        # 2. 이닝 보너스: 후반부(7회~)로 갈수록 중요도 상승 (최대 3.5배)
        inning_weight = 1.0
        if row['inning'] >= 7:
            inning_weight = 1.0 + (row['inning'] - 6) * 0.5 
            
        # 3. 아웃카운트 보너스: 2사(2-out) 상황에서 결과 내면 20% 추가 보너스
        out_bonus = 1.2 if row['outs'] == 2 else 1.0
        
        # [C] 최종 배당 산출 (베이스 * 점수차 * 이닝 * 아웃카운트)
        final_odds = event_base * score_bonus * inning_weight * out_bonus
        
        # 너무 낮은 배당 방지 (최소 기본배당의 70%) 및 너무 높은 배당 방지 (최대 50배)
        final_odds = max(final_odds, event_base * 0.7)
        final_odds = min(final_odds, 50.0)
        
        return round(final_odds, 2)

    # 배당 계산 적용
    df['odds'] = df.apply(calculate_clutch_odds, axis=1)
    
    # 1,000포인트씩 배팅했다고 가정했을 때 환급금
    df['payout'] = df['odds'] * 1000

    # 3. 리포트 생성 (마크다운 형식)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    total_investment = len(df) * 1000
    total_payout = df['payout'].sum()
    
    report = f"""# 📈 정밀 승리기여도 시뮬레이션 리포트 ({now_str})

## 📊 기획 밸런스 요약
- **총 타석 수:** {len(df)} 타석
- **수익 발생 타석:** {len(df[df['odds'] > 0])} 타석
- **투자 대비 환급률:** {(total_payout / total_investment) * 100:.1f}%
- **총 투자 포인트:** {total_investment:,} P
- **총 환급 포인트:** {total_payout:,.0f} P

> **기획자 메모:** 환급률이 100%보다 낮으면 시스템(집)이 이기는 구조이며, 100%보다 높으면 유저들이 평균적으로 돈을 버는 구조입니다.

## 🔥 승리기여도 기반 대박 타석 TOP 10
*박빙인 상황, 경기 후반부에 터진 안타일수록 배당이 높습니다.*

{df[df['odds'] > 0].sort_values('odds', ascending=False).head(10)[['inning', 'half', 'batter', 'event', 'score_home', 'score_away', 'odds']].to_markdown(index=False)}
"""

    # 파일 저장
    with open("data/simulation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 시뮬레이션 리포트가 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    run_simulation()
