#!/bin/python3

from subprocess import run as sub_run
import os


def execute_cmd(cmd) -> None:
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
            for cmd in cmd.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last cmd
                if cmd == cmd.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    subprocess.run(cmd.strip().split())
                except Exception:
                    print("msh: commmand not found: {}".format(cmd.strip()))

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

def main() -> None:

        while True:
            try:
                cmd = input(f"\n[{os.getcwd()}]$ ")

                if cmd.isspace() or cmd == "":
                    continue
                if cmd == "exit":
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


if '__main__' == __name__:
    main()
