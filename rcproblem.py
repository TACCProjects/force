from collections import defaultdict

class RCProblem:
  class RCCodelet:
    def __init__(self):
      self.result = False
      self.params = {}
      self.deps = []
      self.output = []
      self.code = ""

    def makeResult(self):
      self.result = True

    def setName(self, name):
      self.name = name

    def addParameter(self, name, value):
      self.params[name] = value

    def addDepend(self, name):
      self.deps.append(name)

    def addOutput(self, name):
      self.output.append(name)

    def addCode(self, definition):
      self.code = definition

    def matchesDep(self, dependency):
      codeletMatch = False
      #Inspect the output objects
      for out in self.output:
        #Check for parameter substitutions
        possibles = out.split('[')
        splitdep = dependency.split('[')
        #Compare basenames
        if not possibles[0] == splitdep[0]:
          #This one doesn't match, move on to next output tag
          continue
        #Check for equivalent number of parameters
        if not len(possibles) == len(splitdep):
          #This one doesn't match, move on to next output tag
          continue
        vals = {}
        for i in range(1,len(possibles)):
          #Replace with parameter range
          raw_p = possibles[i].rstrip(']')
          try:
            ranges = self.params[raw_p].split(',')
          except:
            ranges = [raw_p]
          prange = []
          for r in ranges:
            foo = r.split(':')
            if len(foo) == 2:
              prange.append((foo[0],foo[1]))
            else:
              prange.append((foo[0],))

          pval = int (splitdep[i].rstrip(']') )
          vals[possibles[i].rstrip(']')] = pval
          matches = False
          for p in prange:
            if len(p) == 2:
              if pval >= int(p[0]) and pval <= int(p[1]):
                matches = True
            elif len(p) == 1:
              if pval == int(p[0]):
                matches = True
          if not matches:
            #This one doesn't match, move on to next output tag
            break
        if matches:
          codeletMatch = True
          break

      if codeletMatch:
        #Construct list of required depenencies to solve this element
        reqdeps = []
        for dep in self.deps:
          if dep[0] == '"' and dep[len(dep)-1] == '"':
            #Perform parameter expansion for literal variables
            literal = dep.strip('"').rstrip('"')
            for key in vals:
              literal = literal.replace(key, str(vals[key]))
            reqdeps.append("\""+str(eval(literal))+"\"")
          else:
            #Perform parameter expansion for dimensional variables
            base = dep.split('[')[0]
            params = dep.split('[')[1:]
            for p in params:
              expr = p.rstrip(']')
              for key in vals:
                expr = expr.replace(key, str(vals[key]))
              base += "[" + str(eval(expr)) + "]"
            reqdeps.append(base)

        #Construct list of outputs with variables substituted
        outputs = []
        for out in self.output:
          base = out.split('[')[0]
          params = out.split('[')[1:]
          for p in params:
            expr = p.rstrip(']')
            for key in vals:
              expr = expr.replace(key, str(vals[key]))
            base += "[" + str(eval(expr)) + "]"
          outputs.append(base)

        return (True,reqdeps, outputs)
      else:
        return (False, [])

    def isResult(self):
      return self.result

    def getName(self):
      return self.name

    def getCode(self):
      return self.code

    def getOutput(self):
      return self.output

    def getDependencies(self):
      return self.deps

    def getParameters(self):
      return self.params

  def __init__(self):
    self.codelets = defaultdict(list)
    self.data = []
    self.result = None

  def __init__(self, name):
    self.name = name
    self.codelets = defaultdict(list)
    self.data = []
    self.result = None

  def addCodelet(self, name, result, params, deps, output, code):
    codelet = RCProblem.RCCodelet()
    codelet.setName(name)
    if result: codelet.makeResult()
    for (name, value) in params:
      codelet.addParameter(name, value)
    for dep in deps:
      codelet.addDepend(dep)
    for out in output:
      codelet.addOutput(out)
    codelet.addCode(code)

    if result:
      self.result = codelet
    else:
      for out in output:
        #Strip values out of dimension braces
        clean = out.split('[')[0]
        for o in out.split('[')[1:]:
          clean += "[]"
        self.codelets[clean].append(codelet)        

  def addData(self, url):
    self.data.append(url)

  def numCodelets(self):
    return len(self.codelets)

  def getCodelets(self):
    def flatten(l):
      data = []
      for elem in l:
        if isinstance(elem, list):
          data += flatten(elem)
        else:
          data += [elem]
      return data

    return list(set(flatten(self.codelets.values())))

  def numData(self):
    return len(self.data)

  def numEntries(self):
    return len(self.codelets) + len(self.data)
