import re
import ast

class Request:
  def __init__(self, request):
    self.host = request["host"]
    self.base_path = request["basePath"]
    self.path = request["path"]
    self.schemes = request["schemes"]
    self.method = request["method"]
    self.consumes = request["consumes"]
    self.produces = request["produces"]
    self.parameter = request["parameter"]
    self.req_param = request["pathParam"]
    self.response = request["response"]
    self.dependency = request["dependency"]

  def print_pretty(self):
    return self.method + " " + self.path

  def get_response_of(self):
    return self.response

  def has_dependencies_with(self, seq):
    return self.consume().issubset(self.produce(seq))

  def consume(self):
    ret = set()
    if self.method == 'post':
      pass
    else:
      for k in self.dependency.keys():
        ret.add(k)
    #print("consumes are ", ret)
    return ret

  def produce(self, seq):
    # TODO!
    dynamic_objects = set()
    for req in seq:
      for k1, v1 in (req.get_response_of()).items():
        if k1 >= 200 and k1 < 300:  # http status code is 2XX
          v1 = ast.literal_eval(re.sub('object\*', '', v1))
          for k2, v2 in v1.items():
            dynamic_objects.add(k2)
            if v2[0] == '{' and type(eval(v2)) == dict:
              for k3 in eval(v2).keys():
                dynamic_objects.add(k3)
    #print("produces are ", dynamic_objects)
    return dynamic_objects
