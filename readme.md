
# minimal shell

a simple and minimal shell written in python with piping support

Note: This is not meant to be a replacement for your daily driver. Though, technically you can use it if you want.

# config file

```bash

alias ls="ls -alh --color"

PS1 = "$ "

! comments

HISSIZE = 1000
HISFILE = $HOME/.msh_his
```

# usage

```bash

$ python3 msh.py

# or

$ ./msh.py

```

```bash

msh, version 1.0

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

```
    



# TODO

implement history 
