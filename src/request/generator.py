from utils.common import TerminateException
from .request import Request
import requests
import random
from json import dumps as jsonify
from dict2xml import dict2xml as xmlify

class RequestGenerator:
  def __init__(self, request):
    self.method = None
    self.schema = None
    self.host = None
    self.port = -1
    self.uri = None
    self.query = None
    self.content_type = None
    self.headers = {}
    #self.body = {}
    self.param_path = {}
    self.param_body = {}

    self.interpret_request(request)

  def add_headers(self, key, val):
    self.headers[key] = val

  def interpret_request(self, request):
    self.method = request.method
    self.schema = random.choice(request.schemes)
    self.host = request.host
    self.basepath = request.base_path
    self.path = request.path

    if hasattr(request, 'consumes') and request.consumes != None:
      content_type = random.choice(request.consumes)
      self.content_type = content_type
      self.add_headers('Content-Type', content_type)

    if hasattr(request, 'produces') and request.produces != None:
      accept = random.choice(request.produces)
      self.add_headers('Accept', accept)

    req_param = request.req_param
    for i in request.req_param:
      if req_param[i][:7] == 'integer':
        for x in req_param:
          self.param_path[x] = [req_param[x], None]
      else:
        raise TerminateException('Not Implement')

    if 'require' in request.parameter:
      require = request.parameter['require']
      for i in require:
        if require[i][:7] == 'object*':
          obj = eval(require[i][7:])
          for x in obj:
            self.param_body[x] = [obj[x], None]
        else:
          raise TerminateException('Not Implement')

  def has_empty_parameter(self):
    for i in [self.param_path, self.param_body]:
      for j in i:
        if i[j][1] == None:
          return False
    return True

  def check_type(self, type, val):
    if type == 'string':
      return isinstance(val, str)
    elif type == 'integer':
      return isinstance(val, int)
    else:
      return False

  def set_parameter(self, name, val):
    if name in self.param_path:
      if self.check_type(self.param_path[name][0], val):
        self.param_path[name][1] = val
    elif name in self.param_body:
      if self.check_type(self.param_body[name][0], val):
        self.param_body[name][1] = val
    else:
      pass

  def get_url(self):
    path = self.path
    for i in self.param_path:
      path = path.replace('{'+i+'}', str(self.param_path[i][1]))
    url = '{}://{}{}{}'.format(self.schema, self.host, self.basepath, path)
    return url

  def get_body(self):
    body = {}
    for i in self.param_body:
      body[i] = self.param_body[i][1]
    if self.content_type == 'application/x-www-form-urlencoded':
      return body
    elif self.content_type == 'application/json':
      return jsonify(body)
    elif self.content_type == 'application/xml':
      return xmlify(body, newlines=False)
    else:
      raise TerminateException('unhandlable content-type')

  def execute(self):
    if not self.has_empty_parameter():
      raise TerminateException('parameter not filled')
    r = None
    _url = self.get_url()
    _headers = self.headers
    if self.method == 'get':
      r = requests.get(_url, headers=_headers)
    elif self.method == 'post':
      _body = self.get_body()
      r = requests.post(_url, headers=_headers, data=_body)
    elif self.method == 'put':
      _body = self.get_body()
      r = requests.put(_url, headers=_headers, data=_body)
    elif self.method == 'delete':
      r = requests.delete(_url, headers=_headers)
    return r.status_code, r.content # is there any response object?
