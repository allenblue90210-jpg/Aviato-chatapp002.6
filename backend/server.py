
import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Body, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
from pathlib import Path

# --- Configuration & Setup ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Database
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# --- Models ---

class Availability(BaseModel):
    openDate: Optional[str] = None
    laterMinutes: int = 0
    laterStartTime: Optional[int] = None # Timestamp
    maxContact: int = 0
    currentContacts: int = 0
    timedHour: Optional[int] = None
    timedMinute: Optional[int] = None
    timezoneOffset: Optional[int] = None # Minutes difference from UTC
    modeStartedAt: Optional[float] = None # Timestamp for Orange Mode session reset

class Review(BaseModel):
    raterId: str
    raterName: str
    raterProfilePic: Optional[str] = None
    rating: float
    timestamp: float

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    password: Optional[str] = None # Not returned in API
    location: str = "Unknown"
    vibe: str = ""
    profilePic: Optional[str] = None # Default is None (No Profile)
    selections: List[str] = []
    approvalRating: int = 0
    reviewRating: float = 0.0
    reviewCount: int = 0
    availabilityMode: Optional[str] = None # 'green', 'blue', etc.
    availability: Availability = Field(default_factory=Availability)
    reviews: List[Review] = []

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    senderId: str
    text: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp() * 1000)
    read: bool = False
    seen: bool = False

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str # The ID of the OTHER user in the chat (from perspective of current user)
    # Note: In a real relational model, we'd have a 'participants' list. 
    # But to match frontend MVP structure where 'conversations' are stored per user:
    # We will store "Chat Objects" that belong to a specific user.
    # OR better: We store one Conversation document with participants=[A, B] and transform it for the frontend.
    # For simplicity and speed to match the current frontend 'conversations' state which is an array of objects
    # attached to the current user, we will emulate that structure or adapt.
    
    # Let's go with a cleaner backend approach:
    # A Conversation document has 'participants': [id1, id2] and 'messages': [].
    # But the frontend expects a list of objects where each object has "userId" (the OTHER person).
    
    participants: List[str]
    messages: List[Message] = []
    timerStarted: Optional[float] = None
    timerExpired: bool = False
    rated: bool = False
    ratingType: Optional[str] = None
    ratingReason: Optional[str] = None
    
    # Computed fields for frontend (not stored but generated)
    # lastMessage, etc.

class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    profilePic: Optional[str] = None
    selections: Optional[List[str]] = None
    availabilityMode: Optional[str] = None
    availability: Optional[Availability] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# --- Helpers ---

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    # Map _id to id
    user['id'] = str(user['_id'])
    del user['_id']
    if 'password' in user: del user['password']
    return user

# --- Seed Data ---
async def seed_data():
    if await db.users.count_documents({}) > 0:
        return # Already seeded

    logger.info("Seeding database...")
    
    # 1. Create Demo User
    demo_user = {
        "_id": "current-user",
        "id": "current-user",
        "email": "demo@aviato.com",
        "password": get_password_hash("password"),
        "name": "Demo User",
        "location": "San Francisco",
        "vibe": "Chill",
        "profilePic": "https://i.pravatar.cc/150?u=current-user",
        "selections": ["Coding", "Coffee"],
        "availabilityMode": "green",
        "availability": Availability().model_dump(),
        "approvalRating": 100,
        "reviewRating": 5.0,
        "reviewCount": 1
    }
    await db.users.insert_one(demo_user)
    
    # 2. Create Mock Users from mockData.js
    mock_users = [
      {
        "_id": "1", "id": "1", "name": "Asuab", "location": "Los Angeles", "vibe": "Vibe coder",
        "profilePic": "https://i.pravatar.cc/150?u=1",
        "selections": ["Metal Gear 1", "Metal Gear 2", "Zelda", "Mario", "Pokemon"],
        "approvalRating": 54, "reviewRating": 4.5, "reviewCount": 12, "availabilityMode": "green",
        "availability": {"maxContact": 10, "currentContacts": 2}, "email": "asuab@test.com"
      },
      {
        "_id": "2", "id": "2", "name": "Sussie", "location": "Miami", "vibe": "Vibe coder",
        "profilePic": "https://i.pravatar.cc/150?u=2",
        "selections": ["Metal Gear 1", "Metal Gear 2", "Metal Gear 3", "Final Fantasy", "Sonic"],
        "approvalRating": 89, "reviewRating": 4.8, "reviewCount": 25, "availabilityMode": "yellow",
        "availability": {"laterMinutes": 120, "maxContact": 10, "currentContacts": 5}, "email": "sussie@test.com"
      },
      # Add a few more...
      {
        "_id": "6", "id": "6", "name": "John", "location": "New York", "vibe": "Photographer",
        "profilePic": "https://i.pravatar.cc/150?u=6",
        "selections": ["Photography", "Art", "Travel"],
        "approvalRating": 120, "reviewRating": 4.9, "reviewCount": 67, "availabilityMode": "green",
        "availability": {"maxContact": 15, "currentContacts": 8}, "email": "john@test.com"
      }
    ]
    
    for u in mock_users:
        u['password'] = get_password_hash("password") # Default password
        # Ensure availability defaults
        if 'availability' not in u: u['availability'] = {}
        # Merge with default availability
        def_avail = Availability().model_dump()
        def_avail.update(u['availability'])
        u['availability'] = def_avail
        await db.users.insert_one(u)

    logger.info("Seeding complete.")

