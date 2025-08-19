from fastapi import APIRouter, Response
from pydantic import BaseModel, EmailStr
from services.validatetoken import validate_token
from db.mongo import User_Ride_detail
from fastapi import Request, HTTPException


router=APIRouter();



@router.get('/my-rides')
async def my_previus_rides(request: Request):
    print("enter in function")
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):      
        return {"message":"Missing or Invalid Token","status":200}
    token = auth_header.split(" ")[1] 
    try:
        
        payload = await validate_token(token)
        print(payload)
        my_riders_details=await User_Ride_detail.find_one({"email":payload["email"]})
        print(my_riders_details["ride_details"])
        return {
                "status": 200,
                "message": "User Ride find Sucessfully",
                "my_rides_details": my_riders_details["ride_details"]
            }
       
    except Exception as e:
        return {"message":"No Rides Present, Please Try after Some Time","status":404}
    