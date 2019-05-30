import random
import re
import string
import copy
from ast import literal_eval
from .request import Request

class Mutation:

  type_list = ["string", "float", "integer", "boolean", "array"]
  str_max_len = 8192
  int_max_len = [-100000000000, 10000000000]
  boolean = [True, False]

  def __init__(self, seq_set):
    self.seq_set = seq_set

  def mutate_value(self, types):
    # TODO : extend 4->5, when we handle array
    random_num = random.randrange(0,4)
    val_type = self.type_list[random_num]
    if val_type == self.type_list[0]:
      ret = self.random_string()
    elif val_type == self.type_list[1]:
      ret = random.random()
    elif val_type == self.type_list[2]:
      ret = random.randrange(self.int_max_len[0], self.int_max_len[1])
    elif val_type == self.type_list[3]:
      ret = self.boolean[random.randrange(0,2)]
    else:
      # TODO : hanlder array
      ret = random.randrange(0,2)
    return ret

  def mutate_path(self, path_param, path):
    new_path = path
    ret = {}
    keys = path_param.keys()
    for name in keys:
      paths = new_path.split(name)
      ret[name] = self.mutate_value(path_param[name])
      new_path = str(paths[0])[:-1] + str(ret[name]) + str(paths[1])[1:]
    return ret, new_path

  def random_string(self):
    letters = string.ascii_lowercase
    length = random.randrange(0, self.str_max_len)
    return ''.join(random.choice(letters) for i in range(length))

  def mutate_param(self, parameter):
    ret = {"optional" :{}, "require": {}}
    keys = parameter.keys()
    for i in keys:
      keys2 = parameter[i].keys()
      for j in keys2:
        ret[i][j] = self.mutate_value(parameter[i][j])
    return ret

  def remove_param_object(self, data):
    string = str(data)
    value = {}
    keys = data.keys()
    for i in keys:
      string = str(data[i])
      while True:
        if "object*" in string:
          string = string.replace("object*", "REMOVE_", 1)
          string = string.split("REMOVE_")[1][:-2]
          value[i] = literal_eval(string)
        else:
          value[i] = literal_eval(string)
          break
    return value

  def remove_path_object(self, data):
    string = str(data)
    value = {}
    keys = data.keys()
    while True:
      if "object*" in string:
        string = string.replace("object*", "REMOVE_", 1)
        string = string.split("REMOVE_")[1][:-2]
        value = literal_eval(string)
      else:
        value = literal_eval(string)
        break
    return value

  def mutate(self):
    seq_set = []
    for seq in range(0,len(self.seq_set)):
      sequence = []
      for req in self.seq_set[seq]:
        request = copy.deepcopy(req)
        param = self.remove_param_object(request.parameter)
        req_param = self.remove_path_object(request.req_param)
        request.parameter = self.mutate_param(param)
        request.req_param, path = self.mutate_path(req_param, request.path)
        sequence.append(request)
      seq_set.append(sequence)
    return seq_set


