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

    return zlib.adler32(data, 1)


def enc_request(request, order_id):
    amount = request.REQUEST["Amount"]

    redirect_url = get_redirect_url(request)

    cca_request = "Merchant_Id=%s&Order_Id=%s&Redirect_Url=%s" % (
        settings.DCAVENUE["MERCHANT_ID"], order_id, redirect_url,
    )

    cca_request = "%s&%s" % (
        cca_request, "&".join(
            "%s=%s" % (k, v) for k, v in request.REQUEST.items()
        )
    )

    cca_request = "%s&TxnType=A&actionID=TXN&Checksum=%s" % (
        cca_request, checksum(redirect_url, amount, order_id)
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
    data = "%s|%s|%s|%s|%s" % (
        settings.DCAVENUE["MERCHANT_ID"], data["OrderId"], data["Amount"],
        data["AuthDesc"], settings.DCAVENUE["WORKING_KEY"]
    )
    return zlib.adler32(data, 1) == data['Checksum']


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