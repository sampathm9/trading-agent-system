def simple_strategy(candles, index):

    if index == 0:
        return 'WAIT'

    current = float(candles[index]['close'])
    previous = float(candles[index - 1]['close'])

    if current > previous:
        return 'BUY'

    if current < previous:
        return 'EXIT'

    return 'WAIT'
