import sys
from interpreter import MalbolgeInterpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py \"Your message here\"")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Target output: {target}")

    program = 0 ## use it later
    print("\nGenerated Malbolge program:\n")
    print(program)

    print("\nValidating output:")
    output = MalbolgeInterpreter(program).run()
    print(f"Output: {output}")

    if output != target:
        print(f"Output doesn't match target: {output} != {target}")
    else:
        print("Output matches the target!")

if __name__ == "__main__":
    main()
