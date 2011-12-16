from mpycache import LRUCache
import socket
import signal
import voldemort

class RCLHT:
  def __init__(self):
    self.hashtable = {}

  def get(self, key):
    try:
      return self.hashtable[key]
    except:
      return None

  def put(self, key, value):
    self.hashtable[key] = value

class TimeoutException(Exception):
  pass

class RCDHT:
  def __init__(self):
    self.HOST = "localhost"
    self.PORT = 9999
    self.dht = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.cache = LRUCache(10000,0,0)

  def get(self, key):
    def timeout_handler(signum, frame):
      raise TimeoutException()

    value = self.cache.get(key)
    if value == None:
      self.dht.sendto("get "+key+"\n", (self.HOST, self.PORT))
      signal.signal(signal.SIGALRM, timeout_handler)
      signal.alarm(1)
      try:
        received = self.dht.recv(1024)
        return received.strip()
      except TimeoutException:
        return ""
    else:
      return value

  def put(self, key, value):
    self.cache.put(key, value)
    self.dht.sendto("put "+key+" "+value+"\n", (self.HOST, self.PORT))

class RCVoldemort:
  def __init__(self,host):
    self.dht = voldemort.StoreClient('force', [(host,6666)])
    self.cache = LRUCache(100000,0,0)

  def get(self, key):
    value = self.cache.get(key)
    if value == None:
      resp = self.dht.get(key)
      try:
        return resp[0][0]
      except:
        return ""
    else:
      return value

  def getall(self, keys):
    missing = []
    local = {}
    for key in keys:
      val = self.cache.get(key)
      if val == None:
        missing.append(key)
      else:
        local[key] = val
    remote = self.dht.get_all(missing)
    for key in remote:
      local[key] = remote[key][0][0]
    return local

  def put(self, key, value):
    self.cache.put(key, value)
    try:
      self.dht.put(key, value)
    except (voldemort.client.VoldemortException):
      pass
