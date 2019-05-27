import yaml

class SwaggerParser():
  datalist = {}
  def __init__(self, fName):
    self.doc = yaml.load(open(fName,"r"))

  def getBasePath(self):
    return self.doc["basePath"] # String

  def getSchemes(self):
    return self.doc["schemes"] # List or String

  def getPath(self):
    return self.doc["paths"].keys() # List or String

  def getMethod(self, path):
    data = self.doc["paths"][path]
    methods = data.keys()
    if len(methods) != 1:
      for method in methods:
        self.datalist[method] = data
    else:
      self.datalist[methods] = data
    return methods # List or String

  def typeExtract(self, paramData):
    if "type" in paramData:
      return paramData["type"]
    elif "schema" in paramData:
      # TODO : Consider $ref type, instead of non-type schema
      if "type" in paramData["schema"]:
        return paramData["schema"]["type"]
      else:
        return paramData["schema"]
    else:
      # TODO : find other key value for type
      return ""

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

  def getDef(self):
    # TODO : Consider definitions field
    return "" # List or String
    None

  def getDefProp(self):
    # TODO : Consider parameters field
    return "" # Class { field : type, ... }
    None

  def getParam(self):
    # TODO : Consider parameters field
    None

  def getSecDef(self):
    # TODO : Consider securityDefintions field
    None



# TODO : Remove if we dont need testing
if __name__ == "__main__":
  parser = SwaggerParser("swagger.yaml")
  print parser.getBasePath()
  print parser.getSchemes()
  paths = parser.getPath()
  print paths
  method = parser.getMethod(paths[0])
  print method
  resp = parser.getMethodResponse(method[0])
  print resp
  param = parser.getMethodParam(method[0])
  print param


