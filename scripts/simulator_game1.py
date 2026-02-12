import pandas as pd
import numpy as np
import os
import sys
from collections import defaultdict

# [핵심 설정]
WPA_WEIGHT = 2.8
BASE_PRICE = 1000

def run_game1_simulation():
    input_path = 'data/ws_2025_with_wpa.csv'
    
    # 1. 파일 존재 확인
    if not os.path.exists(input_path):
        print(f"❌ 에러: {input_path} 파일이 없습니다. 현재 경로의 파일들:")
        print(os.listdir('.'))
        sys.exit(1) # 에러와 함께 종료

    df = pd.read_csv(input_path)
    df.columns = [c.lower().replace(' ', '_') for c in df.columns] # 컬럼명 표준화
    
    print(f"📊 로드된 컬럼: {list(df.columns)}")

    # 2. 필수 컬럼 체크
    required = ['game_id', 'inning', 'half', 'player_id', 'player_name', 'wpa']
    for col in required:
        if col not in df.columns:
            print(f"❌ 에러: '{col}' 컬럼이 없습니다.")
            sys.exit(1)

    # 3. 1차전 추출
    game_ids = df['game_id'].unique()
    game1_df = df[df['game_id'] == game_ids[0]].copy()
    
    price_history = []
    player_stats = defaultdict(float) 
    
    for (inn, half), step_data in game1_df.groupby(['inning', 'half'], sort=False):
        for _, row in step_data.iterrows():
            player_stats[row['player_id']] += row['wpa']
        
        # 이닝별 가격 기록
        for p_id in player_stats:
            p_name = game1_df[game1_df['player_id'] == p_id]['player_name'].iloc[0]
            price = BASE_PRICE * (1 + WPA_WEIGHT * player_stats[p_id])
            price_history.append({
                'inning_key': f"{inn}{half}",
                'player_name': p_name,
                'price': max(100, round(price, 2))
            })

    # 4. 결과 저장
    if not price_history:
        print("❌ 에러: 생성된 가격 데이터가 없습니다.")
        sys.exit(1)

    result_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    out_path = 'data/game1_price_history.csv'
    result_df.to_csv(out_path, index=False)
    
    print(f"✅ 파일 생성 완료: {out_path} ({len(result_df)} rows)")

if __name__ == "__main__":
    run_game1_simulation()