# --- Routes ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_data()
    yield

app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")

# Auth Routes
@api.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    
    user['id'] = str(user['_id'])
    del user['_id']
    del user['password']
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@api.post("/auth/signup", response_model=Token)
async def signup(req: SignupRequest):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=req.email,
        name=req.name,
        password=get_password_hash(req.password),
        availabilityMode="green"
    ).model_dump()
    new_user['_id'] = new_user['id']
    
    await db.users.insert_one(new_user)
    
    access_token = create_access_token(data={"sub": req.email})
    
    del new_user['_id']
    del new_user['password']
    
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

@api.get("/auth/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# User Routes
@api.get("/users")
async def get_users():
    users = await db.users.find({}, {"password": 0}).to_list(1000)
    for u in users:
        u['id'] = str(u['_id'])
        del u['_id']
        
        # --- ORANGE MODE DYNAMIC COUNT (Active Conversations) ---
        if u.get('availabilityMode') == 'orange':
            # Count conversations that:
            # 1. Involve this user
            # 2. Have at least one message (messages array is not empty)
            # This ensures simply "viewing" (empty chat) doesn't burn a slot.
            active_count = await db.conversations.count_documents({
                "participants": u['id'],
                "messages": {"$not": {"$size": 0}}
            })
            if 'availability' not in u: u['availability'] = {}
            u['availability']['currentContacts'] = active_count
        # ---------------------------------
        
    return users

@api.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"_id": user_id}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user['id'] = str(user['_id'])
    del user['_id']
    
    # --- ORANGE MODE DYNAMIC COUNT (Active Session) ---
    if user.get('availabilityMode') == 'orange':
        # Count conversations that became active (message sent) AFTER the mode started/reset
        mode_start = user.get('availability', {}).get('modeStartedAt', 0)
        
        active_count = await db.conversations.count_documents({
            "participants": user['id'],
            "messages": {"$not": {"$size": 0}},
            "timerStarted": {"$gt": mode_start}
        })
        if 'availability' not in user: user['availability'] = {}
        user['availability']['currentContacts'] = active_count
    # ---------------------------------
    
    return user

