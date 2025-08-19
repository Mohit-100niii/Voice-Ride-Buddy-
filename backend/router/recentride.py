
from fastapi import APIRouter
from pydantic import BaseModel
from db.mongo import User_last_Ride
router=APIRouter()


    
@router.get("/")
async def recent_ride(email: str):
    try:
        user = await User_last_Ride.find_one({"email":email})

        if user and "last_ride" in user:
            return {
                "status": 200,
                "message": "Last ride found successfully",
                "last_ride": user["last_ride"]
            }
        else:
            return {
                "status": 404,
                "message": "No ride found for this user"
            }

    except Exception as e:
        print(e)
        return {        
             "message": "Server error",
            "status_code":500
        }