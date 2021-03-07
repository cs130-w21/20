# StockMeetsBagel

[![Build Status](https://travis-ci.com/cs130-w21/20.svg?branch=master)](https://travis-ci.com/cs130-w21/20)
[![Release](https://img.shields.io/github/v/release/cs130-w21/20?label=release)](https://github.com/cs130-w21/20/releases/latest)

See our [about page](https://github.com/cs130-w21/20/wiki/About-StockMeetsBagel).

## Setup
It is recommended to install dependencies for this project in a virtual environment. Python 3 comes with `venv`, while Python 2 needs `virtualenv`. Instructions here are from [Flask's docs](https://flask.palletsprojects.com/en/1.1.x/installation/#python-version).

### Create an environment
On Unix machines, run the following in the project folder:

```
$ mkdir venv
$ python3 -m venv venv
```

On Windows, run the following in the project folder (Powershell):
```
> mkdir venv
> py -3 -m venv venv
```

If you are using Python 2, run this instead:
```
$ mkdir venv
$ python2 -m virtualenv venv
```

### Activate the environment
Before installing dependencies, activate the created environment:
```
$ . venv/bin/activate
```

On Windows:
```
> venv\Scripts\activate
```

### Install dependencies
Within the activated environment, run the following command to install dependencies (Windows/Unix):
```
$ pip install -r requirements.txt
```

This will install Flask with optional dependencies in your activated environment. If you do not need optional dependencies listed in the requirements file, you can edit `requirements.txt` before installing.

### Before Running
If you are running the application for the first time, you will need to initialize the database. Run the following within `venv` to initialize the database:
```
$ flask init-db
```
