import bcrypt
from fastapi import APIRouter, Response
from pydantic import BaseModel, EmailStr
from db.mongo import User_detail
from services.generatetoken import create_jwt_token
from fastapi import Request, HTTPException
from services.validatetoken import validate_token
from fastapi.responses import JSONResponse

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    country: str


class LoginRequired(BaseModel):
    email: EmailStr
    password: str
    
class RequestProfile(BaseModel):
    token:str


@router.post("/register")
async def user_registration(data: RegisterRequest):
    try:
        existing_user = await User_detail.find_one({"email": data.email})
        if existing_user:
            return {"message": "User already exists"}
        hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
        user_data = {
            "name": data.name,
            "email": data.email,
            "password": hashed_password.decode("utf-8"),
            "country": data.country,
        }
        print(user_data)
        await User_detail.insert_one(user_data)
        return {"message": "User Registered Successfully", "status": 200}
    except Exception as e:
        print("❌ Error:", e)
        return {"error": str(e)}


@router.post("/login")
async def user_login(data: LoginRequired):
    try:
        email = data.email
        existing_user = await User_detail.find_one({"email": email})
        if existing_user:
            flag = bcrypt.checkpw(
                data.password.encode(), existing_user["password"].encode()
            )
            token = create_jwt_token(existing_user["email"])
            print(token)
            print(flag)
            if flag == False:
                return {"message": "Please Enter correct Password !", "status": 404}
            else:
                return {
                    "message": "User Login Successfully",
                    "status": 200,
                    "token": token,
                }
    except Exception as e:
        print("Login Error", e)
        return {
            "message": "Server is Not Responsed , Please try again after some time",
            "status": 404,
        }


@router.get("/profile")
async def get_user_profile(request: Request):
    print("Enter in Get Profile")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):      
        return {"message":"Missing or Invalid Token","status":200}
    token = auth_header.split(" ")[1] 
    print(token)
    try:
        payload = await validate_token(token)
        print(payload)
        return {"email": payload["email"], "name": payload["name"],"status":200}
    except Exception as e:
      
       return {
           "message":"Please Login Again",
           "status":404
       }
        
    
    
    
    
    
    