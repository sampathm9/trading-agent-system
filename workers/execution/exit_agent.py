class ExitAgent:

    def __init__(self, position_manager, position_monitor):
        self.position_manager = position_manager
        self.position_monitor = position_monitor

    def evaluate(self, current_price, strategy_exit=False, market_regime='UNKNOWN', force_exit=False):

        position = self.position_manager.get_position()

        decision = self.position_monitor.check(
            position=position,
            current_price=current_price,
            strategy_exit=strategy_exit,
            market_regime=market_regime,
            force_exit=force_exit
        )

        if decision['action'] == 'EXIT':
            result = self.position_manager.close(current_price)

            return {
                'action': 'EXITED',
                'reason': decision['reason'],
                'trade': result
            }

        return decision
