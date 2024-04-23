Undefiner Telegram Bot
=== 

## Prerequisites

You should install `g++` and `clang-format`. Installation depends on your distribution.
To install these packages on Ubuntu/Debian (and derivatives):
```console
# apt install clang-format g++
```

## Installation

```console
$ git clone --depth=1 https://github.com/Aqendo/undefiner
$ python -m venv venv
$ source venv/bin/activate
$ pip install aiogram
$ cp .env{.example,}
$ nano .env
$ mkdir cpps
$ python main.py
```

## LICENSE

This code is distributed under **MIT License**. [LICENSE](/LICENSE)
