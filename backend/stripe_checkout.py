import os
import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Remplacez par votre clé secrète Stripe (test ou live)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_votre_cle_secrete")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_votre_cle_publique")
stripe.api_key = STRIPE_SECRET_KEY

@app.post("/create-checkout-session")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': 'Abonnement Premium'},
                    'unit_amount': 999,  # 9,99€ en centimes
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8080/abonnement.html?success=true',
            cancel_url='http://localhost:8080/abonnement.html?canceled=true',
        )
        return JSONResponse({"id": session.id, "publicKey": STRIPE_PUBLIC_KEY})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
