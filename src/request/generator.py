from .request import Request

class Generator():
  def __init__(self, request):
    self.req = request

  def get_curl_data(self):
    cmd = "curl"
    if self.req.method != "get":
      cmd += " -X %s" % (self.req.method.upper())
    if self.req.consumes != None:
      for i in self.req.consumes:
        consumes = i
      cmd += " -H \"Content-Type: %s\"" % (i)
    return cmd

  def get_url(self):
    # schemes, host, basepath, path
    req_url = ""
    for i in self.req.schemes:
      # TODO : consider schemes type
      schemes = i
    host = self.req.host
    basepath = self.req.base_path
    path = self.req.path
    req_url = "%s://%s%s%s" % (schemes, host, basepath, path)
    # TODO : if self.req.req_param.keys is in path
    #        then we put a real value
    # if self.req.req_param != None:
    #   Muation.insert_data(path, self.req.req_param)
    return req_url

  # main function
  def get_message(self):
    msg = { "curl": "", "url": "" }
    msg["curl"] = self.get_curl_data()
    msg["url"] = self.get_url()
    return msg

