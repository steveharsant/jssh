# Jump SSH

Seemless ssh through jumpboxes & bastion hosts

## Configuration & Usage

1. Add the following to the *top* of your ssh config file found at `~/.ssh/config`:

```config
Host *
  IgnoreUnknown JumpHost
```

> ***Note:*** The `IgnoreUnknown` option can take multiple values using comma sperated values

2. Add entries for the jumpboxes/bastion hosts. Minimum configuration needed is `Hostname` and `User`.

**Example:**

```config
Host myJumpHost
  Hostname 192.168.1.1
  User admin
```

3. Add the `JumpHost` option to the hosts that require a jumpbox for connections. This is the host that will receive an interactive shell.

> ***Note:*** If the hosts entry does not exist, create it. Minimum configuration needed is `Hostname`, `User` and `JumpHost`.

**Example:**

```config
Host myHost
  Hostname 192.168.1.20
  User admin
  IdentityFile ~/.ssh/my_keyfile
  JumpHost myJumpHost
```

4. Connect with `jssh` using: `/path/to/jssh myHost`

> ***Note:*** You can append `debug` to the above command for debugging information. No other options are available at this time


## Building

`jssh` is prebuilt for Windows and Linux x86 machines. For Mac's and/or ARM based machines, build a standalone binary with:

```shell
git clone https://github.com/steveharsant/jssh
cd jssh
pip install -r requirements.txt
pyinstaller --onefile ./jssh.py
```

The binary will be found in the `./dist` directory once built.
