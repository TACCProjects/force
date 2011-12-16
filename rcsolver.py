import sys
import itertools
import random
import math
from StringIO import StringIO

class RCSolver():
  def solveProblem(self, problem, rcht):
    if rcht == None:
      rcht = RCLHT()

    if problem.result:
      out = problem.result.getOutput()[0].split('[')[0]
      ptsolved = None
      while(1):
        pset = []
        p=1
        if not ptsolved == None and not ptsolved[0] == out:
          ptsolved = None
        for param in problem.result.getParameters():
          prange = problem.result.params[param].split(':')
          if len(prange) == 2:
            if ptsolved == None:
              foo = range(int(prange[0]), int(prange[1]))
            else:
              width = int(prange[1])-int(prange[0])
              foo = range(max(int(prange[0]), int(ptsolved[p]) - width/5), min(int(prange[1]), int(ptsolved[p]) + width/5))
            random.shuffle(foo)
            pset.append(foo)
          else:
            if ptsolved == None:
              pset.append([int(prange[0])])
            else:
              pset.append([ptsolved[p]])
              
          p=p+1

        missing = False
        for e in itertools.product(*pset):
          if ptsolved == None:
            key = out 
          else:
            key = ptsolved[0]
          for i in range(0, len(e)):
            key += "[" + str(e[i]) + "]"
          #Check to see if value exists already
          value = rcht.get(key)
          if value == "" or value == None:
            attempt = key
            missing = True
            break

        if not missing:
          if ptsolved == None:
            break
          else:
            ptsolved = None
        else:
          while(1):
            solvesIt = False
            cleanattempt = attempt.split('[')[0]
            for a in attempt.split('[')[1:]:
              cleanattempt += "[]"
            for codelet in problem.codelets[cleanattempt]:
              check = codelet.matchesDep(attempt)
	      if check[0]:
		solvesIt = True
                missing = []
                code = codelet.code
                dhtdeps = []
                dephash = {}
                deplist = check[1]
                for dep in check[1]:
                  if dep[0] == '"' and dep[len(dep)-1] == '"':
                    value = dep[1:len(dep)-1]
                    dephash[dep] = value
                  else:
                    dhtdeps.append(dep)
                remote_vals = rcht.getall(dhtdeps)
                for dep in dhtdeps:
                  try:
                    value = remote_vals[dep]
                    dephash[dep] = value
                  except:
                    missing.append(dep)
                break
            if not solvesIt:
              break
            if not missing:
              break
            else:
              attempt = random.choice(missing)
          if not solvesIt:
            #Check the data files for something that fills this attempt
            found = False
            for files in problem.data:
              for file in files:
                for line in open(file):
                  if attempt in line:
                    found = True
                    value = line.split(' ')[1]
                    break
                if found:
                  break
              if found:
                break
            if found:
              print "("+file+") "+attempt + " " + value.rstrip('\n')
              rcht.put(attempt, value.rstrip('\n'))
            else:
              print "Cannot find a way to compute/load "+attempt
              sys.exit()
          else:
            callfunc = "update("
            for d in deplist:
              a = dephash[d]
              if isinstance(eval(a),str):
                callfunc += "'" + a + "',"
              else:
                callfunc += a + ","
            callfunc = callfunc.rstrip(",") + ")"
            ptsolved = []
            for i in attempt.split('['):
              ptsolved.append(i.rstrip(']'))
            ptsolved = tuple(ptsolved)
            buf = StringIO()
            sys.stdout = buf
            try:
              exec(code+"\n\nprint "+callfunc)
              sys.stdout = sys.__stdout__
            except:
              sys.stdout = sys.__stdout__
              print "Update for codelet \"{0}\" failed:".format(codelet.name)
              print "{0}".format(code)
              print "Last call: {0}".format(callfunc)
              sys.exit()
            try:
              value=eval(buf.getvalue().rstrip('\n'))
            except:
              print "Error in processing result for codelet {0}".format(codelet.name)
              print "{0}".format(code)
              print "Attempting to solve: {0}".format(attempt)
              print "Last call: {0}".format(callfunc)
              raise
            try:
              for (key,val) in zip(check[2], value):
                print key + " " + str(val)
                rcht.put(key, str(val))
            except:
              print attempt + " " + str(value)
              rcht.put(attempt, str(value))
              
