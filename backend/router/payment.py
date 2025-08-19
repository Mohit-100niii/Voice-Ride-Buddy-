from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
from db.mongo import User_Ride_detail, User_last_Ride
import datetime

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()


class PaymentRequest(BaseModel):
    fare: float
    pickup: str
    dropup: str
    date: str  # will parse "2025-08-13"
    time: str  # will parse "23:00"


@router.post("/payment")
async def ride_payment(data: PaymentRequest):
    try:
        print("Payment data", data)

        if not data.fare or not data.pickup or not data.dropup:
            return {"status": 404, "message": "Missing required fields"}

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": "Ride Booking",
                            "description": f"Pickup: {data.pickup}\n"
                            f"Dropoff: {data.dropup}\n"
                            f"Fare: ₹{data.fare}\n"
                            f"Date: {data.date}\n"
                            f"Time: {data.time}",
                        },
                        "unit_amount": int(float(data.fare) * 100),
                    },
                    "quantity": 1,
                }
            ],
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            metadata={
                "pickup": data.pickup,
                "dropup": data.dropup,
                "date": data.date,
                "fare": str(data.fare),
                "time": data.time,
            },
        )

        return {
            "status": 200,
            "message": "Checkout session created successfully",
            "url": session.url,
        }

    except Exception as e:
        print("Payment error:", e)
        return {"status": 500, "message": str(e)}


endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=stripe_signature, secret=endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        print("Webhook signature verification failed", e)
        return {"status": 400}

    # 🎯 Handle successful payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Payment succeeded. Session:", session["id"])

        # Access metadata (you stored pickup/drop/fare in metadata or line_items)
        customer_email = session.get("customer_details", {}).get("email")
        pickup = session.get("metadata", {}).get("pickup")
        dropup = session.get("metadata", {}).get("dropup")
        amount_paid = session["amount_total"] / 100  # Convert paise to INR
        date = session.get("metadata", {}).get("date")
        time = session.get("metadata", {}).get("time")
        print(pickup, dropup, amount_paid)

        print("✅ Ride stored for", customer_email)
        User_Exist = User_Ride_detail.find_one({"email": customer_email})
        ride_data = {
            "pickup": pickup,
            "dropup": dropup,
            "amount": amount_paid,
            "date": date,
            "time": time,
        }
        if User_Exist:
            await User_Ride_detail.update_one(
                {"email": customer_email},
                {"$push": {"ride_details": ride_data}},
                upsert=True,
            )

            await User_last_Ride.update_one(
                {"email": customer_email},
                {"$set": {"last_ride": ride_data}},
                upsert=True,
            )

        else:
            await User_Ride_detail.insert_one(
                {"email": customer_email, "ride_details": [ride_data]}
            )

            await User_last_Ride.insert_one(
                {"email": customer_email}, {"last_ride": ride_data}
            )

    return {"status": 200}
