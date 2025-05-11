import random
import multiprocessing
from tqdm import tqdm
import generator as mb
import common as gc

toseed       = [mb.MALBOLGE_OPC['nop'], mb.MALBOLGE_OPC['rot'], mb.MALBOLGE_OPC['opr']]
toseed_norot = [mb.MALBOLGE_OPC['nop'], mb.MALBOLGE_OPC['opr']]

def generateBoilerplatte(pool):
    mvm = {
        'mem': 0,
        'str': '',
        'a': 0
    }
    mvm['str'] += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['nop'],  len(mvm['str']))
    mvm['str'] += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['movd'], len(mvm['str']))
    mvm['str'] += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['jump'], len(mvm['str']))

    for _ in range(37):
        op = pool.pop(0) if pool else random.choice(list(mb.MALBOLGE_OPCODES))
        mvm['str'] += mb.MALBOLGE_ENCODE(op, len(mvm['str']))

    mvm['str'] += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['halt'], len(mvm['str']))
    op = pool.pop(0) if pool else random.choice(list(mb.MALBOLGE_OPCODES))
    mvm['str'] += mb.MALBOLGE_ENCODE(op, len(mvm['str']))

    vm = mb.loadVM(mvm['str'], partially=True)
    mvm['mem'] = ord(mb.xlat2[ord(mvm['str'][-1]) - 33])
    return mvm

def perform_op_mvm(mvm, op, input_val=None):
    l = len(mvm['str'])
    t = (op - (l % 94) + 94) % 94
    if t < 33:
        t += 94
    mvm['str'] += chr(t)
    vm = mb.loadVM(mvm['str'], partially=True)
    if op == mb.MALBOLGE_OPC['rot']:
        mvm['a'] = mb.MALBOLGE_ROT(mvm['mem'])
    elif op == mb.MALBOLGE_OPC['opr']:
        mvm['a'] = mb.MALBOLGE_OP(mvm['a'], mvm['mem'])
    elif op == mb.MALBOLGE_OPC['in']:
        mvm['a'] = input_val
    mvm['mem'] = ord(mb.xlat2[t - 33])

def cloneMVM(mvm):
    return {
        'a': mvm['a'],
        'mem': mvm['mem'],
        'str': mvm['str']
    }

def nextWin(win, prop):
    ptr = 0
    while True:
        if len(win) == ptr:
            win.append(1)
            break
        win[ptr] += 1
        if win[ptr] == prop:
            win[ptr] = 0
            ptr += 1
        else:
            break

def generateStaticText(target_str, callback, random_pool_str):
    random_pool = gc.parseRandomPool(random_pool_str)
    gmvm = generateBoilerplatte(list(random_pool)) # Use a copy
    mvm = gmvm
    window = []
    norot = False
    target = gc.parseTargetString(target_str)

    for g in tqdm(range(len(target)), desc = "Generating Static Objects", unit = "step"):
        for g in range(len(target)): # Use enumerate(target) will lead to an error, for all range(len(arg)), preserved.
            callback({'progress': g / len(target)})
            if target[g] == -1:
                perform_op_mvm(mvm, mb.MALBOLGE_OPC['in'], target[g+1])
                gmvm = mvm
                g += 1
                continue
            elif target[g] == -2:
                perform_op_mvm(mvm, mb.MALBOLGE_OPC['rot'])
                gmvm = mvm
                continue
            elif target[g] == -3:
                norot = True
                continue

            while True:
                window.clear()
                while True:
                    mvm = cloneMVM(gmvm)
                    nextWin(window, 2 if norot else 3)
                    if len(window) == 14:
                        for _ in range(13):
                            perform_op_mvm(mvm, mb.MALBOLGE_OPC['nop'])
                        gmvm = mvm
                        break # inner while

                    found = False
                    for tt in range(len(window)):
                        if (mvm['a'] % 256) != target[g]:
                            op = (toseed_norot if norot else toseed)[window[tt]]
                            perform_op_mvm(mvm, op)

                        if (mvm['a'] % 256) == target[g]:
                            perform_op_mvm(mvm, mb.MALBOLGE_OPC['out'])
                            gmvm = mvm
                            norot = False
                            found = True
                            break # for tt
                    if found:
                        break # outer while
                if found:
                    break # ww loop

    if target:
        callback({'progress': len(target) / len(target)})
    perform_op_mvm(mvm, mb.MALBOLGE_OPC['halt'])
    return mvm['str']

