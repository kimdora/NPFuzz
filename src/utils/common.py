class TerminateException(Exception):
  def __init__(self, message):
    self.message = message

class ForceStopNLog(Exception):
  def __init__(self, message):
    self.message = message

def error(message):
  raise TerminateException(message)
