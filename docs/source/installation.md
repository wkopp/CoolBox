# Installation

Recommend use [conda](https://docs.conda.io/en/latest/miniconda.html) to manage environments.

## Install from bioconda channel

```bash
$ conda install -c bioconda coolbox
```

## Install from source

```bash
$ git clone https://github.com/GangCaoLab/CoolBox.git
$ cd CoolBox
$ conda env create --file environment.yml
$ python -m pip install . --no-deps -vv
```

## For Windows Users

CoolBox not support run on Windows natively for now.
But you can use the WSL(Windows Subsystem for Linux) to run it.
See [this](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

Or, you can choice to use docker on Windows.

## Using Docker

Pull the CoolBox docker image:

```
$ docker pull nanguage/coolbox
```

Run a container, with mount current directory in file system to the '/data' in the container.
And binding the container port 8888(jupyter default port) to the host port 9000:

```
$ docker run -ti -p 9000:8888 nanguage/coolbox:latest
```

Then run jupyter notebook in the container:

```
$ jupyter notebook --ip=0.0.0.0 --allow-root
```