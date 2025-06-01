import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse


class TestNotifyStripeView(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('stripe-webhook')
        self.valid_payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "visit_id": "123"
                    }
                }
            }
        })
        self.charge_payload = json.dumps({
            "type": "charge.updated",
            "data": {
                "object": {
                    "id": "ch_test123"
                }
            }
        })
        self.signature = "test_signature"

    @patch('stripe.Webhook.construct_event')
    def test_successful_checkout_session_completed(self, mock_construct):
        response = self.client.post(
            self.webhook_url,
            data=self.valid_payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )

        self.assertEqual(response.status_code, 200)
        mock_construct.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    @patch('requests.patch')
    def test_failed_visit_update(self, mock_patch, mock_construct):
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "visit_id": "123"
                    }
                }
            }
        }
        mock_patch.return_value.status_code = 404
        mock_patch.return_value.text = "Visit not found"

        response = self.client.post(
            self.webhook_url,
            data=self.valid_payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )

        self.assertEqual(response.status_code, 200)
        mock_patch.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    @patch('requests.patch')
    def test_missing_visit_id_in_metadata(self, mock_patch, mock_construct):
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {}
                }
            }
        }

        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {"object": {"metadata": {}}}
        })
        response = self.client.post(
            self.webhook_url,
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )

        self.assertEqual(response.status_code, 200)
        mock_patch.assert_not_called()