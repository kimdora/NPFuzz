import yaml
# integer, string, array, boolean
class Request():
  def __init__(self, request):
    self.basepath = request["basePath"]
    self.path = request["path"]
    self.schema = request["schemes"]
    self.method = request["method"]
    self.contentType = request["contentType"]
    self.parameter = request["parameter"]
    self.reqParam = request["pathParam"]
    self.response = request["response"]
    self.dependency = request["dependency"]

  def getBasePath(self):
    return self.basePath

  def getSchema(self):
    return self.schema

  def getPathParam(self):
    return self.pathParam

  def getPath(self):
    return self.path

  def getMethod(self):
    return self.method

  def getContentType(self):
    return self.contentType

  def getParameter(self):
    return self.parameter

  def getReqParam(self):
    return self.reqParam

  def getResponse(self):
    return self.response

class SwaggerParser():
  datalist = {}
  preDef = {}
  def __init__(self, fName):
    self.doc = yaml.load(open(fName,"r"))

  def getReqSet(self):
    reqSet = []
    paths = self.getPath()
    for i in paths:
      request = {}
      method = parser.getMethod(i)
      for j in method:
        resp = parser.getMethodResponse(j)
        param, pathParam, dependency = self.getMethodParam(j)
        produces = self.getProduce(j)
        request["basePath"] = self.getBasePath()
        request["schemes"] = self.getSchemes()
        request["path"] = i
        request["method"] = j
        request["contentType"] = produces
        request["parameter"] = param
        request["pathParam"] = pathParam
        request["response"] = resp
        request["dependency"] = dependency
        reqSet.append(Request(request))
    return reqSet

  def getBasePath(self):
    return self.doc["basePath"] # String

  def getSchemes(self):
    return self.doc["schemes"] # List or String

  def getPath(self):
    return self.doc["paths"].keys() # List or String

  def getPathParam(self, path):
    if "parameters" in self.doc["paths"][path]:
      return self.doc["paths"][path]
    else:
      return None

  def getMethod(self, path):
    data = self.doc["paths"][path]
    methods = data.keys()
    for method in methods:
      self.datalist[method] = data
    return methods # List or String

  def getProperties(self, properties):
    # TODO : Consider whether default = false
    ret = {"Optional": {}, "Require": {}}
    reqList = []
    if "required" in properties:
      for i in properties["required"]:
        reqList.append(i)
    for i in properties["properties"]:
      if i in reqList:
        ret["Require"][i] = self.typeExtract(properties["properties"][i])
      else:
        ret["Optional"][i] = self.typeExtract(properties["properties"][i])
    return ret

  def refExtract(self, refClass, refFunc):
    funcs = self.doc[refClass][refFunc]
    self.preDef[refClass] = {}
    self.preDef[refClass][refFunc] = self.getProperties(funcs)
    return self.getProperties(funcs)

  def typeExtract(self, paramData):
    #TODO : consider "additionalProperties" as items
    ret = ""
    # type, schema->type, schema->ref, schema->type * (item -> ref), ...
    if "type" in paramData and "items" in paramData:
      # main type * item type
      item = self.typeExtract(paramData["items"])
      ret = "%s*%s" % (paramData["type"], item)
    elif "type" in paramData:
      ret = paramData["type"]
    elif "$ref" in paramData:
      refer = paramData["$ref"].split("/")
      ret = self.refExtract(refer[1],refer[2])
    elif "schema" in paramData:
      ret = self.typeExtract(paramData["schema"])
    else:
      ret = None
    return ret

  def getProduce(self, method):
    path = self.datalist[method]
    if "produces" not in path[method]:
      return None
    return path[method]["produces"]

  def getMethodParam(self, method):
    path = self.datalist[method]
    if "parameters" not in path[method]:
      return None, None, None
    param = path[method]["parameters"]
    ret = {"Optional": {}, "Require": {}}
    dependency = {}
    pathParam = {}
    # TODO : Consider parameters format
    # Now : { Optional: { in: type }, Require: { in: type } }
    for data in param:
      vType = self.typeExtract(data)
      if data["in"] == "path":
        pathParam[data["name"]] = vType
        dependency[data["name"]] = vType
      else:
        if data["required"] == True:
          ret["Require"][data["name"]] = vType
          dependency[data["name"]] = vType
        else:
          ret["Optional"][data["name"]] = vType
    return ret, pathParam, dependency

  def getMethodResponse(self, method):
    ret = {}
    path = self.datalist[method]
    if "responses" in path[method]:
      resp = path[method]["responses"].keys()
      for i in resp:
        ret[i] = self.typeExtract(i)
    # TODO : Consider reponses schema
    return ret

# TODO : Remove if we dont need testing
if __name__ == "__main__":
  parser = SwaggerParser("swagger.yaml")
  parser.getReqSet()
