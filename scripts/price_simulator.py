import pandas as pd
import numpy as np
import os

# [설정] 단일 경기 고변동성 모드
WPA_WEIGHT = 2.5  # 기존 0.5에서 5배 상향 (70% 수익률 타겟)
BASE_PRICE = 1000

def run_single_game_simulation():
    if not os.path.exists('data/ws_2025_with_wpa.csv'):
        print("WPA 데이터가 없습니다. analyze_wpa.py를 먼저 실행하세요.")
        return

    df = pd.read_csv('data/ws_2025_with_wpa.csv')
    
    # 9이닝 단일 경기 데이터만 추출 (혹은 전체를 9이닝으로 간주)
    # 여기서는 시뮬레이션을 위해 상위 9이닝 분량만 타겟팅합니다.
    df = df[df['inning'] <= 9]
    
    price_history = []
    
    # 선수별 누적 WPA 계산 및 가격 환산
    player_groups = df.groupby(['player_id', 'player_name'])
    
    for (p_id, p_name), group in player_groups:
        # 이닝별로 가격이 어떻게 변하는지 추적
        cum_wpa = 0
        for _, row in group.sort_values(['inning', 'half']).iterrows():
            cum_wpa += row['wpa']
            # 핵심 수식: 변동성을 극대화함
            current_price = BASE_PRICE * (1 + WPA_WEIGHT * cum_wpa)
            
            # 상하한가 방어 (0원 미만 방지)
            current_price = max(100, current_price) 
            
            price_history.append({
                'inning': row['inning'],
                'half': row['half'],
                'inning_key': f"{row['inning']}{row['half']}",
                'player_id': p_id,
                'player_name': p_name,
                'cumulative_wpa': round(cum_wpa, 4),
                'price': round(current_price, 2)
            })

    result_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    result_df.to_csv('data/price_history_single_game.csv', index=False)
    
    # MVP 리포트
    final_p = result_df.groupby('player_name').last().sort_values('price', ascending=False)
    print("\n🔥 단일 경기 변동성 테스트 결과 (Top 5)")
    print(final_p[['price', 'cumulative_wpa']].head(5))

if __name__ == "__main__":
    run_single_game_simulation()
