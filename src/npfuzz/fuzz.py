from sqlite3 import connect as sqlite3_open
from request.generator import RequestGenerator, ParameterNotFilled
from request.request import Request
from utils.common import TerminateException, ForceStop
from .mutation import Mutation
from pyxml2dict import XML2Dict
from json import loads as json_decode
import random
from sys import float_info
import pickle
from datetime import datetime
from shutil import copyfile

def find_val(obj, target_key):
  for k, v in obj.items():
    if k == target_key:
      return v
    elif isinstance(v, dict):
      return find_val(v, target_key)
  return None

class Fuzzing:
  def __init__(self):
    self.db = self._init_db()
    self.context = None
    self.indepenent_item = None
    self.executed_request_count = None
    self.final_status_code = None
    self.request_parameters = None

  def _init_db(self):
    fname = 'result_{}.db'.format(str(datetime.utcnow()).replace(' ', '_'))
    copyfile('result_empty.db', fname)
    return sqlite3_open(fname)

  def _log(self, req_set):
    #print('\033[1;31m')
    req_set = pickle.dumps(req_set)
    context = pickle.dumps(self.context)
    status = self.last_status_code
    req_param = pickle.dumps(self.request_parameters)
    req_cnt =self.executed_request_count
    #print('\033[0;0m')
    try:
      cur = self.db.cursor()
      cur.execute('INSERT INTO fuzzing_log (status, req_set, req_param, req_cnt, context) VALUES(?, ?, ?, ?, ?)', (status, req_set , req_param, req_cnt, context))
      self.db.commit()
    except:
      raise TerminateException('db error')

  def _init_context(self):
    self.context = {}
    self.independent_item = {}
    self.executed_request_count = 0
    self.last_status_code = 0
    self.request_parameters = []

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
      except ForceStop as e:
        print("ForceStop", e.message)
      finally:
        self._log(seq)
      #print('-' * 80)

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
        if req.method == 'post' and body[category][item] not in self.context:
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
      elif i == 1: val = t.random_string(20)
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
    else:
      val = None
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

    self.request_parameters.append(gen.get_parameters())

    try:
      self.executed_request_count += 1
      response_code, headers, content = gen.execute()
    except ParameterNotFilled:
      raise ForceStop('Parameter is not filled')

    self.last_status_code = response_code
    if response_code == 500: raise ForceStop('status_code == 500')

    if 'content-type' in headers:
      content_type = headers['content-type'] # request's Accept is response's Content-Type
      #if content_type != gen.headers['Accept']:
      #  raise ForceStop('Response[content-type] and Request[accept] is not match')

      if content_type == 'application/json':
        dat = json_decode(content.decode('utf-8'))
        self._update_context(dat)
      elif content_type == 'application/xml':
        xml2dict = XML2Dict()
        dat = xml2dict.fromstring(content.decode('utf-8'))
        self._update_context(dat)
      else:
        pass

    #print (response_code)
    self.last_status_code = response_code
    return (headers, content)

  def _request_mutation(self, req):
    mutation_target = {}

    _mutation_type = random.randrange(0, 2)
    if _mutation_type == 0: # both mutation
      cb1 = lambda x: mutation_target.update({list(x)[0]: x[list(x)[0]][0]})
      cb2 = lambda x: mutation_target.update({list(x)[0]: x[list(x)[0]][0]})
    elif _mutation_type == 1: # indepedent_item mutation
      cb1 = lambda x: mutation_target.update({list(x)[0]: x[list(x)[0]][0]})
      cb2 = lambda x: 0

    self._param_parse(req, cb1, cb2)

    mutation_input = {}
    for _name in mutation_target:
      _type = mutation_target[_name]
      
      type_change_flag = bool(random.randrange(0, 2))
      if type_change_flag:
        candidate_type = ['integer', 'string', 'array', 'float', 'boolean']
        to_type = random.choice(candidate_type)
        if _name in req.req_param:
          req.req_param[_name] = to_type
        for category in req.parameter:
          for key in req.parameter[category]:
            if _name in req.parameter[category][key]:
              req.parameter[category][key] = req.parameter[category][key].replace('\'{}\': \'{}\''.format(_name, _type), '\'{}\': \'{}\''.format(_name, to_type))
        #{'require': {'body': "object*{'body': 'string', 'checksum': 'string'}"}, 'optional': {}}
        #print(_name, _type)
        #print(req.parameter) 
        #print(req.req_param) 
      mutation_input.update({_name: self._get_random_value(_type)})

    headers, content = self._request(req, mutation_input)
    return headers, content, 'how it mutated'

if __name__ == '__main__':
  pass