@api.put("/users/{user_id}")
async def update_user(user_id: str, updates: UserUpdate, current_user: dict = Depends(get_current_user)):
    if current_user['id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        return current_user
        
    # If switching to Orange Mode OR updating Orange Mode settings, reset the session timer
    # We reset if 'availabilityMode' is explicitly set to 'orange', 
    # OR if 'availability' dict is provided (meaning settings update).
    should_reset = False
    
    if update_data.get('availabilityMode') == 'orange':
        should_reset = True
    elif current_user.get('availabilityMode') == 'orange' and 'availability' in update_data:
        should_reset = True
        
    if should_reset:
        # Set modeStartedAt to NOW
        if 'availability' not in update_data: update_data['availability'] = {}
        # Preserve existing availability data if doing a partial update? 
        # Pydantic dump includes everything set in model. If frontend sends full object, we are good.
        update_data['availability']['modeStartedAt'] = datetime.now().timestamp() * 1000
        
    # --- BLUE MODE VALIDATION ---
    if update_data.get('availabilityMode') == 'blue':
        # Check if 'availability' is present, or merge with existing?
        # Assuming frontend sends full availability object for updates.
        avail = update_data.get('availability') or current_user.get('availability', {})
        open_date_str = avail.get('openDate')
        
        if open_date_str:
            try:
                open_date = datetime.strptime(open_date_str, "%Y-%m-%d").date()
                today = datetime.now().date()
                if open_date <= today:
                    raise HTTPException(
                        status_code=400,
                        detail="Open Date must be tomorrow or later"
                    )
            except ValueError:
                # Invalid date format is handled by logic/frontend usually, but safe to ignore here
                pass
    # ----------------------------

    await db.users.update_one({"_id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"_id": user_id}, {"password": 0})
    updated_user['id'] = str(updated_user['_id'])
    del updated_user['_id']
    
    # --- ORANGE MODE DYNAMIC COUNT (Active Session) ---
    if updated_user.get('availabilityMode') == 'orange':
        mode_start = updated_user.get('availability', {}).get('modeStartedAt', 0)
        
        active_count = await db.conversations.count_documents({
            "participants": updated_user['id'],
            "messages": {"$not": {"$size": 0}},
            "timerStarted": {"$gt": mode_start}
        })
        if 'availability' not in updated_user: updated_user['availability'] = {}
        updated_user['availability']['currentContacts'] = active_count
    # ---------------------------------
    
    return updated_user

@api.post("/users/{user_id}/reviews")
async def add_review(user_id: str, review: Review, current_user: dict = Depends(get_current_user)):
    # Add review to user
    await db.users.update_one(
        {"_id": user_id},
        {"$push": {"reviews": review.model_dump()}}
    )
    
    # Recalculate ratings
    user = await db.users.find_one({"_id": user_id})
    if user and "reviews" in user:
        reviews = user["reviews"]
        if reviews:
            total_rating = sum(r["rating"] for r in reviews)
            avg_rating = total_rating / len(reviews)
            review_count = len(reviews)
            
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"reviewRating": round(avg_rating, 1), "reviewCount": review_count}}
            )
    
    return {"status": "success"}

# Conversation Routes
@api.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    # Find conversations where current user is a participant
    cursor = db.conversations.find({"participants": current_user['id']})
    conversations = await cursor.to_list(1000)
    
    result = []
    for conv in conversations:
        # Transform for frontend
        other_user_id = next((pid for pid in conv['participants'] if pid != current_user['id']), None)
        if not other_user_id: continue # Should not happen
        
        # Calculate frontend fields
        messages = conv.get('messages', [])
        last_message = messages[-1] if messages else None
        
        conv_obj = {
            "id": str(conv['_id']),
            "userId": other_user_id,
            "messages": messages,
            "timerStarted": conv.get('timerStarted'),
            "timerExpired": conv.get('timerExpired', False),
            "rated": conv.get('rated', False),
            "lastMessage": last_message['text'] if last_message else "",
            "lastMessageTime": last_message['timestamp'] if last_message else conv.get('timestamp', 0),
            "lastMessageSenderId": last_message['senderId'] if last_message else None,
            # Simple logic for now
            "waitingForResponse": last_message['senderId'] == current_user['id'] if last_message else False,
            "theyRespondedLast": last_message['senderId'] != current_user['id'] if last_message else False,
        }
        result.append(conv_obj)
        
    # Sort by lastMessageTime descending (newest first)
    result.sort(key=lambda x: x['lastMessageTime'], reverse=True)
    
    return result

