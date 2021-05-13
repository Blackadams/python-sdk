# Elarian Python SDK

> The wrapper provides convenient access to the Elarian APIs.
>
> **Project Status: Still under ACTIVE DEVELOPMENT, APIs are unstable and may change at any time until release of v1.0.0.**

[![PyPi version](https://pypip.in/v/elarian/badge.png)](https://pypi.org/project/elarian/)

## Documentation

Take a look at the [API docs here](http://docs.elarian.com).


## Install

You can install the package from [pypi](https://pypi.org/project/elarian) by running: 

```bash
$ pip install elarian
```

## Usage

```python
from elarian import Elarian, Customer

elarian = Elarian(api_key="test_api_key", org_id="test_org", app_id="test_app_id")
customer = Customer(client=elarian, number="+254709759881")

await elarian.connect()

# get customer state
resp = await customer.get_state()

print(resp)

```

## Development

```bash
$ git clone https://github.com/ElarianLtd/python-sdk.git
$ cd python-sdk
$ python setup.py
```


Run all tests:

Update the following params in your `.env` file then run `python -m unittest discover -v`

```bash
# TODO
```

## Issues

If you find a bug, please file an issue on [our issue tracker on GitHub](https://github.com/ElarianLtd/javascript-sdk/issues).