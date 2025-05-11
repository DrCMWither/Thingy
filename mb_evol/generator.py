xlat1       = '+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA"lI.v%{gJh4G\\-=O@5`_3i<?Z\';FNQuY]szf$!BS/|t:Pn6^Ha'
xlat2       = '5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK\'X~xDl}REokN:#?G"i@'
legal       = 'ji*p</vo'
space       = '\t\r\n\v\f '
EXIT        = -1
WANTS_INPUT = -2

opc = {
    'jump': 4,
    'out': 5,
    'in': 23,
    'rot': 39,
    'movd': 40,
    'opr': 62,
    'nop': 68,
    'halt': 81
}
opcodes = [4, 5, 23, 39, 40, 62, 68, 81]
assembly = {
    'i': 4,
    '<': 5,
    '/': 23,
    '*': 39,
    'j': 40,
    'p': 62,
    'o': 68,
    'v': 81
}

def loadVM(code_str, partially = False):
    vm = {
        'mem': [0] * 59049,
        'a': 0,
        'c': 0,
        'd': 0
    }
    pos = 0
    for char in code_str:
        if char in space:
            continue
        tt = ord(char)
        if tt < 127 and tt > 32 and legal.find(xlat1[((tt - 33 + pos) % 94)]) == -1:
            raise ValueError('Illegal character.')
        if pos == 59049:
            raise ValueError('Code too long!')
        vm['mem'][pos] = tt
        pos += 1

    if not partially:
        while pos < 59049:
            vm['mem'][pos] = op(vm['mem'][pos - 1], vm['mem'][pos - 2])
            pos += 1
    return vm

def step(vm, input_val = None):
    if vm['mem'][vm['c']] < 33 or vm['mem'][vm['c']] > 126:
        raise ValueError('Would enter infinite loop!')

    output = None
    va = vm['a']
    vc = vm['c']
    vd = vm['d']
    vmd = vm['mem'][vm['d']]

    opcode = xlat1[((vm['mem'][vc] - 33 + vc) % 94)]

    if opcode == 'j':
        vm['d'] = vmd
    elif opcode == 'i':
        vm['c'] = vmd
    elif opcode == '*':
        vm['a'] = vm['mem'][vd] = (vmd // 3) + (vmd % 3) * 19683
    elif opcode == 'p':
        vm['a'] = vm['mem'][vd] = op(va, vmd)
    elif opcode == '<':
        output = va % 256
    elif opcode == '/':
        if input_val is not None:
            vm['a'] = input_val
        else:
            raise ValueError(WANTS_INPUT)
    elif opcode == 'v':
        return EXIT

    if vm['mem'][vm['c']] < 33 or vm['mem'][vm['c']] > 126:
        vm['a'] = va
        vm['c'] = vc
        vm['d'] = vd
        vm['mem'][vd] = vmd
        raise ValueError('Illegal ' + ('jump' if opcode == 'i' else 'write') + '!')

    vm['mem'][vm['c']] = ord(xlat2[vm['mem'][vm['c']] - 33])
    vm['c'] = (vm['c'] + 1) % 59049
    vm['d'] = (vm['d'] + 1) % 59049

    return output

p9 = [1, 9, 81, 729, 6561]
op_o = [
    [4, 3, 3, 1, 0, 0, 1, 0, 0],
    [4, 3, 5, 1, 0, 2, 1, 0, 2],
    [5, 5, 4, 2, 2, 1, 2, 2, 1],
    [4, 3, 3, 1, 0, 0, 7, 6, 6],
    [4, 3, 5, 1, 0, 2, 7, 6, 8],
    [5, 5, 4, 2, 2, 1, 8, 8, 7],
    [7, 6, 6, 7, 6, 6, 4, 3, 3],
    [7, 6, 8, 7, 6, 8, 4, 3, 5],
    [8, 8, 7, 8, 8, 7, 5, 5, 4]
]

def op(x, y):
    t = 0
    for j in range(5):
        t += op_o[(y // p9[j]) % 9][(x // p9[j]) % 9] * p9[j]
    return t

def execVM(vm, input_callback=None):
    output = ''
    while vm['c'] < len(vm['mem']):
        try:
            t = step(vm, input_callback()) if input_callback else step(vm)
            if t == EXIT:
                break
            if t is not None:
                output += chr(t)
        except ValueError as e:
            if str(e) == str(WANTS_INPUT):
                if input_callback is None:
                    break
            else:
                raise e
    return output

def appendAndPerform(vm, op_code, input_val = None, skip = False):
    l = len(vm['mem']) if skip else vm['c']
    t = (op_code - (l % 94) + 94) % 94
    if t < 33:
        t += 94
    vm['mem'].append(t)
    if not skip:
        step(vm, input_val)
    return chr(t)

def clone(vm):
    return {
        'a': vm['a'],
        'c': vm['c'],
        'd': vm['d'],
        'mem': list(vm['mem'])
    }

def decode(code, position):
    return decodeInt(ord(code), position)

def decodeInt(code, position):
    return xlat1[((code - 33 + position) % 94)]

def decodeNext(vm):
    return decodeInt(vm['mem'][vm['c']], vm['c'])

def normalize(code, allowWildcard=False):
    normalized = ''
    skipped = 0
    for i, char in enumerate(code):
        ct = ord(char)
        if ct < 127 and (ct > 32 or (allowWildcard and ct == 32)):
            normalized += char if char == ' ' else decodeInt(ct, i - skipped)
        else:
            skipped += 1
            normalized += char
    return normalized

def assemble(normalized, allowWildcard = False):
    code = ''
    skipped = 0
    for i, char in enumerate(normalized):
        ct = ord(char)
        if ct < 127 and (ct > 32 or (allowWildcard and ct == 32)):
            code += char if char == ' ' else encode(assembly[char], i - skipped)
        else:
            skipped += 1
            code += char
    return code

def rot(m):
    return (m // 3) + (m % 3) * 19683

def encode(code, position):
    return chr(encodeInt(code, position))

def encodeInt(code, position):
    t = (code - (position % 94) + 94) % 94
    if t < 33:
        t += 94
    return t

def validateCode(code, normalized = False, allowWildcard = False):
    if normalized:
        pattern = r'^[o*p/<vij ]*$' if allowWildcard else r'^[o*p/<vij]*$'
        import re
        return re.match(pattern, code) is not None
    else:
        return validateCode(normalize(code), True, allowWildcard)

def validate(code, normalized=False):
    trimmed = ''.join(char for char in code if 32 < ord(char) < 127)
    return validateCode(trimmed, normalized, False)

MALBOLGE_WANTS_INPUT    = WANTS_INPUT
MALBOLGE_OPC            = opc
MALBOLGE_OPCODES        = opcodes
MALBOLGE_ASSEMBLY       = assembly
MALBOLGE_LOAD_VM        = loadVM
MALBOLGE_STEP           = step
MALBOLGE_EXEC           = execVM
MALBOLGE_OP             = op
MALBOLGE_ROT            = rot
MALBOLGE_ENCODE         = encode
MALBOLGE_DECODE         = decode
MALBOLGE_APPEND_PERFORM = appendAndPerform
MALBOLGE_NORMALIZE      = normalize
MALBOLGE_ASSEMBLE       = assemble
MALBOLGE_EXIT           = EXIT