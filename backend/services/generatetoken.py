import jwt
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def create_jwt_token(email):
    algorithm =  os.getenv("ALGO_KEY")
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=5)  # expires in 5 days
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=algorithm)
    return token