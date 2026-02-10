import pandas as pd
import os

def run_single_game_analysis():
    data_path = "data/ws_2025_real_results.csv"
    if not os.path.exists(data_path): return

    df = pd.read_csv(data_path)
    target_date = df['game_date'].unique()[0]
    game_df = df[df['game_date'] == target_date].copy()

    # 초/말 정렬
    game_df['half_order'] = game_df['half'].map({'top': 0, 'bottom': 1})
    game_df = game_df.sort_values(by=['inning', 'half_order', 'outs']).drop('half_order', axis=1)

    # [엔진 핵심] 주자 상태 추적 변수
    runners = {"1B": False, "2B": False, "3B": False}
    current_inning_half = ""
    combo_count = 0

    def update_runners(event):
        """타석 결과에 따른 주자 이동 시뮬레이션 (데이터 보정용)"""
        nonlocal runners
        if event == 'Home Run':
            runners = {"1B": False, "2B": False, "3B": False}
        elif event in ['Single', 'Walk', 'Hit By Pitch']:
            # 단순화된 이동: 1루씩 진루
            new_runners = {"1B": True, "2B": runners["1B"], "3B": runners["2B"]}
            runners = new_runners
        elif event == 'Double':
            runners = {"1B": False, "2B": True, "3B": runners["1B"]}
        elif event == 'Triple':
            runners = {"1B": False, "2B": False, "3B": True}
        # 아웃 상황은 주자 유지 (실제론 태그업 등이 있으나 여기선 기본값 유지)

    def get_ultimate_odds(row, current_combo):
        nonlocal runners, current_inning_half
        
        # 이닝이나 공수교대 시 주자 초기화
        this_half = f"{row['inning']}_{row['half']}"
        if current_inning_half != this_half:
            runners = {"1B": False, "2B": False, "3B": False}
            current_inning_half = this_half

        # 기본 배당 (볼넷 하향 반영)
        base_hitter = {'Single': 1.4, 'Double': 2.2, 'Triple': 3.5, 'Home Run': 5.5, 'Walk': 0.8, 'Hit By Pitch': 0.8}
        h_base = base_hitter.get(row['event'], 0)
        p_base = 1.05 if h_base == 0 else 0
        
        # 주자 수 계산
        base_occupancy = sum(runners.values())
        
        # 가중치 계산
        h_weight = 1.0 + (base_occupancy * 0.25)
        p_weight = 1.0 + (base_occupancy * 0.15)
        solo_bonus = 1.2 if (base_occupancy == 0 and row['event'] == 'Home Run') else 1.0

        score_diff = abs(row['score_home'] - row['score_away'])
        clutch = 1.0 + (0.5 / (score_diff + 1))
        inning_w = 1.0 + (max(0, row['inning'] - 6) * 0.2)

        if score_diff >= 5: p_base *= 0.8

        combo_bonus = 1.0 + (current_combo * 0.05)
        h_odds = round(h_base * clutch * inning_w * 0.9 * h_weight * solo_bonus * combo_bonus, 2)
        p_odds = round(p_base * (1 + (clutch-1)*0.4) * (1 + (inning_w-1)*0.4) * p_weight, 2)
        
        # 다음 타석을 위해 주자 상태 업데이트
        current_event = row['event'] if h_base > 0 else "OUT"
        update_runners(current_event)
        
        return h_odds, p_odds, runners.copy()

    report = f"# 🏟️ MLB StatsAPI 기반 엔진 고도화: {target_date}\n\n"
    report += "> **업데이트:** 주자 추적 엔진(State Tracker) 도입으로 '주자없음' 버그 해결\n\n"
    report += "| 이닝 | 타석 | 타자 | 상황 | 결과 | 타자배당 | 투수배당 |\n"
    report += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    idx = 1
    for _, r in game_df.iterrows():
        # 현재 타석 시작 전 주자 상태를 먼저 텍스트화
        bases = [k for k, v in runners.items() if v]
        base_txt = ", ".join(bases) if bases else "주자없음"
        
        h_odds, p_odds, _ = get_ultimate_odds(r, combo_count)
        res = r['event'] if h_odds > 0 else "OUT"
        
        if h_odds > 0: combo_count += 1
        else: combo_count = 0
            
        report += f"| {r.inning}회{r.half} | {idx} | {r.batter} | {base_txt} | {res} | **{h_odds}배** | {p_odds}배 |\n"
        idx += 1

    with open("data/one_game_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ 위키 로직 반영 및 주자 추적 엔진 가동 완료!")

if __name__ == "__main__":
    run_single_game_analysis()
