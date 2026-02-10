"""
Player Stock Price Simulator
이닝별 선수 가격 변동 시뮬레이션
"""

import pandas as pd
import numpy as np
from collections import defaultdict

class PlayerStockSimulator:
    """
    선수 "주식" 가격 시뮬레이터
    
    가격 공식:
    Price = Base × (1 + WPA_factor × cumulative_WPA) × (1 + demand_factor)
    """
    
    def __init__(self, base_price=1000, wpa_weight=0.5, demand_weight=0.3):
        """
        Args:
            base_price: 모든 선수의 초기 가격
            wpa_weight: WPA가 가격에 미치는 영향 (0.5 = WPA 0.1당 5% 변동)
            demand_weight: 수요가 가격에 미치는 영향
        """
        self.base_price = base_price
        self.wpa_weight = wpa_weight
        self.demand_weight = demand_weight
        
        # 선수별 누적 WPA 추적
        self.player_wpa = defaultdict(float)
        
        # 이닝별 가격 히스토리
        self.price_history = defaultdict(list)
        
        # 선수 정보 (id -> name 매핑)
        self.player_names = {}
    
    def calculate_price(self, player_id, cumulative_wpa, demand_factor=0.0):
        """
        선수의 현재 가격 계산
        
        Args:
            player_id: 선수 ID
            cumulative_wpa: 누적 WPA
            demand_factor: 수요 요인 (-1.0 ~ 1.0)
        
        Returns:
            float: 현재 가격
        """
        # WPA 기반 가격 배수
        wpa_multiplier = 1 + (self.wpa_weight * cumulative_wpa)
        
        # 수요 기반 가격 배수
        demand_multiplier = 1 + (self.demand_weight * demand_factor)
        
        # 최종 가격 (음수 방지)
        price = self.base_price * max(wpa_multiplier, 0.1) * demand_multiplier
        
        return max(price, 100)  # 최소 100포인트
    
    def simulate_game(self, plays_df):
        """
        단일 경기의 가격 변동 시뮬레이션
        
        Args:
            plays_df: WPA가 계산된 play-by-play 데이터
        
        Returns:
            DataFrame: 이닝별 선수 가격 변동
        """
        game_id = plays_df.iloc[0]['game_id']
        print(f"\n{'='*60}")
        print(f"Simulating Game {game_id}")
        print(f"{'='*60}")
        
        # 이닝별로 그룹화
        plays_df['inning_key'] = plays_df['inning'].astype(str) + plays_df['half']
        
        price_records = []
        
        for inning_key, inning_plays in plays_df.groupby('inning_key', sort=False):
            # 이 이닝의 WPA 업데이트
            for _, play in inning_plays.iterrows():
                batter_id = play['batter_id']
                pitcher_id = play['pitcher_id']
                wpa = play['wpa']
                
                # 선수 이름 저장
                if batter_id not in self.player_names:
                    self.player_names[batter_id] = play['batter_name']
                if pitcher_id not in self.player_names:
                    self.player_names[pitcher_id] = play['pitcher_name']
                
                # WPA 누적
                self.player_wpa[batter_id] += wpa
                self.player_wpa[pitcher_id] -= wpa  # 투수는 반대
            
            # 이닝 종료 시점 가격 계산
            inning_num = inning_plays.iloc[0]['inning']
            half = inning_plays.iloc[0]['half']
            
            for player_id, cum_wpa in self.player_wpa.items():
                price = self.calculate_price(player_id, cum_wpa)
                
                price_records.append({
                    'game_id': game_id,
                    'inning': inning_num,
                    'half': half,
                    'inning_key': inning_key,
                    'player_id': player_id,
                    'player_name': self.player_names[player_id],
                    'cumulative_wpa': cum_wpa,
                    'price': price,
                    'price_change_pct': ((price / self.base_price) - 1) * 100
                })
        
        return pd.DataFrame(price_records)
    
    def simulate_series(self, all_plays_df):
        """
        전체 시리즈 시뮬레이션
        
        Args:
            all_plays_df: 전체 경기 데이터
        
        Returns:
            DataFrame: 전체 시리즈 가격 변동
        """
        print(f"\n{'='*60}")
        print(f"MLB Stock Game - 2025 World Series Simulation")
        print(f"{'='*60}")
        print(f"Base Price: {self.base_price:,} points")
        print(f"WPA Weight: {self.wpa_weight}")
        print(f"Total Games: {all_plays_df['game_id'].nunique()}")
        
        all_price_records = []
        
        for game_id, game_plays in all_plays_df.groupby('game_id'):
            game_prices = self.simulate_game(game_plays)
            all_price_records.append(game_prices)
        
        full_history = pd.concat(all_price_records, ignore_index=True)
        
        return full_history
    
    def get_final_prices(self):
        """
        시리즈 종료 시점 최종 가격
        
        Returns:
            DataFrame: 선수별 최종 가격 및 수익률
        """
        final_data = []
        
        for player_id, cum_wpa in self.player_wpa.items():
            price = self.calculate_price(player_id, cum_wpa)
            
            final_data.append({
                'player_id': player_id,
                'player_name': self.player_names[player_id],
                'cumulative_wpa': cum_wpa,
                'final_price': price,
                'roi_pct': ((price / self.base_price) - 1) * 100,
                'profit': price - self.base_price
            })
        
        return pd.DataFrame(final_data).sort_values('roi_pct', ascending=False)


