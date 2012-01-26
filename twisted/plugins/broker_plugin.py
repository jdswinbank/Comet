from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "VOEvent Broker", "broker.broker", "Run a VOEvent broker.", "broker"
)
