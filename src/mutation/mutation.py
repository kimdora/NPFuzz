import random
import string

class Mutation:

  type_list = ["string", "float", "integer", "boolean"]
  str_max_len = 8192
  int_max_len = [-100000000000, 10000000000]
  boolean = [True, False]

  def __init__(self, seq_set):
    self.seq_set = seq_set

  def mutate_value(self, types):
    random_num = random.randrange(0,4)
    val_type = type_list[random_num]
    if val_type == self.type_list[0]:
      ret = self.random_string()
    elif val_type == self.type_list[1]:
      ret = random.random()
    elif val_type == self.type_list[2]:
      ret = random.random(int_max_len[0], int_max_len[1])
    else:
      ret = boolean[random.randrange(0,2)]
    return ret

  def mutate_path(self, path_param, path):
    new_path = path
    ret = {}
    keys = path_param.keys()
    for name in keys:
      paths = new_path.split(name)
      value = self.mutate_value()
      new_path = paths[:-1] + str(value) + paths[1:]
    return ret

  def random_string(self):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_max_len))

  def mutate_param(self, parameter):
    ret = {}
    keys = parameter.keys()
    for i in keys:
      ret[i] = self.mutate_value()
    return ret

  def mutate(self):
    for seq in self.seq_set:
      for req in seq:
        req.parameter = self.mutate_param(req.parameter)
        req.req_param = self.mutate_path(req.req_param, req.path)

