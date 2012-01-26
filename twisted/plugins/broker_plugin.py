from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "Comet VOEvent Broker", "comet.broker.broker", "The Comet VOEvent broker.", "broker"
)
