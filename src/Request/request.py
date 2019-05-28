class Request():
  def __init__(self, request):
    self.base_path = request["basePath"]
    self.path = request["path"]
    self.schema = request["schemes"]
    self.method = request["method"]
    self.content_type = request["contentType"]
    self.parameter = request["parameter"]
    self.req_param = request["pathParam"]
    self.response = request["response"]
    self.dependency = request["dependency"]

  def get_base_path(self):
    return self.base_path

  def get_schema(self):
    return self.schema

  def get_dependency(self):
    return self.dependency

  def get_path(self):
    return self.path

  def get_method(self):
    return self.method

  def get_content_type(self):
    return self.content_type

  def get_parameter(self):
    return self.parameter

  def get_req_param(self):
    return self.req_param

  def get_response(self):
    return self.response

  def has_dependencies(self, seq):
    return consume(req).issubset(produce(seq))

  def consume(self, req):
      required = {'GET /blog/posts/{id}': 'id'}
      res = set()
      if req in required:
          res.add(required[req])
      return res

  def produce(self, seq):
      dynamic_objects = set()
      response = {'POST /blog/posts': 'id', 'GET /blog/posts/{id}': 'checksum'}
      for req in seq:
          if req in response:
              new_objects = dynamic_objects.add(response[req])
      return dynamic_objects
