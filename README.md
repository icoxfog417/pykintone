# pykintone

Python library to access [kintone](https://kintone.cybozu.com).

```python
import pykintone

r = pykintone.app("kintone domain", "app id", "api token").select("updated_time > NOW()")
if r.ok:
    records = r.records
```

## Quick Start

```
pip install pykintone
```

## Feature

**Basic operation**

* create
* read
* update
* delete

**Record and model mapping**

```python
import pykintone
from pykintone import model


class Person(model.kintoneModel):

    def __init__(self):
        super(Person, self).__init__()
        self.last_name = ""
        self.first_name = ""


app = pykintone.load("path_to_account_setting").app()
persons = app.select().models(Person)

someone = persons[0]
someone.last_name = "xxx"
app.update(someone)

```

**File Field**

```python
import pykintone
from pykintone import model
import pykintone.structure_field as sf


class MyFolder(model.kintoneModel):

    def __init__(self):
        super(MyFolder, self).__init__()
        self.files = [sf.File()]


app = pykintone.load("path_to_account_setting").app()
myfiles = ["note.txt", "image.png"]

folder = MyFolder()
folder.files = [sf.File.upload(f, app) for f in myfiles]

result = app.create(folder)
record = app.get(result.record_id).model(MyFolder)
files = [f.download(app) for f in record.files]
```

**Create application**

```python
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.view import View

account = pykintone.load("path_to_account_setting").account

with Administrator(account) as admin:
    # create application
    created = admin.create_application("my_application")

    # create form
    f1 = ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "Title")
    f2 = ff.BaseFormField.create("MULTI_LINE_TEXT", "description", "Desc")
    admin.form().add([f1, f2])

    # create view
    view = View.create("mylist", ["title", "description"])
    admin.view().update(view)
```


## Installation Detail

You can download from [pypi](https://pypi.python.org/pypi/pykintone).

```
pip install pykintone
```

`pykintone` works on Python3, and it depends on below libraries.

* [PyYAML](http://pyyaml.org/wiki/PyYAML)
* [requests](http://docs.python-requests.org/en/latest/)
* ([enum34](https://pypi.python.org/pypi/enum34)) for Python2

You can write account setting file as below (yaml format).

```
domain: xxx
login:
    id: user_id
    password: password
basic:
    id: basic_id
    password: password
apps:
    test:
        id: 1
```

Of course you can use api_token. 

```
domain: xxx
apps:
    test:
        id: 1
        api_token: xxxx
```

## Test

You have to create test application on kintone, and you can use `tests/pykintoneTest.zip` (application template) to do it.
