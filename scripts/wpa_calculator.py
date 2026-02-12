"""
WPA (Win Probability Added) Calculator
MLB 역사적 데이터 기반 Win Expectancy 테이블 사용
"""

import pandas as pd
import numpy as np

class WPACalculator:
    """
    Win Probability Added 계산 엔진
    
    기반: Tom Tango의 Win Expectancy 연구 (1999-2010 MLB 데이터)
    출처: The Book: Playing the Percentages in Baseball
    """
    
    def __init__(self):
        # Run Expectancy Matrix (24 base-out states)
        # 출처: Baseball Prospectus & FanGraphs 역사적 데이터
        self.run_expectancy = self._build_re_matrix()
        
        # Win Expectancy는 이닝, 점수차, RE를 조합하여 계산
        # 간단한 버전: 9회까지의 기대승률 테이블
        self.win_expectancy_base = self._build_we_base()
    
    def _build_re_matrix(self):
        """
        Run Expectancy Matrix 구축
        24가지 상황 (8 base states × 3 out states)
        """
        # 실제 MLB 역사 데이터 기반 (2010-2020 평균)
        re_matrix = {
            # (주자상황, 아웃카운트): 기대득점
            ('000', 0): 0.481,
            ('000', 1): 0.254,
            ('000', 2): 0.098,
            
            ('100', 0): 0.859,
            ('100', 1): 0.509,
            ('100', 2): 0.214,
            
            ('010', 0): 1.100,
            ('010', 1): 0.664,
            ('010', 2): 0.305,
            
            ('001', 0): 1.356,
            ('001', 1): 0.938,
            ('001', 2): 0.350,
            
            ('110', 0): 1.437,
            ('110', 1): 0.888,
            ('110', 2): 0.426,
            
            ('101', 0): 1.784,
            ('101', 1): 1.158,
            ('101', 2): 0.471,
            
            ('011', 0): 1.964,
            ('011', 1): 1.352,
            ('011', 2): 0.570,
            
            ('111', 0): 2.254,
            ('111', 1): 1.546,
            ('111', 2): 0.736,
        }
        
        return re_matrix
    
    def _build_we_base(self):
        """
        Win Expectancy 기본 테이블
        점수차와 이닝별 승률 (역사적 데이터)
        
        간소화 버전: -10점 ~ +10점, 1-9회
        """
        # 실제로는 더 복잡하지만, 핵심 패턴을 담은 테이블
        # 9회말 기준 승률 (점수차별)
        we_9th_bottom = {
            -5: 0.01, -4: 0.02, -3: 0.05, -2: 0.12, -1: 0.28,
            0: 0.50,
            1: 0.72, 2: 0.88, 3: 0.95, 4: 0.98, 5: 0.99
        }
        
        # 이닝별 가중치 (간소화)
        inning_weights = {
            1: 0.50, 2: 0.50, 3: 0.50, 4: 0.51, 5: 0.52,
            6: 0.55, 7: 0.60, 8: 0.70, 9: 1.00
        }
        
        return {
            'ninth_inning': we_9th_bottom,
            'inning_weights': inning_weights
        }
    
    def get_run_expectancy(self, runners, outs):
        """
        현재 상황의 Run Expectancy 반환
        
        Args:
            runners: str - '000', '100', '111' 등
            outs: int - 0, 1, 2
        
        Returns:
            float - 기대 득점
        """
        if outs >= 3:
            return 0.0
        
        return self.run_expectancy.get((runners, outs), 0.0)
    
    def calculate_win_expectancy(self, inning, half, score_diff, runners, outs):
        """
        현재 상황의 Win Expectancy 계산
        
        Args:
            inning: int - 이닝 (1-9+)
            half: str - 'top' or 'bottom'
            score_diff: int - 점수차 (home - away)
            runners: str - 주자 상황
            outs: int - 아웃 카운트
        
        Returns:
            float - 승률 (0.0 ~ 1.0)
        """
        # 연장전은 9회로 취급
        inning = min(inning, 9)
        
        # Run Expectancy 가져오기
        re = self.get_run_expectancy(runners, outs)
        
        # 9회 기준 승률 테이블
        we_9th = self.win_expectancy_base['ninth_inning']
        
        # 점수차 보정 (RE 반영)
        if half == 'top':
            # 원정팀 공격: 득점하면 리드 확대/축소
            adjusted_diff = score_diff - re
        else:
            # 홈팀 공격: 득점하면 리드 확대/축소
            adjusted_diff = score_diff + re
        
        # 점수차를 테이블 범위로 제한
        adjusted_diff = int(np.clip(adjusted_diff, -5, 5))
        
        # 9회 승률 가져오기
        base_we = we_9th.get(adjusted_diff, 0.5)
        
        # 이닝별 가중치 적용 (초반일수록 불확실성 높음)
        inning_weight = self.win_expectancy_base['inning_weights'].get(inning, 0.5)
        
        # 최종 승률 (단순화 버전)
        we = 0.5 + (base_we - 0.5) * inning_weight
        
        # top/bottom 반전
        if half == 'top':
            we = 1 - we  # 원정팀 입장
        
        return np.clip(we, 0.0, 1.0)
    
    def calculate_wpa(self, before_state, after_state):
        """
        플레이 전후 상태로 WPA 계산
        
        Args:
            before_state: dict - 플레이 전 상황
            after_state: dict - 플레이 후 상황
        
        Returns:
            float - WPA 값
        """
        we_before = self.calculate_win_expectancy(**before_state)
        we_after = self.calculate_win_expectancy(**after_state)
        
        return we_after - we_before
    
    def get_base_out_state(self, runners, outs):
        """
        24가지 base-out state 식별자 반환 (디버깅용)
        """
        return f"{runners}-{outs}"


