#!/bin/python3

from subprocess import run as sub_run
from sys import argv
import os


__version__ = 1.0


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


def execute_cmd(cmd):
    """execute commands and handle piping"""
    try:
        if "|" in cmd:
            # save for restoring later on
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # first cmd takes cmdut from stdin
            fdin = os.dup(s_in)

            # iterate over all the cmds that are piped
            for cmmd in cmd.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last cmd
                if cmmd == cmd.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    sub_run(cmmd.strip().split())
                except Exception:
                    print("msh: commmand not found: {}".format(cmmd.strip()))

            # restore stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)
        else:
            sub_run(cmd.split(" "))
    except Exception:
        print("msh: commmand not found: {}".format(cmd))

def msh_cd(path):
    """convert to absolute path and change directory"""
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))


def arithmetic(exp) -> None:
    exp = exp.strip()

    if ["+","-","*","/"] in exp:
        print(exp)
    else:
        print("psh: invalid arithmetic expression")




def main(PS1: str = "") -> None:
        pass

        while True:
            try:
                cmd = input(PS1)

                if cmd.isspace() or cmd == "":
                    continue
                elif cmd.startswith("%"):
                    arithmetic(cmd[1:])
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

#def parse_conf(file: str) -> None:
#    if os.path.isfile(file) and file.endswith(".msh"):
#        pass
#    else:
#        pass

def usage() -> None:
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

    args = {
#         "c": ["-c","--config"],
          "h": ["-h", "--help"]
          }


    if len(argv) == 2 and argv[1].startswith("PS1"):
        try:
            PS1 = f"{argv[1].split("=")[1]}".replace("{u}",u).replace("{h}",h).replace("{w}",w)
            
            main(PS1)
        except IndexError:
            print(f"msh: unrecognized option '{argv[1]}'")
            print("Try 'msh --help' for more information.")
    elif len(argv) > 1:

        if (argv[1] in args["h"]):
            usage()

        else:

            print(f"msh: unrecognized option '{argv[1]}'")
            print("Try 'msh --help' for more information.")
    else:
        
        main()






if '__main__' == __name__:
    args()
