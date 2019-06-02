from sqlite3 import connect as sqlite3_open
from request.generator import RequestGenerator, ParameterNotFilled
from request.request import Request
from utils.common import TerminateException, ForceStopNLog
from .mutation import Mutation
from pyxml2dict import XML2Dict
from json import loads as json_decode
import random
from sys import float_info

def find_val(obj, target_key):
  for k, v in obj.items():
    if k == target_key:
      return v
    elif isinstance(v, dict):
      return find_val(v, target_key)
  return None


class Fuzzing:
  def __init__(self):
    self.db = sqlite3_open('result.db')
    self.context = None
    self.indepenent_item = None
    self.executed_request_count = None

  def _log(self, seq, result):
    pass

  def _init_context(self):
    self.context = {}
    self.independent_item = {}
    self.executed_request_count = 0

  def execute(self, seqSet):
    if not isinstance(seqSet, list):
      raise TerminateException('Fuzzing.execute should require list')

    for seq in seqSet:
      self._init_context()
      self._infer_context_parameter(seq)
      last_req = seq[-1:][0]

      try:
        # build up context
        for req in seq[:-1]:
          self._request(req)

        # do mutate      
        self._request_mutation(last_req)
      except ForceStopNLog as e:
        #self._log()
        print("ForceStop", e.message)
      #print(self.context)
      print('-' * 80)

  def _infer_context_parameter(self, req_set):
    t = Mutation([])

    for req in req_set:
      body = t.remove_param_object(req.parameter)
      path = t.remove_path_object(req.req_param)

      for category in body:
        for item in body[category]:
          if req.method == 'post':
            self.independent_item.update(body[category])
          else:
            self.context.update({item: [body[category][item], None]})
  
      for item in path:
        self.context.update({item: [path[item], None]})

  def _update_context(self, obj):
    for key in self.context:
      val = find_val(obj, key)
      if val != None:
        self.context[key][1] = val
    print ('obj', obj)
    print ('ctx', self.context)

  def _get_random_value(self, _type):
    t = Mutation([])
    if _type == 'string':
      i = random.randrange(0, 2)
      if i == 0: val = ''
      elif i == 1: val = t.random_string()
      elif i == 2: val = '' # TODO: ...
    elif _type == 'integer':
      i = random.randrange(0, 5)
      if i == 0: val = 0
      elif i == 1: val = random.randragne(1, t.int_max_len[1] - 1)
      elif i == 2: val = random.randragne(t.int_max_len[0] + 1, -1)
      elif i == 3: val = t.int_max_len[1]
      elif i == 4: val = t.int_max_len[0]
    elif _type == 'float':
      i = random.randrange(0, 5)
      if i == 0: val = 0.0
      elif i == 1: val = random.random()
      elif i == 2: val = -random.random()
      elif i == 3: val = float_info.max
      elif i == 4: val = float_info.min
    elif _type == 'boolean':
      val = bool(random.randrange(0, 2))
    elif _type == 'array':
      val = [] # TODO: should put the items
    return val

  def _request(self, req, parameters=None):
    if not isinstance(req, Request):
      raise TerminateException('Fuzzing._request should require Request object')

    if parameters == None:
      parameters = {}
    print(req.method, req.host, req.base_path, req.path)
    gen = RequestGenerator(req)
    
    for key, val in parameters:
      gen.set_parameter(key, val)

    for key in self.independent_item:
      if key not in parameters:
        val = self._get_random_value(self.independent_item[key])
        gen.set_parameter(key, val)
    for key in self.context:
      val = self.context[key][1]
      if key not in parameters:
        gen.set_parameter(key, val)

    try:
      self.executed_request_count += 1
      response_code, headers, content = gen.execute()
    except ParameterNotFilled:
      raise ForceStopNLog('Parameter is not filled')

    if 'content-type' in headers:
      content_type = headers['content-type'] # request's Accept is response's Content-Type
      if content_type != gen.headers['Accept']:
        raise ForceStopNLog('Response[content-type] and Request[accept] is not match')

      if content_type == 'application/json':
        dat = json_decode(content.decode('utf-8'))
        self._update_context(dat)
      elif content_type == 'application/xml':
        xml2dict = XML2Dict()
        dat = xml2dict.fromstring(content.decode('utf-8'))
        self._update_context(dat)
      else:
        pass

    return (response_code, headers, content)

  def _request_mutation(self, req):
    # change type ==> new reqSet(seq) or just change in mutation?
    response_code, headers, content = self._request(req, {})
    return response_code, headers, content, 'how it mutated'

if __name__ == '__main__':
  pass

