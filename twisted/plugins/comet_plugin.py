from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "Comet VOEvent Broker", "comet.service.broker", "The Comet VOEvent broker.", "comet"
)
