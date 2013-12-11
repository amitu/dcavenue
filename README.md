A simple django app to integrate with CCAvenue using **Advanced Site
Integration for Real Time Success Failure**.

# installation

```shell
$ pip install dcavenue
```

Add "dcavenue" to *INSTALLED_APPS*.

# settings

```python

# in settings.py

DCAVENUE = {
    "MERCHANT\_ID": "<your merchant key>",
    "WORKING\_KEY": "<32 bit working key>", # len must be 32
}
```

Configure DCAVENUE["MERCHANT\_ID"] and DCAVENUE["WORKING\_KEY"] in settings.

In order to construct full url http headers are looked into, so make
sure they are working. This can be overridden by DOMAIN setting. If the
site is to be secure or not will be picked by request.is\_secure(), this
can be overridden by DCAVENUE["SECURE"] setting.

# usage

To initiate payment, redirect user to *reverse("dcavenue-start")* with GET
parameters, Order_Id, Amount, and Currency. Once payment has been successful,
DCAVENUE["CALLBACK"] would be called with data dict as parameter. Order_Od is
optional, if not passed it will be calculated. The callback must return a HTTP
response after handling the payment/failure [could be html response or could be
http response redirect, recommended]. An optional callback method is provided,
which defaults to showing a success or failure notification to the user, for
debugging only.

In order to work java must be installed on your machine and path of
ccavutil.jar must be available as DCAVENUE["JAR"] setting. CCAvenue uses AES
to encrypt the data before sending on wire, the jar file is needed for that. It
is quite possible to implement encryption by using python equivalent instead of
calling jar file, but it is not yet done.

An intermediary page is shown to user momentarily, the template used is
DCAVENUE["TEMPLATE"], this template will have access to orderid, amount,
and currency. If this setting is not provided, a empty page will be
used, which will immediately redirect user to payment gateway. If template is
provided, it must be "inspired" by the empty page as found in views.py.

# notes

The project has dependency on importd, but it can work with regular django
projects not using importd too.

requirements.txt is only for development.

This is only tested with Indian merchant accounts on ccavenue.