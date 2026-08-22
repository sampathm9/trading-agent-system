from dataclasses import dataclass
from typing import List

@dataclass
class BacktestTrade:
    entry_index: int
    exit_index: int
    entry_price: float
    exit_price: float
    side: str
    pnl: float


class BacktestEngine:

    def run(self, candles, strategy):
        trades: List[BacktestTrade] = []
        position = None

        for i in range(len(candles)):
            signal = strategy(candles, i)

            if position is None and signal in ('BUY', 'SELL'):
                position = {
                    'index': i,
                    'price': float(candles[i]['close']),
                    'side': signal
                }
                continue

            if position is not None and signal == 'EXIT':
                exit_price = float(candles[i]['close'])

                if position['side'] == 'BUY':
                    pnl = exit_price - position['price']
                else:
                    pnl = position['price'] - exit_price

                trades.append(
                    BacktestTrade(
                        entry_index=position['index'],
                        exit_index=i,
                        entry_price=position['price'],
                        exit_price=exit_price,
                        side=position['side'],
                        pnl=pnl
                    )
                )

                position = None

        if position is not None and candles:
            exit_price = float(candles[-1]['close'])

            if position['side'] == 'BUY':
                pnl = exit_price - position['price']
            else:
                pnl = position['price'] - exit_price

            trades.append(
                BacktestTrade(
                    entry_index=position['index'],
                    exit_index=len(candles) - 1,
                    entry_price=position['price'],
                    exit_price=exit_price,
                    side=position['side'],
                    pnl=pnl
                )
            )

        return self._summary(trades)

    def _summary(self, trades):
        total_pnl = sum(t.pnl for t in trades)
        winning = [t for t in trades if t.pnl > 0]
        losing = [t for t in trades if t.pnl < 0]

        win_rate = (
            len(winning) / len(trades) * 100
            if trades
            else 0.0
        )

        return {
            'total_trades': len(trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'trades': trades
        }
