"""
2025 World Series WPA 분석 실행
"""

import pandas as pd
from wpa_calculator import calculate_game_wpa, aggregate_player_wpa

def analyze_ws_2025():
    """
    2025 월드시리즈 WPA 분석
    """
    print("="*60)
    print("2025 World Series WPA Analysis")
    print("="*60)
    
    # 데이터 로드
    print("\n📂 Loading data...")
    df = pd.read_csv('data/ws_2025_complete.csv')
    
    print(f"✅ Loaded {len(df)} plays from {df['game_id'].nunique()} games")
    print(f"   Players: {df['batter_id'].nunique()} batters, {df['pitcher_id'].nunique()} pitchers")
    
    # WPA 계산
    print("\n🧮 Calculating WPA for all plays...")
    df_with_wpa = calculate_game_wpa(df)
    
    # 선수별 집계
    print("\n📊 Aggregating by player...")
    batter_wpa, pitcher_wpa = aggregate_player_wpa(df_with_wpa)
    
    # 결과 저장
    print("\n💾 Saving results...")
    df_with_wpa.to_csv('data/ws_2025_with_wpa.csv', index=False)
    batter_wpa.to_csv('data/ws_2025_batter_wpa.csv', index=False)
    pitcher_wpa.to_csv('data/ws_2025_pitcher_wpa.csv', index=False)
    
    # 상위 선수 출력
    print("\n" + "="*60)
    print("TOP 10 BATTERS by WPA")
    print("="*60)
    top_batters = batter_wpa.nlargest(10, 'total_wpa')
    for idx, row in top_batters.iterrows():
        print(f"{row['player_name']:25s} | WPA: {row['total_wpa']:+.3f} | PA: {int(row['plate_appearances'])}")
    
    print("\n" + "="*60)
    print("TOP 10 PITCHERS by WPA")
    print("="*60)
    top_pitchers = pitcher_wpa.nlargest(10, 'total_wpa')
    for idx, row in top_pitchers.iterrows():
        print(f"{row['player_name']:25s} | WPA: {row['total_wpa']:+.3f} | BF: {int(row['batters_faced'])}")
    
    print("\n" + "="*60)
    print("DRAMATIC MOMENTS (Highest single-play WPA)")
    print("="*60)
    dramatic = df_with_wpa.nlargest(10, 'wpa')[['game_id', 'inning', 'half', 'batter_name', 'event', 'wpa', 'description']]
    for idx, play in dramatic.iterrows():
        print(f"\nGame {play['game_id']} - {play['inning']}회 {play['half']}")
        print(f"  {play['batter_name']}: {play['event']}")
        print(f"  WPA: {play['wpa']:+.3f}")
        print(f"  {play['description'][:80]}...")
    
    print("\n✅ Analysis complete!")
    print(f"\nFiles saved:")
    print(f"  - data/ws_2025_with_wpa.csv (모든 플레이)")
    print(f"  - data/ws_2025_batter_wpa.csv (타자별 집계)")
    print(f"  - data/ws_2025_pitcher_wpa.csv (투수별 집계)")

if __name__ == "__main__":
    analyze_ws_2025()
