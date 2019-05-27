import yaml

class SwaggerParser():
  datalist = {}
  preDef = {}
  def __init__(self, fName):
    self.doc = yaml.load(open(fName,"r"))

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
    if len(methods) != 1:
      for method in methods:
        self.datalist[method] = data
    else:
      self.datalist[methods] = data
    return methods # List or String

  def getProperties(self, properties):
    # TODO : Consider whether default = false
    ret = {False: {}, True: {}}
    reqList = []
    if "required" in properties:
      for i in properties["required"]:
        reqList.append(i)
    for i in properties["properties"]:
      if i in reqList:
        ret[True][i] = self.typeExtract(properties["properties"][i])
      else:
        ret[False][i] = self.typeExtract(properties["properties"][i])
    return ret

  def refExtract(self, refClass, refFunc):
    funcs = self.doc[refClass][refFunc]
    self.preDef[refClass] = {}
    self.preDef[refClass][refFunc] = self.getProperties(funcs)
    return "%s[%s]" % (refClass, refFunc)

  def typeExtract(self, paramData):
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
      raise TypeExtractException
    return ret

  def getMethodParam(self, method):
    path = self.datalist[method]
    param = path[method]["parameters"]
    ret = {False: {}, True: {}}
    # TODO : Consider parameters format
    # Now : { False: { in: type }, True: { in: type } }
    for data in param:
      vType = self.typeExtract(data)
      if data["required"] == True:
        ret[True][data["in"]] = vType
      else:
        ret[False][data["in"]] = vType
    return ret # { False: { in: type }, True: { in: type } }

  def getMethodResponse(self, method):
    path = self.datalist[method]
    resp = path[method]["responses"].keys()
    # TODO : Consider reponses schema
    return resp

# TODO : Remove if we dont need testing
if __name__ == "__main__":
  parser = SwaggerParser("swagger.yaml")
  #print parser.getBasePath()
  #print parser.getSchemes()
  paths = parser.getPath()
  print paths[0]
  pathparam = parser.getPathParam(paths[0])
  print pathparam
  method = parser.getMethod(paths[0])
  print method[0]
  resp = parser.getMethodResponse(method[0])
  #print resp
  param = parser.getMethodParam(method[0])
  print param


