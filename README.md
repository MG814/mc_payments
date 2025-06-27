[![codecov](https://codecov.io/gh/MG814/mc_payments/graph/badge.svg?token=V5YS70GDQJ)](https://codecov.io/gh/MG814/mc_payments)

# Payments Microservice

### Overview
The Payments microservice is a core component of the MediCare project, responsible for handling payment processing through integration with Stripe payment gateway. This service manages the complete payment flow from receiving payment amount data from the visits microservice to processing payments and sending confirmation responses back.

### Architecture
This microservice operates as part of a distributed system architecture, communicating with:
- **Visits microservice**: Receives payment amount data and sends payment confirmation
- **Stripe API**: Processes actual payment transactions
- **Redis**: Handles task queuing and caching

### Key Features
- Secure payment processing via Stripe integration
- Asynchronous task processing with Celery
- Automated invoice email delivery after successful payments
- RESTful API endpoints for payment operations

## 🛠 Technologies

- **python 3.13**
- **django 5.1**
- **psycopg2-binary 2.9.10**
- **django-environ 0.11.2** 
- **requests 2.32.3**
- **coverage 7.6.1** 
- **bandit 1.7.9** 
- **ruff 0.6.3** 
- **safety 3.2.7** 
- **stripe 11.1.1**

### Setup

#### 1. Clone the repository

```bash
git clone https://github.com/MG814/mc_payments.git
cd mc_payments
```

#### 2. Running the entire application:

```bash
docker-compose up --build
```

#### 3. Migrations (in a separate terminal):

```bash
docker-compose exec web-payments python src/manage.py migrate
```