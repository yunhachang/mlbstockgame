import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path): return

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
        
        # [투수 기본 배당]
        p_base = 1.05 if h_base == 0 else 0
        
        # [주자 상황 파악]
        base_occupancy = 0
        if row.get('on_1b'): base_occupancy += 1
        if row.get('on_2b'): base_occupancy += 1
        if row.get('on_3b'): base_occupancy += 1
        
        # [기획] 주자 상황별 가중치 적용
        # 타자 가중치: 주자당 25% 상승
        h_base_weight = 1.0 + (base_occupancy * 0.25)
        # 투수 가중치: 주자당 15% 상승 (위기 탈출 보상)
        p_base_weight = 1.0 + (base_occupancy * 0.15)
        
        # [기획] 솔로 홈런/득점 보정
        solo_bonus = 1.2 if (base_occupancy == 0 and row['event'] == 'Home Run') else 1.0

        # 상황 가중치 (점수차, 이닝)
        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)

        # 점수차 5점 이상 투수배당 삭감 (보험 방지)
        if score_diff >= 5: p_base *= 0.8

        # 타자 최종 배당 (수요몰림 -10%, 콤보, 주자 가중치 적용)
        combo_bonus = 1.0 + (current_combo * 0.05)
        h_odds = h_base * clutch * inning_w * 0.9 * h_base_weight * solo_bonus * combo_bonus
        
        # 투수 최종 배당 (주자 가중치 적용 + 동적 마진 40% 반영)
        p_clutch = 1.0 + ((clutch - 1.0) * 0.4)
        p_inning = 1.0 + ((inning_w - 1.0) * 0.4)
        # 투수에게도 주자 상황 보너스(p_base_weight)를 적용하여 위기 탈출 배당 상승
        p_odds = p_base * p_clutch * p_inning * p_base_weight
        
        return pd.Series([round(h_odds, 2), round(p_odds, 2)])

    report = f"# 🏟️ 투수 위기탈출 로직 적용 리포트: {target_date}\n\n"
    report += "> **적용 로직:** 주자 유무에 따른 투수 배당 변동 (위기 상황 시 투수 배당 상승)\n\n"
    report += "| 이닝 | 타석 | 타자 | 상황 | 결과 | 타자배당 | 투수배당 |\n"
    report += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    idx = 1
    for _, r in game_df.iterrows():
        h_odds, p_odds = get_ultimate_odds(r, combo_count)
        res = r['event'] if h_odds > 0 else "OUT"
        
        bases = []
        if r.get('on_1b'): bases.append("1루")
        if r.get('on_2b'): bases.append("2루")
        if r.get('on_3b'): bases.append("3루")
        base_txt = ", ".join(bases) if bases else "주자없음"
        
        if h_odds > 0: combo_count += 1
        else: combo_count = 0
            
        report += f"| {r.inning}회{r.half} | {idx} | {r.batter} | {base_txt} | {res} | **{h_odds}배** | {p_odds}배 |\n"
        idx += 1

    with open("data/one_game_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 투수 배당 고도화 리포트 생성 완료!")

if __name__ == "__main__":
    run_single_game_analysis()