@api.post("/conversations/start")
async def start_chat(request: Request, payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    target_user_id = payload.get("userId")
    if not target_user_id:
        raise HTTPException(status_code=400, detail="userId required")

    # Debug Logging
    logger.info(f"Start Chat Request. User: {current_user['email']}, Target: {target_user_id}")
    if target_user_id:
        tgt = await db.users.find_one({"_id": target_user_id})
        if tgt:
            logger.info(f"Target Mode: {tgt.get('availabilityMode')}, Avail: {tgt.get('availability')}")
            # Log Timezone Info
            offset_h = request.headers.get('x-timezone-offset')
            logger.info(f"Header Offset: {offset_h}")
        
    # Check if exists
    existing = await db.conversations.find_one({
        "participants": {"$all": [current_user['id'], target_user_id]}
    })
    
    if existing:
        return {"id": str(existing['_id']), "status": "exists"}
    
    # --- BLUE MODE LOGIC CHECK ---
    # Check if target user is in blue mode
    target_user = await db.users.find_one({"_id": target_user_id})
    if target_user and target_user.get('availabilityMode') == 'blue':
        open_date_str = target_user.get('availability', {}).get('openDate')
        if open_date_str:
            try:
                open_date = datetime.strptime(open_date_str, "%Y-%m-%d").date()
                today = datetime.now().date()
                
                if open_date > today:
                    # Date is in the future. BLOCK EVERYONE (even existing chats? Yes, universally blocked).
                    # User requirement: "block all access to his messaging box for all users universally"
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User is unavailable until {open_date_str} (Blue Mode)"
                    )
            except ValueError:
                pass # Invalid date format, ignore
    
    # --- YELLOW MODE LOGIC CHECK ---
    if target_user and target_user.get('availabilityMode') == 'yellow':
        avail = target_user.get('availability', {})
        start_time = avail.get('laterStartTime')
        minutes = avail.get('laterMinutes')
        
        if start_time and minutes:
            # Check if expired
            now_ms = datetime.now().timestamp() * 1000
            end_time = start_time + (minutes * 60 * 1000)
            
            if now_ms > end_time:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User's availability duration has expired (Yellow Mode)"
                )
    # -----------------------------

    # --- BROWN MODE LOGIC CHECK ---
    # Feature Removed: We skip the blocking logic for Brown Mode.
    if target_user and target_user.get('availabilityMode') == 'brown':
        pass
    # -----------------------------

    # --- ORANGE MODE LOGIC CHECK ---
    # Allow starting chat for "View" mode even when limit is reached
    # The actual blocking happens in send_message endpoint
    # This allows users to see the chat interface and understand the limit
    # -------------------------------
    
    new_conv = {
        "_id": str(uuid.uuid4()),
        "participants": [current_user['id'], target_user_id],
        "messages": [],
        "created_at": datetime.now()
    }
    await db.conversations.insert_one(new_conv)
    return {"id": new_conv['_id'], "status": "created"}

