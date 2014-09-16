class VOEventReceiver(Protocol):
  TIMEOUT = 20 # seconds

  def connectionMade(self):
    setTimeout(self.TIMEOUT)

  def connectionLost(self):
    setTimeout(None)
    close_connection()

  def timeoutConnection(self):
    log.msg("Connection timed out")
    close_connection()

  def stringReceived(self, data):
    try:
        message = parse(data)
        if is_valid(message):
            log.info("Good message received")
            acknowledge(message)
            process_event(message)
        else:
            log.warning("Bad message received")
    except ParseError:
        log.warning("Message unparsable")
    finally:
        close_connection()
