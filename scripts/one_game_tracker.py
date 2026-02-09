import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path):
        print("데이터가 없습니다.")
        return

    df = pd.read_csv(data_path)
    
    # 첫 번째 경기 데이터만 추출
    target_date = df['game_date'].unique()[0]
    game_df = df[df['game_date'] == target_date].copy()
    game_df = game_df.sort_values(by=['inning', 'half', 'outs'])

    def get_odds(row):
        base_hitter = {'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 'Home Run': 5.5, 'Walk': 1.1, 'Hit By Pitch': 1.1}
        h_base = base_hitter.get(row['event'], 0)
        p_base = 1.05 if h_base == 0 else 0
        
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)
        
        h_odds = round(h_base * clutch * inning_w, 2)
        p_clutch = 1.0 + ((clutch - 1.0) * 0.4)
        p_inning = 1.0 + ((inning_w - 1.0) * 0.4)
        p_odds = round(p_base * p_clutch * p_inning, 2)
        return pd.Series([h_odds, p_odds])

    game_df[['H_Odds', 'P_Odds']] = game_df.apply(get_odds, axis=1)

    report = f"# 🏟️ 1경기 집중 분석: {target_date} 월드시리즈\n\n"
    report += "| 이닝 | 타석 | 타자 | 점수차 | 결과 | 타자배당 | 투수배당 |\n"
    report += "| :--- | :--- | :--- | :---: | :--- | :--- | :--- |\n"
    
    idx = 1
    for _, r in game_df.iterrows():
        res = r['event'] if r['H_Odds'] > 0 else "OUT"
        report += f"| {r.inning}회{r.half} | {idx} | {r.batter} | {abs(r.score_home-r.score_away)} | {res} | **{r.H_Odds}배** | {r.P_Odds}배 |\n"
        idx += 1

    # 파일 생성 확인 로그
    output_path = "data/one_game_analysis.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ {output_path} 생성 완료!")

if __name__ == "__main__":
    run_single_game_analysis()