def generateDynamicString(vm, target, callback):
    str_code = ''
    norot = False
    if not target:
        return ''

    parsed_target = gc.parseTargetString(target)
    for t in tqdm(range(len((parsed_target))), desc = "Generating Dynamic Objects", unit = "step"):
        for t in range(len(parsed_target)):
            callback({'progress': t / len(parsed_target)})
            if parsed_target[t] == -1:
                str_code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['in'], parsed_target[t+1])
                t += 1
            elif parsed_target[t] == -2:
                str_code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['rot'])
            elif parsed_target[t] == -3:
                norot = True
            else:
                str_code += generateDynamic(vm, parsed_target[t], norot)
                str_code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['out'])
                norot = False
        callback({'progress': len(parsed_target) / len(parsed_target)})
    return str_code

def generateDynamic(ovm, tc, norot):
    if ovm['d'] >= ovm['c']:
        raise ValueError('d must be smaller than c')
    if (ovm['a'] % 256) == tc:
        return ''

    gvm = {
        'a': ovm['a'],
        'c': ovm['c'],
        'd': ovm['d'],
        'mem': list(ovm['mem'][:ovm['c']])
    }
    window   = []
    gstr     = ''
    str_code = ''
    t        = 0
    tt       = 0

    while True:
        window.clear()
        while True:
            vm = mb.clone(gvm)
            str_code = gstr

            nextWin(window, 2 if norot else 3)
            if (vm['mem'][vm['d']] > vm['d'] and vm['mem'][vm['d']] < vm['c']):
                str_code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['movd'])
                gvm = vm
                gstr = str_code
                break  # inner while

            if len(window) == 14:
                for _ in range(13):
                    str_code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['nop'])
                gvm = vm
                gstr = str_code
                break # inner while

            found = False
            for tt in range(len(window)):
                if (vm['a'] % 256) != tc:
                    op = (toseed_norot if norot else toseed)[window[tt]]
                    str_code += mb.MALBOLGE_APPEND_PERFORM(vm, op)

                if (vm['a'] % 256) == tc:
                    ovm['a'] = vm['a']
                    ovm['c'] = vm['c']
                    ovm['d'] = vm['d']
                    ovm['mem'] = vm['mem']
                    return str_code
            if found:
                break # outer while
        if found:
            break # while True

def buildPrefix(mcode, canJump, bestWithoutJump, randomPool):
    tvm      = None
    lnow     = 0
    t        = 0
    op       = 0
    code     = ''
    ok       = False
    accessed = {}

    for char in mcode:
        code += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['nop'], len(code)) if char == ' ' else char

    for _ in range(len(code), 59049):
        code += mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['nop'], len(code))

    tvm = mb.loadVM(code, True)
    while tvm['c'] < len(tvm['mem']) and tvm['d'] < len(tvm['mem']) and mb.decodeNext(tvm) != '<' and mb.decodeNext(tvm) != '/' and mb.decodeNext(tvm) != 'v':
        accessed[tvm['c']] = 1
        if mb.decodeNext(tvm) != 'o':
            accessed[tvm['d']] = 1
        if mb.decodeNext(tvm) == 'i':
            accessed[tvm['mem'][tvm['d']]] = 1
        try:
            mb.step(tvm)
        except ValueError as e:
            lnow = -1
            break
        if tvm['d'] < tvm['c']:
            ok = True
            break
        if (tvm['c'] >= len(mcode)) and tvm['c'] not in accessed and tvm['mem'][tvm['d']] < tvm['d'] and tvm['mem'][tvm['d']] < tvm['c']:
            tvm['mem'][tvm['c']] = mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['movd'], tvm['c'])
            code = code[:tvm['c']] + chr(tvm['mem'][tvm['c']]) + code[tvm['c']+1:]
        elif canJump and (tvm['c'] >= len(mcode)) and tvm['c'] not in accessed and tvm['mem'][tvm['d']] > tvm['d'] and 33 <= tvm['mem'][tvm['mem'][tvm['d']]] <= 126 and max(lnow, tvm['mem'][tvm['d']] + 1, tvm['d']) < bestWithoutJump:
            tvm['mem'][tvm['c']] = mb.MALBOLGE_ENCODE(mb.MALBOLGE_OPC['jump'], tvm['c'])
            code = code[:tvm['c']] + chr(tvm['mem'][tvm['c']]) + code[tvm['c']+1:]

    if lnow != -1:
        lnow = len(accessed)
    else:
        lnow = 0

    temp_tvm = mb.loadVM(code, True)
    temp_tvm['c'] = 0
    while temp_tvm['c'] < lnow:
        accessed[temp_tvm['c']] = 1
        temp_tvm['c'] += 1

    if not canJump:
        hiscode = buildPrefix(mcode, True, lnow if lnow != -1 else float('inf'), randomPool)
        if (lnow == -1 or (hiscode and len(hiscode) <= lnow)):
            return hiscode
        return False

    if lnow == -1 or not ok:
        return False

    code = code[:lnow]
    ncode = ''
    pool = list(randomPool)
    for t in range(lnow):
        if t >= len(mcode) or mcode[t] == ' ':
            ncode += code[t] if t in accessed else mb.MALBOLGE_ENCODE(pool.pop(0) if pool else random.choice(list(mb.MALBOLGE_OPCODES)), t)
        else:
            ncode += code[t]
    return ncode

