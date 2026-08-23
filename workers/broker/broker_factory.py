from workers.broker.broker_interface import BrokerInterface
from workers.broker.paper_broker import PaperBroker
from workers.broker.real_broker import RealBroker


def create_broker(paper: bool = True) -> BrokerInterface:

    if paper:
        return PaperBroker()

    return RealBroker()
