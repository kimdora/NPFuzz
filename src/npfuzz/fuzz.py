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
        print("ForceStop", e.message)
      print('-' * 80)

  def _infer_context_parameter(self, req_set):
    callback_i = lambda x: self.independent_item.update(x)
    callback_c = lambda x: self.context.update(x)

    for req in req_set:
      self._param_parse(req, callback_i, callback_c) 

  def _param_parse(self, req, callback_i, callback_c):
    t = Mutation([])

    body = t.remove_param_object(req.parameter)
    path = t.remove_path_object(req.req_param)

    for category in body:
      for item in body[category]:
        if req.method == 'post':
          callback_i(body[category])
        else:
          callback_c({item: [body[category][item], None]})
  
    for item in path:
      callback_c({item: [path[item], None]})

  def _update_context(self, obj):
    for key in self.context:
      val = find_val(obj, key)
      if val != None:
        self.context[key][1] = val
    #print ('obj', obj)
    #print ('ctx', self.context)

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
      elif i == 1: val = random.randrange(1, t.int_max_len[1] - 1)
      elif i == 2: val = random.randrange(t.int_max_len[0] + 1, -1)
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
    #print(req.method, req.host, req.base_path, req.path)
    gen = RequestGenerator(req)
    
    for key in parameters:
      val = parameters[key]
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

    print (response_code)
    return (response_code, headers, content)

  def _request_mutation(self, req):
    mutation_target = {}
    callback_i = lambda x: 0
    callback_c = lambda x: mutation_target.update({list(x)[0]: x[list(x)[0]][0]})

    self._param_parse(req, callback_i, callback_c)

    mutation_input = {}
    for _name in mutation_target:
      _type = mutation_target[_name]
      
      change_type = bool(random.randrange(0, 2))
      if change_type:
        # should replace the change the parmeter of req and _type
        pass
      
      mutation_input.update({_name: self._get_random_value(_type)})

    response_code, headers, content = self._request(req, mutation_input)
    return response_code, headers, content, 'how it mutated'

if __name__ == '__main__':
  pass

