from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "Comet VOEvent Broker", "comet.service", "The Comet VOEvent broker.", "comet"
)
