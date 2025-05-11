import generator as mb

def parseTargetString(target):
    ret = []
    escape = False
    for char in target:
        if escape:
            if char == '\\':
                ret.append(ord(char))
            elif char == 'p':
                ret.append(-1)
            elif char == 'x':
                ret.append(-2)
            elif char == 's':
                ret.append(-3)
            escape = False
        else:
            if char == '\\':
                escape = True
            else:
                ret.append(ord(char))

    t = 0
    while t < len(ret) - 1:
        if ret[t] == -1 and ret[t + 1] == -1:
            ret.insert(t + 1, -2)
            t += 2
        else:
            t += 1

    if ret and ret[-1] == -1:
        ret.append(10)

    return ret

def parseRandomPool(str_pool):
    if not str_pool:
        return []
    ret = []
    for char in str_pool:
        ret.append(0 if char == ' ' else mb.MALBOLGE_ASSEMBLY.get(char))
    return ret

def progressForStack(stack):
    progress = 0
    cm = 8
    progress += stack[0] / cm
    for t in range(1, min(len(stack), 5)):
        cm *= 9
        progress += (stack[t] + 1) / cm
    return progress