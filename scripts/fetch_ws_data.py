"""
MLB Play-by-Play Data Collector
주자 상황, 볼카운트, 선수 ID 등 WPA 계산에 필요한 모든 정보 수집
"""
import statsapi
import pandas as pd
import os
from datetime import datetime

def get_runner_state(runners_data):
    """
    주자 상황을 binary string으로 변환
    예: 1루 3루 → '101', 만루 → '111', 주자 없음 → '000'
    """
    bases = {'1': False, '2': False, '3': False}  # 1루, 2루, 3루
    
    if runners_data:
        for runner in runners_data:
            start_base = runner.get('movement', {}).get('start')
            if start_base in ['1B', '2B', '3B']:
                base_num = start_base[0]  # '1', '2', '3'
                bases[base_num] = True
    
    return ''.join(['1' if bases[str(i)] else '0' for i in [1, 2, 3]])

def collect_game_plays(game_id, game_date, game_summary):
    """
    단일 경기의 play-by-play 데이터 수집
    """
    print(f"\n📊 Fetching: {game_summary}")
    
    try:
        pbp = statsapi.get('game_playByPlay', {'gamePk': game_id})
    except Exception as e:
        print(f"❌ Error fetching game {game_id}: {e}")
        return []
    
    plays = []
    
    for play in pbp.get('allPlays', []):
        about = play.get('about', {})
        result = play.get('result', {})
        matchup = play.get('matchup', {})
        count = play.get('count', {})
        runners = play.get('runners', [])
        
        # 주자 상황 파싱
        runner_state = get_runner_state(runners)
        
        # 선수 정보
        batter = matchup.get('batter', {})
        pitcher = matchup.get('pitcher', {})
        
        play_data = {
            # 게임 메타 정보
            'game_id': game_id,
            'game_date': game_date,
            'inning': about.get('inning'),
            'half': about.get('halfInning'),
            'at_bat_index': about.get('atBatIndex'),
            
            # 게임 상황
            'outs': count.get('outs', 0),
            'balls': count.get('balls', 0),
            'strikes': count.get('strikes', 0),
            'runners': runner_state,  # '000', '100', '110', '111' 등
            
            # 타자/투수 정보
            'batter_id': batter.get('id'),
            'batter_name': batter.get('fullName'),
            'pitcher_id': pitcher.get('id'),
            'pitcher_name': pitcher.get('fullName'),
            
            # 플레이 결과
            'event': result.get('event'),
            'event_type': result.get('eventType'),
            'description': result.get('description'),
            
            # 스코어
            'home_score': result.get('homeScore'),
            'away_score': result.get('awayScore'),
            
            # RBI
            'rbi': result.get('rbi', 0),
        }
        
        plays.append(play_data)
    
    print(f"✅ Collected {len(plays)} plays")
    return plays

def collect_world_series_2025():
    """
    2025 월드시리즈 전체 데이터 수집
    """
    target_start = '2025-10-24'  # 2025 월드시리즈 시작일
    target_end = '2025-11-05'    # 넉넉하게 설정
    
    print(f"🔍 Searching for 2025 World Series games...")
    print(f"Date range: {target_start} to {target_end}")
    
    # 스케줄 조회
    sched = statsapi.schedule(start_date=target_start, end_date=target_end, sportId=1)
    ws_games = [g for g in sched if g.get('game_type') == 'W']
    
    if not ws_games:
        print("❌ No World Series games found")
        return None
    
    print(f"\n✅ Found {len(ws_games)} World Series games\n")
    
    # 각 경기별 데이터 수집
    all_plays = []
    for i, game in enumerate(ws_games, 1):
        print(f"[Game {i}/{len(ws_games)}]")
        game_plays = collect_game_plays(
            game['game_id'],
            game['game_date'],
            game['summary']
        )
        all_plays.extend(game_plays)
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(all_plays)
    
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # CSV 저장
    output_file = 'data/ws_2025_complete.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"Total plays collected: {len(df)}")
    print(f"Saved to: {output_file}")
    print(f"\nData summary:")
    print(f"  - Games: {df['game_id'].nunique()}")
    print(f"  - Innings: {df['inning'].max()}")
    print(f"  - Unique batters: {df['batter_id'].nunique()}")
    print(f"  - Unique pitchers: {df['pitcher_id'].nunique()}")
    
    # 주자 상황 분포 확인
    print(f"\nRunner situations:")
    print(df['runners'].value_counts().head(10))
    
    return df

if __name__ == "__main__":
    df = collect_world_series_2025()
