import json

import stripe

from django.http import JsonResponse

from django.http import HttpResponse
import requests

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from payments.email_utils import send_email
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

#Zamiast django dać DRF
@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8500"

        try:
            request_data = json.loads(request.body)
            price = request_data.get('price')
            name = request_data.get('name')
            visit_id = request_data.get('visit_id')

            if price is None:
                return JsonResponse({'error': 'Price is required'}, status=400)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': name,
                            },
                            'unit_amount': int(float(price) * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/admin/',
                cancel_url=YOUR_DOMAIN + '/admin/',
                metadata={
                    'visit_id': visit_id
                }
            )

            return JsonResponse({'url': checkout_session.url})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def notify_stripe_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.ENDPOINT_SECRET
        )
    except (stripe.error.StripeError, KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
        logging.error(f'SignatureVerifcationError: {str(e)}')
        # Invalid signature
        return HttpResponse(status=400)

    try:
        if event["type"] == "checkout.session.completed":
            visit_id = event['data']['object']['metadata']['visit_id']

            api_gateway_url = f'http://web-visits:8600/visits/{visit_id}/'

            data = {'is_paid': True}

            response = requests.patch(api_gateway_url, json=data)

            if response.status_code == 200:
                logging.info(f"Visit {visit_id} updated to paid successfully.")
            else:
                logging.error(f"Failed to update visit {visit_id}: {response.text}")

    except (stripe.error.StripeError, KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
        logging.error(f'CheckoutSessionIncomplete: {str(e)}')

    try:
        if event["type"] == 'charge.updated':
            charge = stripe.Charge.retrieve(
                event["data"]["object"]["id"],
            )
            patient_email = charge.get('billing_details').get('email')
            print(patient_email)
            try:
                send_email.delay(receipt_url=charge.get('receipt_url'), patient_email=patient_email)
            except (KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
                logging.error(f'EmailNotSent: {str(e)}')
    except (stripe.error.StripeError, KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
        logging.error(f'ChargeNotUpdated: {str(e)}')

    return HttpResponse(status=200)
