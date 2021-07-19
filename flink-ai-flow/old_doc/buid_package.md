# Build Ai Flow From Source

## 1. install java8

**macOS**
```bash
brew cask install adoptopenjdk8
```
**Linux**
```bash
sudo apt-get install openjdk-8-jdk
```

## 2. install maven

**macOS**
```bash
brew install maven
```
**Linux**
```bash
sudo apt-get install maven
```
## 3. install Python3 pip

**macOS**
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
brew install python@2  # or python (Python 3)
```

**Linux**
```bash
sudo apt-get install  python3-dev python3-pip
```

## 4. build package

```bash
sh build_whl_package.sh
```

Finally you will find ai flow package in dist directory.