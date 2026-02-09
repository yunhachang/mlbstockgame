import pandas as pd
from datetime import datetime

# 데이터 로드
df = pd.read_csv("data/ws_2025_real_results.csv")

def calculate_odds(row):
    # 기획자님의 배당 로직
    base = {'Single': 2, 'Double': 3, 'Triple': 5, 'Home Run': 8}.get(row['event'], 0)
    if base == 0: return 0
    
    # 9회 이후 긴장감 가중치
    multiplier = 1.5 if row['inning'] >= 9 else 1.0
    return round(base * multiplier, 2)

df['odds'] = df.apply(calculate_odds, axis=1)
df['payout'] = df['odds'] * 1000 # 1000포인트씩 배팅 가정

# 리포트 생성
report = f"""# 📈 시뮬레이션 리포트 ({datetime.now().strftime('%Y-%m-%d %H:%M')})

## 📊 요약
- **총 타석 수:** {len(df)}
- **수익 발생 타석:** {len(df[df['odds'] > 0])}
- **총 환급 포인트:** {df['payout'].sum():,.0f} P

## 🔥 주요 대박 타석 (TOP 5)
{df[df['odds'] > 0].sort_values('odds', ascending=False).head(5)[['inning', 'batter', 'event', 'odds']].to_markdown(index=False)}
"""

with open("data/simulation_report.md", "w", encoding="utf-8") as f:
    f.write(report)
