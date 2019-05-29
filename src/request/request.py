class Request:
  def __init__(self, request):
    self.base_path = request["basePath"]
    self.path = request["path"]
    self.schemes = request["schemes"]
    self.method = request["method"]
    self.content_type = request["contentType"]
    self.parameter = request["parameter"]
    self.req_param = request["pathParam"]
    self.response = request["response"]
    self.dependency = request["dependency"]

  def get_response_of(self):
    return self.response

  def has_dependencies_with(self, seq):
    return self.consume().issubset(self.produce(seq))

  def consume(self):
    # TODO!
    res = set()
    if self.method == "POST":
      return set()
    for k in self.req_param.keys():
      res.add(k)
    return res

  def produce(self, seq):
    # TODO!
    dynamic_objects = set()
    for req in seq:
      for k, v in (req.get_response_of()).items():
        if k >= 200 and k < 300: # http status code is 2XX
          for i in v.keys():
            dynamic_objects.add(i)
    return dynamic_objects
