"""
User Portfolio Simulator
가상 유저들의 선수 거래 및 포트폴리오 시뮬레이션
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import random

class TradingStrategy:
    """거래 전략 베이스 클래스"""
    
    def decide_action(self, player_id, current_price, price_history, user_portfolio, available_cash):
        """
        거래 결정
        
        Returns:
            ('buy', amount) or ('sell', amount) or ('hold', 0)
        """
        raise NotImplementedError


class RandomStrategy(TradingStrategy):
    """랜덤 전략 - 무작위 매수/매도"""
    
    def decide_action(self, player_id, current_price, price_history, user_portfolio, available_cash):
        action = random.choice(['buy', 'sell', 'hold', 'hold', 'hold'])  # 60% hold
        
        if action == 'buy' and available_cash >= current_price:
            return ('buy', 1)
        elif action == 'sell' and user_portfolio.get(player_id, 0) > 0:
            return ('sell', 1)
        
        return ('hold', 0)


class MomentumStrategy(TradingStrategy):
    """추세 추종 전략 - WPA 상승 시 매수, 하락 시 매도"""
    
    def decide_action(self, player_id, current_price, price_history, user_portfolio, available_cash):
        if len(price_history) < 2:
            return ('hold', 0)
        
        # 최근 가격 변화
        recent_change = price_history[-1] - price_history[-2]
        
        if recent_change > 50 and available_cash >= current_price:
            return ('buy', 1)
        elif recent_change < -50 and user_portfolio.get(player_id, 0) > 0:
            return ('sell', 1)
        
        return ('hold', 0)


class ContrrarianStrategy(TradingStrategy):
    """역발상 전략 - 가격 하락 시 매수, 상승 시 매도"""
    
    def decide_action(self, player_id, current_price, price_history, user_portfolio, available_cash):
        if len(price_history) < 2:
            return ('hold', 0)
        
        recent_change = price_history[-1] - price_history[-2]
        
        if recent_change < -100 and available_cash >= current_price:
            return ('buy', 2)  # 더 적극적으로 매수
        elif recent_change > 100 and user_portfolio.get(player_id, 0) > 0:
            return ('sell', 1)
        
        return ('hold', 0)


class ValueInvestorStrategy(TradingStrategy):
    """가치투자 전략 - WPA 대비 저평가된 선수 매수"""
    
    def __init__(self):
        self.base_price = 1000
    
    def decide_action(self, player_id, current_price, price_history, user_portfolio, available_cash):
        if current_price < self.base_price * 0.8 and available_cash >= current_price:
            # 20% 이상 하락하면 매수
            return ('buy', 1)
        elif current_price > self.base_price * 1.5 and user_portfolio.get(player_id, 0) > 0:
            # 50% 이상 상승하면 매도
            return ('sell', 1)
        
        return ('hold', 0)


class User:
    """가상 유저"""
    
    def __init__(self, user_id, initial_cash=10000, num_slots=3, strategy=None):
        self.user_id = user_id
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.num_slots = num_slots
        self.strategy = strategy or RandomStrategy()
        
        # 포트폴리오: {player_id: quantity}
        self.portfolio = {}
        
        # 거래 내역
        self.trade_history = []
        
        # 가격 추적 (선수별)
        self.price_tracking = defaultdict(list)
    
    def get_portfolio_value(self, current_prices):
        """현재 포트폴리오 가치"""
        total = self.cash
        
        for player_id, qty in self.portfolio.items():
            total += current_prices.get(player_id, 1000) * qty
        
        return total
    
    def can_buy(self):
        """매수 가능 여부 (슬롯 체크)"""
        return len(self.portfolio) < self.num_slots
    
    def buy(self, player_id, player_name, price, quantity=1):
        """선수 매수"""
        total_cost = price * quantity
        
        if self.cash < total_cost:
            return False
        
        if not self.can_buy() and player_id not in self.portfolio:
            return False
        
        self.cash -= total_cost
        self.portfolio[player_id] = self.portfolio.get(player_id, 0) + quantity
        
        self.trade_history.append({
            'action': 'buy',
            'player_id': player_id,
            'player_name': player_name,
            'price': price,
            'quantity': quantity,
            'cash_after': self.cash
        })
        
        return True
    
    def sell(self, player_id, player_name, price, quantity=1):
        """선수 매도"""
        if self.portfolio.get(player_id, 0) < quantity:
            return False
        
        # 매도 수수료 2%
        fee = price * quantity * 0.02
        proceeds = price * quantity - fee
        
        self.cash += proceeds
        self.portfolio[player_id] -= quantity
        
        if self.portfolio[player_id] == 0:
            del self.portfolio[player_id]
        
        self.trade_history.append({
            'action': 'sell',
            'player_id': player_id,
            'player_name': player_name,
            'price': price,
            'quantity': quantity,
            'fee': fee,
            'cash_after': self.cash
        })
        
        return True


class MarketSimulator:
    """시장 전체 시뮬레이션"""
    
    def __init__(self, price_history_df, num_users=100):
        self.price_history = price_history_df
        self.num_users = num_users
        
        # 유저 생성 (다양한 전략 배분)
        self.users = []
        strategies = [
            (RandomStrategy, 30),
            (MomentumStrategy, 25),
            (ContrrarianStrategy, 25),
            (ValueInvestorStrategy, 20)
        ]
        
        user_id = 0
        for strategy_class, count in strategies:
            for _ in range(count):
                strategy = strategy_class()
                user = User(user_id, initial_cash=10000, num_slots=3, strategy=strategy)
                self.users.append(user)
                user_id += 1
        
        # 이닝별 포트폴리오 스냅샷
        self.portfolio_snapshots = []
    
    def simulate(self):
        """전체 시뮬레이션 실행"""
        print(f"\n{'='*60}")
        print(f"Market Simulation - {self.num_users} Virtual Users")
        print(f"{'='*60}")
        
        # 이닝별로 처리
        for inning_key, inning_data in self.price_history.groupby('inning_key', sort=False):
            current_prices = {}
            player_names = {}
            
            for _, row in inning_data.iterrows():
                current_prices[row['player_id']] = row['price']
                player_names[row['player_id']] = row['player_name']
            
            # 각 유저가 거래 결정
            for user in self.users:
                # 현재 보유 중인 선수들에 대해 매도 검토
                for player_id in list(user.portfolio.keys()):
                    if player_id not in current_prices:
                        continue
                    
                    user.price_tracking[player_id].append(current_prices[player_id])
                    
                    action, amount = user.strategy.decide_action(
                        player_id,
                        current_prices[player_id],
                        user.price_tracking[player_id],
                        user.portfolio,
                        user.cash
                    )
                    
                    if action == 'sell' and amount > 0:
                        user.sell(player_id, player_names[player_id], current_prices[player_id], amount)
                
                # 새로운 선수 매수 검토 (상위 10명만)
                top_players = inning_data.nlargest(10, 'price')['player_id'].tolist()
                
                for player_id in top_players:
                    if player_id not in user.price_tracking:
                        user.price_tracking[player_id].append(current_prices[player_id])
                    
                    action, amount = user.strategy.decide_action(
                        player_id,
                        current_prices[player_id],
                        user.price_tracking[player_id],
                        user.portfolio,
                        user.cash
                    )
                    
                    if action == 'buy' and amount > 0:
                        user.buy(player_id, player_names[player_id], current_prices[player_id], amount)
            
            # 이닝 종료 시 스냅샷
            for user in self.users:
                portfolio_value = user.get_portfolio_value(current_prices)
                
                self.portfolio_snapshots.append({
                    'inning_key': inning_key,
                    'user_id': user.user_id,
                    'cash': user.cash,
                    'portfolio_value': portfolio_value,
                    'total_value': portfolio_value,
                    'roi_pct': ((portfolio_value / user.initial_cash) - 1) * 100,
                    'strategy': user.strategy.__class__.__name__
                })
        
        return pd.DataFrame(self.portfolio_snapshots)
    
    def get_final_results(self):
        """최종 결과 집계"""
        final_results = []
        
        for user in self.users:
            # 최종 가격으로 포트폴리오 평가 (마지막 이닝 가격 사용)
            last_inning = self.price_history['inning_key'].iloc[-1]
            last_prices = self.price_history[self.price_history['inning_key'] == last_inning]
            current_prices = dict(zip(last_prices['player_id'], last_prices['price']))
            
            final_value = user.get_portfolio_value(current_prices)
            
            final_results.append({
                'user_id': user.user_id,
                'strategy': user.strategy.__class__.__name__,
                'initial_cash': user.initial_cash,
                'final_value': final_value,
                'profit': final_value - user.initial_cash,
                'roi_pct': ((final_value / user.initial_cash) - 1) * 100,
                'num_trades': len(user.trade_history),
                'final_portfolio_size': len(user.portfolio)
            })
        
        return pd.DataFrame(final_results)


def run_user_simulation():
    """유저 시뮬레이션 실행"""
    print("Loading price history...")
    price_history = pd.read_csv('data/price_history.csv')
    
    # 시뮬레이터 초기화
    simulator = MarketSimulator(price_history, num_users=100)
    
    # 시뮬레이션 실행
    snapshots = simulator.simulate()
    final_results = simulator.get_final_results()
    
    # 결과 저장
    snapshots.to_csv('data/user_portfolio_snapshots.csv', index=False)
    final_results.to_csv('data/user_final_results.csv', index=False)
    
    # 결과 출력
    print("\n" + "="*60)
    print("STRATEGY PERFORMANCE COMPARISON")
    print("="*60)
    strategy_perf = final_results.groupby('strategy').agg({
        'roi_pct': ['mean', 'std', 'min', 'max'],
        'profit': 'mean',
        'num_trades': 'mean'
    }).round(2)
    print(strategy_perf)
    
    print("\n" + "="*60)
    print("TOP 10 USERS by ROI")
    print("="*60)
    top_users = final_results.nlargest(10, 'roi_pct')
    for _, u in top_users.iterrows():
        print(f"User {u['user_id']:3d} ({u['strategy']:20s}) | ROI: {u['roi_pct']:+6.1f}% | Profit: {u['profit']:+7.0f} | Trades: {int(u['num_trades'])}")
    
    print("\n" + "="*60)
    print("BOTTOM 10 USERS by ROI")
    print("="*60)
    bottom_users = final_results.nsmallest(10, 'roi_pct')
    for _, u in bottom_users.iterrows():
        print(f"User {u['user_id']:3d} ({u['strategy']:20s}) | ROI: {u['roi_pct']:+6.1f}% | Loss: {u['profit']:+7.0f} | Trades: {int(u['num_trades'])}")
    
    print("\n✅ User simulation complete!")
    print(f"\nFiles saved:")
    print(f"  - data/user_portfolio_snapshots.csv (이닝별 포트폴리오)")
    print(f"  - data/user_final_results.csv (최종 수익률)")
    
    return snapshots, final_results


if __name__ == "__main__":
    snapshots, results = run_user_simulation()
