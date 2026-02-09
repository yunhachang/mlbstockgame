import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path): return

    # CSV 로드 (모든 데이터를 일단 문자열로 취급하여 누락 방지)
    df = pd.read_csv(data_path)
    target_date = df['game_date'].unique()[0]
    game_df = df[df['game_date'] == target_date].copy()

    # 1. 초(Top) -> 말(Bottom) 순서 정렬
    game_df['half_order'] = game_df['half'].map({'top': 0, 'bottom': 1})
    game_df = game_df.sort_values(by=['inning', 'half_order', 'outs']).drop('half_order', axis=1)

    combo_count = 0

    def get_ultimate_odds(row, current_combo):
        # [타자 기본 배당]
        base_hitter = {
            'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 
            'Home Run': 5.5, 'Walk': 0.8, 'Hit By Pitch': 0.8
        }
        h_base = base_hitter.get(row['event'], 0)
        p_base = 1.05 if h_base == 0 else 0
        
        # [주자 판별 끝판왕 로직]
        # 값이 있고, 'NaN' 문자열이 아니며, null이 아닐 때만 True
        def has_runner(val):
            if pd.isna(val): return False
            v_str = str(val).strip().lower()
            if v_str == "" or v_str == "nan" or v_str == "none" or v_str == "0.0" or v_str == "0":
                return False
            return True

        on_1 = has_runner(row.get('on_1b'))
        on_2 = has_runner(row.get('on_2b'))
        on_3 = has_runner(row.get('on_3b'))
        
        base_occupancy = sum([on_1, on_2, on_3])
        
        # [기획 가중치] 
        h_base_weight = 1.0 + (base_occupancy * 0.25)
        p_base_weight = 1.0 + (base_occupancy * 0.15)
        
        # 솔로 홈런 보너스
        solo_bonus = 1.2 if (base_occupancy == 0 and row['event'] == 'Home Run') else 1.0

        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)

        if score_diff >= 5: p_base *= 0.8

        combo_bonus = 1.0 + (current_combo * 0.05)
        h_odds = h_base * clutch * inning_w * 0.9 * h_base_weight * solo_bonus * combo_bonus
        
        p_clutch = 1.0 + ((clutch - 1.0) * 0.4)
        p_inning = 1.0 + ((inning_w - 1.0) * 0.4)
        p_odds = p_base * p_clutch * p_inning * p_base_weight
        
        return pd.Series([round(h_odds, 2), round(p_odds, 2), on_1, on_2, on_3])

    report = f"# 🏟️ 기획 최종 고도화 리포트: {target_date}\n\n"
    report += "> **최종 밸런스:** 볼넷 하향, 주자 가중치(타자/투수 양방향), 솔로홈런 인정, 콤보 시스템\n\n"
    report += "| 이닝 | 타석 | 타자 | 상황 | 결과 | 타자배당 | 투수배당 |\n"
    report += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    idx = 1
    for _, r in game_df.iterrows():
        h_odds, p_odds, on_1, on_2, on_3 = get_ultimate_odds(r, combo_count)
        res = r['event'] if h_odds > 0 else "OUT"
        
        bases = []
        if on_1: bases.append("1루")
        if on_2: bases.append("2루")
        if on_3: bases.append("3루")
        base_txt = ", ".join(bases) if bases else "주자없음"
        
        if h_odds > 0: combo_count += 1
        else: combo_count = 0
            
        report += f"| {r.inning}회{r.half} | {idx} | {r.batter} | {base_txt} | {res} | **{h_odds}배** | {p_odds}배 |\n"
        idx += 1

    with open("data/one_game_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 모든 예외 케이스를 반영한 주자 인식 로직 완료!")

if __name__ == "__main__":
    run_single_game_analysis()
