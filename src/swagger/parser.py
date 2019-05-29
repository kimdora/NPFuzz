import yaml

from request.request import Request
# integer, string, array, boolean

class SwaggerParser():
  def __init__(self, doc):
    self.doc = doc
    self.datalist = {}
    self.pre_def = {}

  def get_req_set(self):
    req_set = []
    paths = self.get_path()
    for i in paths:
      request = {}
      method = self.get_method(i)
      for j in method:
        resp = self.get_method_response(j)
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
    #  print (i.dependency)
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

  def add_type(self, data, param):
    if data == "":
      ret = param
    elif param == "":
      ret = data
    else:
      ret = "%s*%s" % (data, param)
    return ret

  def extract_types(self, types):
    ret = []
    for i in types:
      ret = "%s*%s" % (ret, i)
    return ret

  def extract_type(self, param_data):
    #TODO : consider "additionalProperties" as items
    ret = ""
    # type, schema->type, schema->ref, schema->type * (item -> ref), ...
    if "type" in param_data:
      if param_data["type"] != "object":
        ret = param_data["type"]
    if "schema" in param_data:
      schema = self.extract_type(param_data["schema"])
      ret = self.add_type(ret, schema)
    if "$ref" in param_data:
      # TODO : $ref is only one?
      print (len(param_data["$ref"]))
      refer = param_data["$ref"].split("/")
      reference = self.extract_ref(refer[1],refer[2])
      ret = self.add_type(ret, reference)
    if "items" in param_data:
      item = self.extract_type(param_data["items"])
      ret = self.add_type(ret, item)
    if "properties" in param_data:
      prop_set = {}
      prop = param_data["properties"]
      prop_keys = prop.keys()
      for i in prop_keys:
        prop_type = self.extract_type(prop[i])
        prop_set[i] =prop_type
      ret = self.add_type(ret, prop_set)
    if "additionalProperties" in param_data:
      add_prop = self.extract_type(param_data["properties"])
      ret = self.add_type(ret, prop)
    if "allOf" in param_data:
      all_of = self.extract_type(param_data["allOf"])
      ret = self.add_type(ret, all_of)
    # TODO : handle oneOf if we find oneOf in method
    #if "oneOf" in param_data:
    #  one_of = self.extract_type(param_data["oneOf"])
    #  ret = self.add_type(ret, one_of)
    # TODO : handle anyOf if we find oneOf in method
    #if "anyOf" in param_data:
    #  any_of = self.extract_type(param_data["anyOf"])
    #  ret = self.add_type(ret, any_of)
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
