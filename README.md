# pykintone

Python library to access [kintone](https://kintone.cybozu.com).

```python
import pykintone

r = pykintone.app("kintone domain", "app id", "app token").select("updated_time > NOW()")
if r.ok:
    records = r.records
```

## Feature

* create
* read
* update
* delete

## Installation

You can download from [pypi](https://pypi.python.org/pypi/pykintone).

```
pip install pykintone
```

`pykintone` works on Python3, and it depends on below libraries.

* [PyYAML](http://pyyaml.org/wiki/PyYAML)
* [requests](http://docs.python-requests.org/en/latest/)