def run_price_simulation():
    """
    가격 시뮬레이션 실행 및 결과 저장
    """
    print("Loading WPA data...")
    plays = pd.read_csv('data/ws_2025_with_wpa.csv')
    
    # 시뮬레이터 초기화
    simulator = PlayerStockSimulator(
        base_price=1000,
        wpa_weight=0.5,  # WPA 0.1당 5% 가격 변동
        demand_weight=0.3
    )
    
    # 전체 시뮬레이션
    price_history = simulator.simulate_series(plays)
    
    # 최종 가격
    final_prices = simulator.get_final_prices()
    
    # 결과 저장
    price_history.to_csv('data/price_history.csv', index=False)
    final_prices.to_csv('data/final_prices.csv', index=False)
    
    # 결과 출력
    print("\n" + "="*60)
    print("TOP 10 MOST PROFITABLE PLAYERS (ROI)")
    print("="*60)
    top_roi = final_prices.head(10)
    for _, p in top_roi.iterrows():
        print(f"{p['player_name']:25s} | Price: {p['final_price']:6.0f} | ROI: {p['roi_pct']:+6.1f}% | Profit: {p['profit']:+6.0f}")
    
    print("\n" + "="*60)
    print("TOP 10 WORST PERFORMERS (Losses)")
    print("="*60)
    worst_roi = final_prices.tail(10)
    for _, p in worst_roi.iterrows():
        print(f"{p['player_name']:25s} | Price: {p['final_price']:6.0f} | ROI: {p['roi_pct']:+6.1f}% | Loss: {p['profit']:+6.0f}")
    
    print("\n" + "="*60)
    print("EXTREME VOLATILITY - Biggest Price Swings")
    print("="*60)
    # 각 선수의 가격 변동폭 계산
    volatility = price_history.groupby('player_name').agg({
        'price': ['min', 'max', lambda x: x.max() - x.min()]
    }).reset_index()
    volatility.columns = ['player_name', 'min_price', 'max_price', 'price_range']
    volatility = volatility.sort_values('price_range', ascending=False).head(10)
    
    for _, p in volatility.iterrows():
        print(f"{p['player_name']:25s} | Range: {p['min_price']:6.0f} - {p['max_price']:6.0f} (Δ{p['price_range']:6.0f})")
    
    print("\n✅ Simulation complete!")
    print(f"\nFiles saved:")
    print(f"  - data/price_history.csv (이닝별 가격 변동)")
    print(f"  - data/final_prices.csv (최종 가격 및 수익률)")
    
    return price_history, final_prices


if __name__ == "__main__":
    history, final = run_price_simulation()
