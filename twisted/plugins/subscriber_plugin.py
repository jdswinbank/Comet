from twisted.application.service import ServiceMaker

subscriber = ServiceMaker(
    "Comet VOEvent Subscriber",
    "comet.service.subscriber",
    "The Comet VOEvent subscriber.",
    "subscriber"
)