def calculate_game_wpa(plays_df):
    """
    경기 전체 플레이의 WPA 계산
    
    Args:
        plays_df: DataFrame - collect_game_plays()로 수집한 데이터
    
    Returns:
        DataFrame - WPA 컬럼이 추가된 데이터
    """
    calculator = WPACalculator()
    
    plays = plays_df.copy()
    plays['wpa'] = 0.0
    plays['we_before'] = 0.0
    plays['we_after'] = 0.0
    
    for i in range(len(plays)):
        if i == 0:
            # 첫 플레이는 기본 상태
            continue
        
        current = plays.iloc[i]
        previous = plays.iloc[i-1]
        
        # 플레이 전 상태 (이전 플레이의 결과)
        before_state = {
            'inning': int(previous['inning']),
            'half': previous['half'],
            'score_diff': int(previous['home_score'] - previous['away_score']),
            'runners': previous['runners'],
            'outs': int(previous['outs'])
        }
        
        # 플레이 후 상태 (현재 플레이의 결과)
        after_state = {
            'inning': int(current['inning']),
            'half': current['half'],
            'score_diff': int(current['home_score'] - current['away_score']),
            'runners': current['runners'],
            'outs': int(current['outs'])
        }
        
        # WPA 계산
        try:
            wpa = calculator.calculate_wpa(before_state, after_state)
            plays.at[i, 'wpa'] = wpa
            plays.at[i, 'we_before'] = calculator.calculate_win_expectancy(**before_state)
            plays.at[i, 'we_after'] = calculator.calculate_win_expectancy(**after_state)
        except Exception as e:
            print(f"Error at play {i}: {e}")
            plays.at[i, 'wpa'] = 0.0
    
    return plays


def aggregate_player_wpa(plays_df):
    """
    선수별 WPA 집계
    
    Args:
        plays_df: DataFrame - WPA가 계산된 플레이 데이터
    
    Returns:
        DataFrame - 선수별 WPA 합계
    """
    # 타자별 WPA (공격 기여도)
    batter_wpa = plays_df.groupby(['batter_id', 'batter_name']).agg({
        'wpa': 'sum',
        'at_bat_index': 'count'
    }).reset_index()
    
    batter_wpa.columns = ['player_id', 'player_name', 'total_wpa', 'plate_appearances']
    batter_wpa['role'] = 'batter'
    
    # 투수별 WPA (수비 기여도, 부호 반전)
    pitcher_wpa = plays_df.groupby(['pitcher_id', 'pitcher_name']).agg({
        'wpa': lambda x: -x.sum(),  # 투수는 실점 방지가 기여
        'at_bat_index': 'count'
    }).reset_index()
    
    pitcher_wpa.columns = ['player_id', 'player_name', 'total_wpa', 'batters_faced']
    pitcher_wpa['role'] = 'pitcher'
    
    return batter_wpa, pitcher_wpa


if __name__ == "__main__":
    # 테스트 예시
    calc = WPACalculator()
    
    # 예: 9회말 2사 주자없음, 1점 차
    we = calc.calculate_win_expectancy(
        inning=9,
        half='bottom',
        score_diff=-1,  # 1점 뒤짐
        runners='000',
        outs=2
    )
    
    print(f"9회말 2사 주자없음, 1점 뒤진 상황 승률: {we:.1%}")
    
    # 홈런 후
    we_after = calc.calculate_win_expectancy(
        inning=9,
        half='bottom',
        score_diff=0,  # 동점
        runners='000',
        outs=2
    )
    
    print(f"홈런 후 동점 상황 승률: {we_after:.1%}")
    print(f"WPA: {we_after - we:+.3f}")
