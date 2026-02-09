import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path): return

    df = pd.read_csv(data_path)
    target_date = df['game_date'].unique()[0]
    game_df = df[df['game_date'] == target_date].copy()

    # 1. 초(Top) -> 말(Bottom) 순서로 정렬 (Top이 먼저 오도록)
    game_df['half_order'] = game_df['half'].map({'top': 0, 'bottom': 1})
    game_df = game_df.sort_values(by=['inning', 'half_order', 'outs']).drop('half_order', axis=1)

    # 연속 적중 보너스 추적용 변수 (가상 유저 A)
    combo_count = 0
    user_a_points = 100

    def get_advanced_odds(row, current_combo):
        # 기본 배당
        base_hitter = {'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 'Home Run': 5.5, 'Walk': 1.1, 'Hit By Pitch': 1.1}
        h_base = base_hitter.get(row['event'], 0)
        p_base = 1.05 if h_base == 0 else 0
        
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)

        # [기획 1] 점수차 가중치 강화: 5점차 이상이면 투수 배당 급감
        if score_diff >= 5:
            p_base *= 0.8  # '보험성 배팅' 방지

        # [기획 2] 수요 비례 배당 (Crowd Effect): 유저들이 안타에 몰린다고 가정해 10% 삭감
        h_odds = h_base * clutch * inning_w * 0.9 
        
        # [기획 3] 연속 적중 보너스 (Combo): 이전 적중 시 5%씩 복리 보너스
        combo_bonus = 1.0 + (current_combo * 0.05)
        
        final_h = round(h_odds * combo_bonus, 2)
        final_p = round(p_base * (1 + (clutch-1)*0.4) * (1 + (inning_w-1)*0.4), 2)
        
        return pd.Series([final_h, final_p])

    report = f"# 🏆 차세대 엔진 시뮬레이션: {target_date}\n\n"
    report += "> **적용 로직:** 초/말 정렬, 5점차 이상 투수배당 삭감, 안타 수요 몰림(-10%), 연속 적중 보너스(+5%/combo)\n\n"
    report += "| 이닝 | 타석 | 타자 | 점수차 | 결과 | 타자배당(보너스포함) | 투수배당 |\n"
    report += "| :--- | :--- | :--- | :---: | :--- | :--- | :--- |\n"
    
    idx = 1
    for _, r in game_df.iterrows():
        h_odds, p_odds = get_advanced_odds(r, combo_count)
        res = r['event'] if h_odds > 0 else "OUT"
        
        # 콤보 시스템 시뮬레이션 (안타/아웃 여부에 따라 콤보 증감)
        # 여기서는 유저가 '타자'에게 걸었다고 가정할 때의 콤보 변화
        if h_odds > 0: combo_count += 1
        else: combo_count = 0
            
        report += f"| {r.inning}회{r.half} | {idx} | {r.batter} | {abs(r.score_home-r.score_away)} | {res} | **{h_odds}배** | {p_odds}배 |\n"
        idx += 1

    with open("data/one_game_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 고도화된 1경기 분석 리포트 생성 완료!")

if __name__ == "__main__":
    run_single_game_analysis()
