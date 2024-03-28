from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

app = FastAPI()

# Replace this with the correct URL where your frontend is hosted
origins = ["http://localhost:3004"]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE","OPTIONS"],
    allow_headers=["*"],
)

# Define a filename for user data storage
USER_DATA_FILE = "user_data.txt"

# Define a data model for user registration
class User(BaseModel):
    username: str
    password: str
    confirmPassword : str
    email: str
    phoneNumber: str

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/api/register")
async def register(user: User):
    if len(user.username) < 6:
        raise HTTPException(status_code=400, detail="Username must be at least 6 characters long.")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    # Additional validation logic for email and phone number can be added here

    # Data uniqueness checks
    try:
        with open(USER_DATA_FILE, "r") as file:
            existing_data = file.readlines()
            for line in existing_data:
                username, email, phoneNumber = line.strip().split(",")
                if user.username == username :
                    raise HTTPException(status_code=400, detail="Username already exists.")
                if user.email == email :
                    raise HTTPException(status_code=400, detail="Email already exists.")
                if user.phoneNumber == phoneNumber:
                    raise HTTPException(status_code=400, detail="Phone number already exists.")
                
    except FileNotFoundError:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        logging.info("User data file not found. Creating a new one.")

    # Save user data to a text file
    try:
        with open(USER_DATA_FILE, "a") as file:
            user_data_string = f"{user.username},{user.email},{user.phoneNumber}\n"
            file.write(user_data_string)
        return {"message": "User registered successfully. (Data saved to file)"}
    except Exception as e:
        logging.error(f"Error saving user data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error registering user. Please try again later.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