def generate(target, prefix, callback, randomPoolStr, prefix_normalized):
    code = None
    randomPool = gc.parseRandomPool(randomPoolStr)

    if prefix:
        code = buildPrefix(mb.MALBOLGE_ASSEMBLE(prefix) if prefix_normalized else prefix, None, None, randomPool)
        if code is False:
            return callback({'error': 'Failed to build custom prefix, try longer prefix.'})

        vm = mb.loadVM(code, True)
        mb.MALBOLGE_EXEC(vm)

        def generateDynamicSubstring(t_range):
            return generateDynamicString(vm, target[t_range[0]:t_range[1]], callback)

        num_processes = 4
        chunk_size = len(target) // num_processes
        ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]
        if len(target) % num_processes != 0:
            ranges[-1] = (ranges[-1][0], len(target))

        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.map(generateDynamicSubstring, ranges)

        for result in results:
            code += result

        code += mb.MALBOLGE_APPEND_PERFORM(vm, mb.MALBOLGE_OPC['halt'])

        callback({'result': code, 'final': True})

    else:
        code = generateStaticText(target, callback, randomPoolStr)
        callback({'result': code, 'final': True})

if __name__ == "__main__":
    print("Malbolge Code Generator (Linear)")
    print("Enter 'r' to execute Malbolge code, or 'g' to generate code.")
    mode = input("> ").lower()

    if mode == 'r':
        malbolge_code = input("Enter Malbolge code to run:\n")
        vm = mb.loadVM(malbolge_code)

        output = []
        def input_callback():
            return ord(input("Enter input character: "))

        try:
            result = mb.MALBOLGE_EXEC(vm, input_callback)
            print("Output:\n" + result)
        except ValueError as e:
            if str(e) == str(mb.MALBOLGE_WANTS_INPUT):
                print("Program expects input.")
            else:
                print(f"Error during execution: {e}")
    elif mode == 'g':
        target_string = input("Enter the target string to output: ")
        prefix = input("Enter an optional prefix (Malbolge assembly or raw code): ")
        prefix_normalized = input("Is the prefix in Malbolge assembly (y/n)? ").lower() == 'y'
        random_pool_str = input("Enter an optional random pool string: ")

        def progress_callback(info):
            if 'progress' in info:
                print(f"Progress: {info['progress']:.2%}", end='\r')
            elif 'result' in info:
                print("\nGenerated Malbolge code:")
                print(info['result'])
            elif 'final' in info:
                print("\nGeneration complete.")
            elif 'error' in info:
                print(f"\nError: {info['error']}")

        generate(target_string, prefix, progress_callback, random_pool_str, prefix_normalized)
    else:
        print("Invalid mode.")
