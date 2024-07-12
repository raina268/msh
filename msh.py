#!/bin/python3

from subprocess import run as sub_run
from sys import argv
import os
import re

__version__ = 1.0

ps1 = ""
alias = {}
history = []
h = os.uname()[1]
u = os.getlogin()

def cwd() -> str:
    # current working directory
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")

    if current_dir.startswith(home_dir):
        current_dir = current_dir.replace(home_dir, "~", 1)

    return current_dir

w = cwd()

def parse_ps1(line: str, from_conf: bool = False):
    # Parse PS1 from configuration file
    global ps1
    try:
        if from_conf:
            ps1 = line.split('=')[1].strip().strip('"').replace("{u}", u).replace("{h}", h).replace("{w}", w)
        else:
            ps1 = line.split('=')[1].strip('"').replace("{u}", u).replace("{h}", h).replace("{w}", w)
    except Exception as e:
        print(f"msh: error parsing PS1 '{line}': {e}")


def execute_cmd(cmd):
    """Execute commands and handle piping"""
    try:
        if "|" in cmd:
            # Save for restoring later on
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # First cmd takes input from stdin
            fdin = os.dup(s_in)

            # Iterate over all the cmds that are piped
            for cmmd in cmd.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # Restore stdout if this is the last cmd
                if cmmd == cmd.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # Redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    sub_run(cmmd.strip().split())
                except Exception:
                    print("msh: command not found: {}".format(cmmd.strip()))

            # Restore stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)
        elif cmd.strip().split("=")[0].split()[0] == "alias":
            msh_alias(cmd)
        elif cmd in alias:
            sub_run(alias[cmd].strip("\"\"").split())
        elif cmd.split()[0] == "echo":
            print(os.getenv(cmd.split()[1].lstrip("$")))
        else:
            sub_run(cmd.split(" "))
    except Exception as e:
        print("msh: command not found: {}".format(cmd))

def msh_alias(cmd) -> None:
    try:
        alias_name = cmd.strip().split("=")[0].split()[1]
        command = cmd.strip().split("=")[1]

        alias[alias_name] = command
    except:
        for k, v in alias.items():
            print(f"{k}={v}")

def parse_conf():
    file_path = os.path.expanduser("~/.mshrc")

    if not os.path.exists(file_path):
        print(f"msh: configuration file '{file_path}' not found.")
        print(f"creating {file_path}\n")

        with open(file_path, mode='w'):
            pass
        return

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('alias'):
                    msh_alias(line)
                elif line.startswith('PS1'):
                    parse_ps1(line, True)

    except Exception as e:
        print(f"msh: error parsing configuration file '{file_path}': {e}")


def msh_cd(path):
    """Convert to absolute path and change directory"""
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))

def arithmetic(exp) -> None:
    # Function to parse and evaluate arithmetic expressions
    exp = exp.strip()[1:]  # Remove '%' sign
    try:
        result = evaluate_expression(exp)
        print(result)
    except Exception as e:
        print(f"msh: error evaluating expression '{exp}': {e}")

def evaluate_expression(expression):
    # Function to evaluate arithmetic expressions without using eval()
    tokens = tokenize(expression)
    return evaluate(tokens)

def tokenize(expression):
    # Tokenizes the arithmetic expression
    tokens = re.findall(r'\d+|\+|-|\*|/', expression)
    return tokens

def evaluate(tokens):
    # Evaluates the arithmetic expression using a simple parser
    if not tokens:
        raise ValueError("Empty expression")

    if len(tokens) == 1:
        return int(tokens[0])

    if len(tokens) == 3:
        left = int(tokens[0])
        op = tokens[1]
        right = int(tokens[2])

        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ValueError("Division by zero")
            return left / right

    raise ValueError("Invalid expression format")

def main(prompt) -> None:
    # Main function to run the shell
    while True:
        try:
            cmd = input(prompt)

            if cmd.isspace() or cmd == "":
                continue
            elif cmd.startswith("%"):
                arithmetic(cmd)
            elif cmd == "exit":
                break
            elif cmd[:3] == "cd ":
                msh_cd(cmd[3:])
            elif cmd == "help":
                print("""msh: a simple and minimal shell written in Python""")
            else:
                execute_cmd(cmd)
        except KeyboardInterrupt as e:
            print(e)
            continue
        except EOFError:
            break

def usage() -> None:
    # Print usage information
    print("""msh, version %s

Usage:  msh [option] ...

Options:
        -h, --help          print this help message
        -p , --prompt       primary prompt

Shell options:
          PS1=primary prompt
                u for username
                h for hostname
                w for working directory

            eg: msh PS1="[{u}@{h} {w}]$ "
          """ % __version__)

def args() -> None:
    # Parse command-line arguments
    args = {
          "h": ["-h", "--help"]
          }

    if len(argv) == 2 and argv[1].startswith("PS1"):
        try:
            parse_ps1(argv[1])
            main(ps1)
        except IndexError:
            print(f"msh: unrecognized option '{argv[1]}'")
            print("Try 'msh --help' for more information.")
    elif len(argv) > 1:
        if argv[1] in args["h"]:
            usage()
        else:
            print(f"msh: unrecognized option '{argv[1]}'")
            print("Try 'msh --help' for more information.")
    else:
        main(ps1)

if __name__ == '__main__':
    parse_conf()  # Load configuration on startup
    args()
