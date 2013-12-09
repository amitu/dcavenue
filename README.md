A simple django app to integrate with CCAvenue using "Advanced Site
Integration for Real Time Success Failure".

Since the app does not have any meaningful models or management command/template
tags etc, there is no reason to add "dcavenue" to INSTALLED_APPS if you are
using it with normal django app. If you are using it with importd project, it
may be required to allow views.py to be loaded, so either import dcavenue.views
from somewhere or put it in INSTALLED_APPS for simplicity.

Add "dcavenue" to installed apps. If it is importd app, mount dcavenue
on some URL, eg /dcavenue. If its a regular django app, url include
dcacenue.urls file at appropriate place.

Configure DCAVENUE["MERCHANT\_ID"] and DCAVENUE["WORKING\_KEY"] in settings.

In order to construct full url http headers are looked into, so make
sure they are working. This can be overridden by DOMAIN setting. If the
site is to be secure or not will be picked by request.is\_secure(), this
can be overridden by DCAVENUE["SECURE"] setting.

To initiate payment, redirect user to reverse("dcavenue-start") with URL
parameters, orderid, amount, and currency, and next. Once payment has
been successful, DCAVENUE["CALLBACK"] would be called with
success=True/False, orderid, next as parameters. Orderid is optional, if
not passed it will be calculated. The callback must return a HTTP
response after handling the payment/failure [could be html response or
could be http response redirect, recommended]. An optional callback
method is provided, which defaults to showing a success or failure
notification to the user, for debugging only.

In order to work java must be installed on your machine and path of
ccavutil.jar must be available as DCAVENUE["JAR"] setting.

An intermediary page is shown to user momentarily, the template used is
DCAVENUE\_TEMPLATE, this template will have access to orderid, amount,
currency, next. If this setting is not provided, a empty page will be
used, which will immediately redirect user to payment gateway.

There exists utility methods dcavenue.encRequest(amount, order\_id=None,
\*\*kw), 

Also there exists constants dcavenue.POST\_URL.

The project has dependency on importd, but it can work with regular django
projects not using importd too.

requirements.txt is only for development.