import json
from unittest import TestCase

from django.urls import reverse
from django.test import Client
from unittest.mock import patch


class TestCreateCheckoutSessionView(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_data = {
            "price": "100.00",
            "name": "Test Service",
            "visit_id": "123"
        }

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_success(self, mock_stripe_create):
        mock_stripe_create.return_value.url = "https://checkout.stripe.com/test_session"

        response = self.client.post(
            reverse("create-checkout-session"),
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("url", response.json())
        self.assertEqual(response.json()["url"], "https://checkout.stripe.com/test_session")

    def test_create_checkout_session_missing_price(self):
        del self.valid_data["price"]

        response = self.client.post(
            reverse("create-checkout-session"),
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Price is required")

    @patch("stripe.checkout.Session.create", side_effect=Exception("Stripe error"))
    def test_create_checkout_session_exception(self):
        response = self.client.post(
            reverse("create-checkout-session"),
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Stripe error")
