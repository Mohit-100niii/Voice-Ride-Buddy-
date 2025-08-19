import asyncio
from db.mongo import fare_rates_collection

async def get_fare(parsed_distance: float):
    parsed_distance=float(parsed_distance)
    try:
        async for item in fare_rates_collection.find():
           
            min_distance = float(item.get('min').strip())
            max_distance = float(item.get('max').strip())
            mileage_rate = float(item.get('mileage_rate').strip())
            
            if min_distance <= parsed_distance <= max_distance:
                total_fare = mileage_rate * parsed_distance
                print(f"✅ Fare matched: ₹{round(total_fare)} for distance {parsed_distance}km")
                return round(total_fare)

    except Exception as e:
        print("❌ Failed to fetch fare:", e)
