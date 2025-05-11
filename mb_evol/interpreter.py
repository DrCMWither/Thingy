import sys

xlat1 = "+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI.v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha"
xlat2 = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@"

def malbolge_op(x, y):
    p9 = [1, 9, 81, 729, 6561]
    table = [
        [4, 3, 3, 1, 0, 0, 1, 0, 0],
        [4, 3, 5, 1, 0, 2, 1, 0, 2],
        [5, 5, 4, 2, 2, 1, 2, 2, 1],
        [4, 3, 3, 1, 0, 0, 7, 6, 6],
        [4, 3, 5, 1, 0, 2, 7, 6, 8],
        [5, 5, 4, 2, 2, 1, 8, 8, 7],
        [7, 6, 6, 7, 6, 6, 4, 3, 3],
        [7, 6, 8, 7, 6, 8, 4, 3, 5],
        [8, 8, 7, 8, 8, 7, 5, 5, 4],
    ]
    result = 0
    for i in range(5):
        result += table[y // p9[i] % 9][x // p9[i] % 9] * p9[i]
    return result

class MalbolgeInterpreter:
    def __init__(self, code):
        self.mem = [0] * 59049
        self.output = ""
        self.a = 0
        self.c = 0
        self.d = 0

        for i, char in enumerate(code):
            val = ord(char)
            if not (33 <= val <= 126):
                raise ValueError("Invalid character in code")
            decoded = xlat1[(val - 33 + i) % 94]
            if decoded not in "ji*p</vo":
                raise ValueError("Invalid Malbolge instruction")
            self.mem[i] = val

        for i in range(len(code), 59049):
            self.mem[i] = malbolge_op(self.mem[i - 1], self.mem[i - 2])

    def run(self):
        while True:
            val = self.mem[self.c]
            if not (33 <= val <= 126):
                self.advance()
                continue

            instr = xlat1[(val - 33 + self.c) % 94]

            if   instr == 'j':
                self.d = self.mem[self.d]
            elif instr == 'i':
                self.c = self.mem[self.d]
            elif instr == '*':
                self.mem[self.d] = self.mem[self.d] // 3 + (self.mem[self.d] % 3) * 19683
                self.a = self.mem[self.d]
            elif instr == 'p':
                self.mem[self.d] = malbolge_op(self.a, self.mem[self.d])
                self.a = self.mem[self.d]
            elif instr == '<':
                self.output += chr(self.a % 256)
            elif instr == '/':
                user_input = sys.stdin.read(1)
                self.a = ord(user_input) if user_input else 59048
            elif instr == 'v':
                break

            self.mem[self.c] = ord(xlat2[val - 33])
            self.advance()
        return self.output

    def advance(self):
        self.c = (self.c + 1) % 59049
        self.d = (self.d + 1) % 59049


code = "ov"


interpreter = MalbolgeInterpreter(code)


output = interpreter.run()


print(output)