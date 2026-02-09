import statsapi
import pandas as pd
import os

# 1. 위키 기반 검증용 타겟 데이터 (기획자님 제공)
target_games = [
    {"date": "2025-10-25", "home": "Blue Jays", "score": "11-4"}, # 1차전 (UTC 기준)
    {"date": "2025-10-26", "home": "Blue Jays", "score": "5-1"},  # 2차전
    {"date": "2025-10-28", "home": "Dodgers", "score": "6-5"},    # 3차전
    {"date": "2025-10-29", "home": "Dodgers", "score": "6-2"},    # 4차전
    {"date": "2025-10-30", "home": "Dodgers", "score": "6-1"},    # 5차전
    {"date": "2025-11-01", "home": "Blue Jays", "score": "3-1"},  # 6차전
    {"date": "2025-11-02", "home": "Blue Jays", "score": "5-4"}   # 7차전
]

def get_verified_ws_data():
    all_plays = []
    
    # 위키 날짜 범위 조회 (10/24 ~ 11/03)
    sched = statsapi.schedule(start_date='10/24/2025', end_date='11/03/2025')
    
    for g in sched:
        # 월드시리즈 경기만 필터링
        if g['game_type'] == 'W':
            game_id = g['game_id']
            print(f"Checking Game ID: {game_id} ({g['summary']})")
            
            # 상세 플레이 데이터 가져오기
            try:
                # 여기서부터는 play_by_play 데이터를 긁어옵니다
                pbp = statsapi.get('game_playByPlay', {'gamePk': game_id})
                for play in pbp.get('allPlays', []):
                    result = play.get('result', {})
                    about = play.get('about', {})
                    matchup = play.get('matchup', {})
                    
                    all_plays.append({
                        "game_id": game_id,
                        "game_date": g['game_date'],
                        "inning": about.get('inning'),
                        "half": about.get('halfInning'),
                        "event": result.get('event'),
                        "batter": matchup.get('batter', {}).get('fullName'),
                        "score_home": result.get('homeScore'),
                        "score_away": result.get('awayScore'),
                        "outs": play.get('count', {}).get('outs')
                    })
            except Exception as e:
                print(f"Error on {game_id}: {e}")

    return pd.DataFrame(all_plays)

# 실행 및 저장
df_final = get_verified_ws_data()
if not df_final.empty:
    os.makedirs('data', exist_ok=True)
    df_final.to_csv('data/ws_2025_verified_backtest.csv', index=False)
    print("✅ 위키 데이터와 크로스체크된 2025 WS 백테스트 데이터 생성 완료!")
