import jwt
import os
from dotenv import load_dotenv
from db.mongo import User_detail

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

async def validate_token(payload):
    algorithm =  os.getenv("ALGO_KEY")
    try:
        print(payload)
        token_payload = jwt.decode(payload, SECRET_KEY, algorithms=[algorithm])

        email = token_payload.get("email")
        print("email",email)
        if not email:
            return {"message": "Invalid token", "status": 403}

        # Check user in DB
        existing_user = await User_detail.find_one({"email": email})
        print(existing_user)
        if not existing_user:
            return {"message": "User not found", "status": 404}

        return {
            "message": "Token validated successfully",
            "email": email,
            "name": existing_user["name"],
            "status": 200,
        }

    except jwt.ExpiredSignatureError:
        return {"message": "Token expired, please login again", "status": 401}
    except jwt.InvalidTokenError:
        return {"message": "Invalid token", "status": 403}
    except Exception as e:
        print("Unexpected error:", e)
        return {"message": "Please login again", "status": 404}
