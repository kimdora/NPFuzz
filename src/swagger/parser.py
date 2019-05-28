import yaml
# integer, string, array, boolean
class Request():
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

  def get_base_path(self):
    return self.base_path

  def get_schema(self):
    return self.schemes

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

class SwaggerParser():
  datalist = {}
  pre_def = {}
  def __init__(self, f_name):
    self.doc = yaml.load(open(f_name, "r"))

  def get_req_set(self):
    req_set = []
    paths = self.get_path()
    for i in paths:
      request = {}
      method = parser.get_method(i)
      for j in method:
        resp = parser.get_method_response(j)
        param, path_param, dependency = self.get_method_param(j)
        produces = self.get_produce(j)
        request["basePath"] = self.get_base_path()
        request["schemes"] = self.get_schemes()
        request["path"] = i
        request["method"] = j
        request["contentType"] = produces
        request["parameter"] = param
        request["pathParam"] = path_param
        request["response"] = resp
        request["dependency"] = dependency
        req_set.append(Request(request))
    #for i in req_set:
    #  print i.response
    return req_set

  def get_base_path(self):
    return self.doc["basePath"] # String

  def get_schemes(self):
    return self.doc["schemes"] # List or String

  def get_path(self):
    return self.doc["paths"].keys() # List or String

  def get_path_param(self, path):
    if "parameters" in self.doc["paths"][path]:
      return self.doc["paths"][path]
    else:
      return None

  def get_method(self, path):
    data = self.doc["paths"][path]
    methods = data.keys()
    for method in methods:
      self.datalist[method] = data
    return methods # List or String

  def get_properties(self, properties):
    # TODO : Consider whether default = false
    ret = {"optional": {}, "require": {}}
    req_list = []
    if "required" in properties:
      for i in properties["required"]:
        req_list.append(i)
    for i in properties["properties"]:
      if i in req_list:
        ret["require"][i] = self.extract_type(properties["properties"][i])
      else:
        ret["optional"][i] = self.extract_type(properties["properties"][i])
    return ret

  def extract_ref(self, ref_class, ref_func):
    funcs = self.doc[ref_class][ref_func]
    self.pre_def[ref_class] = {}
    self.pre_def[ref_class][ref_func] = self.get_properties(funcs)
    return self.pre_def[ref_class]

  def extract_type(self, param_data):
    #TODO : consider "additionalProperties" as items
    ret = ""
    # type, schema->type, schema->ref, schema->type * (item -> ref), ...
    if "type" in param_data and "items" in param_data:
      # main type * item type
      item = self.extract_type(param_data["items"])
      ret = "%s*%s" % (param_data["type"], item)
    elif "type" in param_data:
      ret = param_data["type"]
    elif "$ref" in param_data:
      refer = param_data["$ref"].split("/")
      ret = self.extract_ref(refer[1],refer[2])
    elif "schema" in param_data:
      ret = self.extract_type(param_data["schema"])
    else:
      ret = ""
    return ret

  def get_produce(self, method):
    path = self.datalist[method]
    if "produces" not in path[method]:
      return None
    return path[method]["produces"]

  def get_method_param(self, method):
    path = self.datalist[method]
    if "parameters" not in path[method]:
      return {}, {}, {}
    param = path[method]["parameters"]
    ret = {"optional": {}, "require": {}}
    dependency = {}
    path_param = {}
    # TODO : Consider parameters format
    # Now : { Optional: { in: type }, Require: { in: type } }
    for data in param:
      v_type = self.extract_type(data)
      if data["in"] == "path":
        path_param[data["name"]] = v_type
        dependency[data["name"]] = v_type
      else:
        if data["required"] == True:
          ret["require"][data["name"]] = v_type
          dependency[data["name"]] = v_type
        else:
          ret["optional"][data["name"]] = v_type
    return ret, path_param, dependency

  def get_method_response(self, method):
    ret = {}
    path = self.datalist[method]
    if "responses" in path[method]:
      resp = path[method]["responses"]
      nums = resp.keys()
      for i in nums:
        ret[i] = self.extract_type(resp[i])
    return ret

# TODO : Remove if we dont need testing
if __name__ == "__main__":
  parser = SwaggerParser("swagger.yaml")
  parser.get_req_set()
