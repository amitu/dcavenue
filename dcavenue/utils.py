import uuid
import zlib
import commands
from pprint import pformat

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse


def generate_order_id():
    return uuid.uuid4().get_hex()


def get_redirect_url(request):
    url = "%s%s" % (settings.DOMAIN, reverse("dcavenue-callback"))
    if request.is_secure():
        return "https://%s" % (url, )
    else:
        return "http://%s" % (url, )


def checksum(redirect_url, amount, order_id):
    # "$MerchantId|$OrderId|$Amount|$redirectUrl|$WorkingKey"

    data = "%s|%s|%s|%s|%s" % (
        settings.DCAVENUE["MERCHANT_ID"], order_id, amount,
        redirect_url, settings.DCAVENUE["WORKING_KEY"]
    )

    csum = zlib.adler32(data, 1)

    if csum < 0:
        csum += 2 ** 32

    return csum


def enc_request(request, order_id):
    amount = request.REQUEST["Amount"]

    redirect_url = get_redirect_url(request)

    g = request.GET.get

    cca_request = "&".join(
        [
            "Merchant_Id=%s" % settings.DCAVENUE["MERCHANT_ID"],
            "Amount=%s" % amount,
            "Order_Id=%s" % order_id,
            "Redirect_Url=%s" % redirect_url,
            "billing_cust_name=%s" % g("billing_cust_name", ""),
            "billing_cust_address=%s" % g("billing_cust_address", ""),
            "billing_cust_country=%s" % g("billing_cust_country", ""),
            "billing_cust_state=%s" % g("billing_cust_state", ""),
            "billing_cust_city=%s" % g("billing_cust_city", ""),
            "billing_zip_code=%s" % g("billing_zip_code", ""),
            "billing_cust_tel=%s" % g("billing_cust_tel", ""),
            "billing_cust_email=%s" % g("billing_cust_email", ""),
            "delivery_cust_name=%s" % g("delivery_cust_name", ""),
            "delivery_cust_address=%s" % g("delivery_cust_address", ""),
            "delivery_cust_country=%s" % g("delivery_cust_country", ""),
            "delivery_cust_state=%s" % g("delivery_cust_state", ""),
            "delivery_cust_city=%s" % g("delivery_cust_city", ""),
            "delivery_zip_code=%s" % g("delivery_zip_code", ""),
            "delivery_cust_tel=%s" % g("delivery_cust_tel", ""),
            "billing_cust_notes=%s" % g("billing_cust_notes", ""),
            "Checksum=%s" % checksum(redirect_url, amount, order_id)
        ]
    )

    return commands.getoutput(
        '%s -jar %s %s "%s" enc' % (
            settings.DCAVENUE.get("JAVA", "java"), settings.DCAVENUE["JAR"],
            settings.DCAVENUE["WORKING_KEY"], cca_request
        )
    )


#noinspection PyTypeChecker
def verify_checksum(data):
    # "$MerchantId|$OrderId|$Amount|$AuthDesc|$WorkingKey";
    inp = "%s|%s|%s|%s|%s" % (
        settings.DCAVENUE["MERCHANT_ID"], data["Order_Id"], data["Amount"],
        data["AuthDesc"], settings.DCAVENUE["WORKING_KEY"]
    )

    csum = zlib.adler32(inp, 1)

    if csum < 0:
        csum += 2 ** 32

    return str(csum) == data['Checksum']


def dec_response(request, response):
    response = commands.getoutput(
        '%s -jar %s %s "%s" dec' % (
            settings.DCAVENUE.get("JAVA", "java"), settings.DCAVENUE["JAR"],
            settings.DCAVENUE["WORKING_KEY"], response
        )
    )

    data = dict(
        part.split("=", 1) for part in response.split("&")
    )

    if not verify_checksum(data):
        return None

    return data


def default_callback(request, data):
    return HttpResponse(
        """
            <html>
                <body>
                    %s
                </body>
            </html>
        """ % pformat(data)
    )