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

### Record and model mapping

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

Of course you can use every basic operation.

* create
* read
* update
* delete


## File Field

(You have to prepare the kintone Application that has `my_files` field as below.)

```python
import pykintone
from pykintone import model
import pykintone.structure_field as sf


class MyFolder(model.kintoneModel):

    def __init__(self):
        super(MyFolder, self).__init__()
        self.my_files = [sf.File()]


app = pykintone.load("path_to_account_setting").app()
my_files = ["note.txt", "image.png"]

folder = MyFolder()
folder.my_files = [sf.File.upload(f, app) for f in my_files]

result = app.create(folder)
record = app.get(result.record_id).model(MyFolder)
files = [f.download(app) for f in record.my_files]
```

## Application Administration

```python
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.view import View

kintone = pykintone.load("path_to_account_setting")

with kintone.administration().transaction() as admin:
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

### User API

```python
import pykintone

export_api = pykintone.load("path_to_account_setting").user_api().for_exporting
users = export_api.get_users().users
```

Export

* users
* user's organizations and titles
* user's groups

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
        token: xxxx
```

## Test

You have to create test application on kintone, and you can use `tests/pykintoneTest.zip` (application template) to do it.
