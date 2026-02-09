import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path):
        print("데이터가 없습니다.")
        return

    df = pd.read_csv(data_path)
    
    # 1. 시뮬레이션할 특정 경기 하나만 선택 (가장 첫 번째 경기 날짜 기준)
    target_date = df['game_date'].iloc[0]
    game_df = df[df['game_date'] == target_date].copy()
    game_df = game_df.sort_values(by=['inning', 'half', 'outs'])

    # 2. 하이브리드 동적 마진 로직 (방금 확정한 로직 그대로 적용)
    def get_odds(row):
        base_hitter = {'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 'Home Run': 5.5, 'Walk': 1.1, 'Hit By Pitch': 1.1}
        h_base = base_hitter.get(row['event'], 0)
        p_base = 1.05 if h_base == 0 else 0
        
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)
        
        h_odds = round(h_base * clutch * inning_w, 2)
        # 투수는 동적 마진 적용 (가중치 40%만 반영)
        p_odds = round(p_base * (1 + (clutch-1)*0.4) * (1 + (inning_w-1)*0.4), 2)
        return pd.Series([h_odds, p_odds])

    game_df[['H_Odds', 'P_Odds']] = game_df.apply(get_odds, axis=1)

    # 3. 리포트 작성
    report = f"# 🏟️ 1경기 집중 분석: {target_date} 월드시리즈\n\n"
    report += "유저 A가 100포인트를 언제 걸어야 '최적의 기대치'를 가질지 분석한 타석별 흐름입니다.\n\n"
    report += "| 이닝 | 타자 | 점수차 | 결과 | 타자배당(공격) | 투수배당(수비) |\n"
    report += "| :--- | :--- | :---: | :--- | :--- | :--- |\n"
    
    for _, r in game_df.iterrows():
        res = r['event'] if r['H_Odds'] > 0 else "OUT"
        report += f"| {r.inning}회{r.half} | {r.batter} | {abs(r.score_home-r.score_away)} | {res} | **{r.H_Odds}배** | {r.P_Odds}배 |\n"

    # 파일 저장 (기존 리포트와 겹치지 않게 별도 저장)
    with open("data/one_game_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 한 경기 분석 리포트 생성 완료.")

if __name__ == "__main__":
    run_single_game_analysis()
