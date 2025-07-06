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
            "visit_id": "123",
            "patient_id": "12",
            "doctor_id": "23"
        }

    @patch("stripe.checkout.Session.create")
    @patch("payments.models.Payments.objects.create")
    def test_create_checkout_session_success(self, mock_payment_create, mock_stripe_create):
        mock_stripe_create.return_value.url = "https://checkout.stripe.com/test_session"
        mock_stripe_create.return_value.id = "cs_test_session_123"

        mock_payment_create.return_value = None

        response = self.client.post(
            reverse("create-checkout-session"),
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )

        mock_stripe_create.assert_called_once()
        mock_payment_create.assert_called_once_with(
            patient_id="12",
            doctor_id="23",
            title="Test Service",
            price=100.0,
            stripe_session_id="cs_test_session_123",
            visit_id="123",
            is_completed=False
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

    @patch("stripe.checkout.Session.create")
    def test_stripe_create_called_with_correct_params(self, mock_stripe_create):
        mock_stripe_create.return_value.url = "https://checkout.stripe.com/test_session"

        self.client.post(
            reverse("create-checkout-session"),
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )
        mock_stripe_create.assert_called_once()
        _, kwargs = mock_stripe_create.call_args

        self.assertEqual(kwargs["payment_method_types"], ['card'])
        self.assertEqual(kwargs["line_items"][0]["price_data"]["unit_amount"], 10000)
        self.assertEqual(kwargs["metadata"]["visit_id"], self.valid_data["visit_id"])