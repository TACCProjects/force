from rcproblem import RCProblem
import itertools

class RCParser:
  def __init__(self):
    pass

  def parse(self, filename):
    codesegment = False
    with open(filename) as fp:
      for line in fp:
        words = line.strip().split(' ')
        if words[0] == "end":
          if words[1] == "result" or words[1] == "codelet":
            problem.addCodelet(name, result, params, deps, output, code)
          elif words[1] == "problem":
            #We are all done with this problem!
            break
          elif words[1] == "code":
            codesegment = False
        if codesegment:
          code += line.strip()+"\n  "
        else:
          if words[0] == "problem":
            problem = RCProblem(words[1])
          if words[0] == "result" or words[0] == "codelet":
            if words[0] == "result":
              result = True
            else:
              result = False
            params = []
            deps = []
            output = []
            code = ""
            name = words[1]
          if words[0] == "parameter":
            foo = words[1].split('=')
            params.append((foo[0],foo[1]))

          if words[0] == "depends-on":
	    #Perform range expansion on constant ranges in each dependency
	    splitdeps = words[1].split('[')
	    evalstrng = "itertools.product("
	    basename = splitdeps[0]
	    for sdep in splitdeps[1:]:
	      sdep = sdep.rstrip(']')
	      if not sdep.find(',') == -1 or not sdep.find(':') == -1:
		for dep in sdep.rstrip(']').split(','):
		  prange = dep.split(':')
		  if len(prange) == 2:
		    evalstrng+="range("+prange[0]+","+prange[1]+"+1),"
	      else:
		evalstrng+="['"+sdep+"'],"
	    evalstrng = evalstrng.rstrip(",") + ")"

	    for prod in eval(evalstrng):
	      toadd = basename
	      for dep in prod:
		toadd+="["+str(dep)+"]"
	      deps.append(toadd)

          if words[0] == "output":
            output.append(words[1])

          if words[0] == "code":
            code = " ".join(words[1:]).strip()
            codesegment = True

          if words[0] == "data":
            problem.addData(words[1:])

    return problem

