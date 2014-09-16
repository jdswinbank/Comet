def stringReceived(self, data):
  d = deferred_parse(data)
  d.addCallback(is_valid)
  d.addCallback(check_role)
  d.addCallback(acknowledge)
  d.addCallback(process_event)
  d.addErrback(log_failure)
  d.addCallback(close_connection)