@api.post("/conversations/{user_id}/messages")
async def send_message(request: Request, user_id: str, payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    # user_id here is the TARGET user id
    
    # Get target user first
    target_user = await db.users.find_one({"_id": user_id})
    
    # --- BLUE MODE CHECK (Before Sending) ---
    if target_user and target_user.get('availabilityMode') == 'blue':
        open_date_str = target_user.get('availability', {}).get('openDate')
        if open_date_str:
            try:
                open_date = datetime.strptime(open_date_str, "%Y-%m-%d").date()
                today = datetime.now().date()
                if open_date > today:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User is unavailable until {open_date_str} (Blue Mode)"
                    )
            except ValueError:
                pass
    
    # --- YELLOW MODE CHECK (Before Sending) ---
    if target_user and target_user.get('availabilityMode') == 'yellow':
        avail = target_user.get('availability', {})
        start_time = avail.get('laterStartTime')
        minutes = avail.get('laterMinutes')
        
        if start_time and minutes:
            now_ms = datetime.now().timestamp() * 1000
            end_time = start_time + (minutes * 60 * 1000)
            
            if now_ms > end_time:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User's availability duration has expired (Yellow Mode)"
                )
    # ----------------------------------------

    # --- ORANGE MODE CHECK (Before Sending) ---
    if target_user and target_user.get('availabilityMode') == 'orange':
        # Check counts again (Active Session)
        mode_start = target_user.get('availability', {}).get('modeStartedAt', 0)
        
        current = await db.conversations.count_documents({
            "participants": user_id,
            "messages": {"$not": {"$size": 0}},
            "timerStarted": {"$gt": mode_start}
        })
        max_c = target_user.get('availability', {}).get('maxContact', 0)
        
        # Check if *this* conversation already has messages
        my_conv = await db.conversations.find_one({
            "participants": {"$all": [current_user['id'], user_id]}
        })
        
        # Determine if this message counts as a "New Contact" for this session
        # It is new if:
        # 1. No previous messages exist (New Conversation)
        # 2. Previous messages exist, BUT they are from BEFORE the mode started (Re-activating old chat)
        
        is_new_contact = False
        if not my_conv or not my_conv.get('messages') or len(my_conv['messages']) == 0:
            is_new_contact = True
        else:
            # Check timestamp of last activity vs mode_start
            last_timer = my_conv.get('timerStarted', 0)
            if last_timer <= mode_start:
                is_new_contact = True
            
        if is_new_contact and current >= max_c:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has reached maximum contacts (Orange Mode)"
             )
    # ------------------------------------------

    # --- BROWN MODE CHECK (Before Sending) ---
    # Feature Removed: We skip the blocking logic for Brown Mode.
    if target_user and target_user.get('availabilityMode') == 'brown':
        pass
    # ------------------------------------------

    conv = await db.conversations.find_one({
        "participants": {"$all": [current_user['id'], user_id]}
    })
    
    if not conv:
        # Auto-create?
        conv_id = str(uuid.uuid4())
        await db.conversations.insert_one({
            "_id": conv_id,
            "participants": [current_user['id'], user_id],
            "messages": []
        })
        conv = {"_id": conv_id}

    text = payload.get("text")
    msg = Message(senderId=current_user['id'], text=text)
    msg_dump = msg.model_dump()
    
    # Update conversation
    updates = {
        "$push": {"messages": msg_dump},
    }
    
    # Start timer if not started OR if we need to "renew" the session for Orange Mode counting
    # (i.e. if the timerStarted is OLDER than the modeStartedAt, we update it to NOW so it counts as 1 slot)
    should_update_timer = False
    
    if not conv.get('timerStarted') or conv.get('rated') or conv.get('timerExpired'):
        should_update_timer = True
    elif target_user and target_user.get('availabilityMode') == 'orange':
        mode_start = target_user.get('availability', {}).get('modeStartedAt', 0)
        last_timer = conv.get('timerStarted', 0)
        if last_timer <= mode_start:
            should_update_timer = True
            
    if should_update_timer:
         updates["$set"] = {"timerStarted": datetime.now().timestamp() * 1000, "rated": False, "timerExpired": False}
    
    await db.conversations.update_one(
        {"_id": conv["_id"]},
        updates
    )
    
    return msg_dump

@api.post("/conversations/{user_id}/rate")
async def rate_conversation(user_id: str, payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    is_good = payload.get("isGood")
    reason = payload.get("reason")
    
    conv = await db.conversations.find_one({
        "participants": {"$all": [current_user['id'], user_id]}
    })
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await db.conversations.update_one(
        {"_id": conv["_id"]},
        {
            "$set": {
                "rated": True,
                "timerExpired": True,
                "ratingType": "good" if is_good else "bad",
                "ratingReason": reason
            }
        }
    )
    
    # Update user approval rating
    target_user = await db.users.find_one({"_id": user_id})
    if target_user:
        if is_good:
            change = 10
        else:
            penalties = {
                'No response / Ghosted': -15,
                'Rude or disrespectful': -20,
                'Spam messages': -25,
                'Inappropriate content': -30,
                'One-word answers': -10
            }
            change = penalties.get(reason, -10)

        # Update rating
        await db.users.update_one(
            {"_id": user_id},
            {"$inc": {"approvalRating": change}}
        )
        
        # Note: Do NOT decrement currentContacts.
        # This ensures the slot remains "used" even after rating, 
        # fulfilling the "Session Limit" requirement.

    return {"status": "success"}

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
