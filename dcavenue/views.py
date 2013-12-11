from importd import d

from django.core.urlresolvers import reverse, get_mod_func
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from dcavenue.utils import generate_order_id, enc_request, dec_response
from dcavenue import POST_URL


@d("/", name="dcavenue-index")
def index(request):
    return HttpResponse(
        "<a href='%s'>start</a>" % (
            reverse("dcavenue-start") + "?Amount=10.00",
        )
    )


@d("/start/", name="dcavenue-start")
def start(request):
    order_id = request.REQUEST.get("Order_Id")
    if not order_id:
        order_id = generate_order_id()
    enc_request_data = enc_request(request, order_id=order_id)
    request.session["dcavenue_order_id"] = order_id

    return HttpResponse(
        """
            <html>
                <head><title>Redirecting...</title></head>
                <body>
                    <form method="post" name="redirect" action="%s">
                        <input type="hidden" name="encRequest" value="%s">
                        <input type="hidden" name="Merchant_Id" value="%s">
                    </form>
                </body>
                <script language='javascript'>
                    document.redirect.submit();
                </script>
            </html>
        """ % (POST_URL, enc_request_data, settings.DCAVENUE["MERCHANT_ID"])
    )


@csrf_exempt
@d("/callback/", name="dcavenue-callback")
def callback(request):
    enc_response = request.REQUEST["encResponse"]
    if not enc_response:
        raise d.Http404("No encResponse")

    data = dec_response(request, enc_response)

    if not data:
        raise Http404("Checksum Failed")

    order_id = request.session["dcavenue_order_id"]

    if order_id:
        del request.session["dcavenue_order_id"]
    else:
        raise Http404("No order id in session")

    if order_id != data["Order_Id"]:
        raise Http404("Invalid orderid")

    cb_module, cb_method = get_mod_func(
        settings.DCAVENUE.get("CALLBACK", "dcavenue.utils.default_callback")
    )
    cb = getattr(__import__(cb_module, {}, {}, ['']), cb_method)

    return cb(request, data)

