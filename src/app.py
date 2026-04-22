"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Pydantic models for request/response
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    graduation_year: Optional[int] = None

class PasswordReset(BaseModel):
    new_password: str

class RoleAssignment(BaseModel):
    role: str

class BulkUserOperation(BaseModel):
    emails: List[str]
    operation: str
    role: Optional[str] = None

# In-memory user database
users = {
    "michael@mergington.edu": {
        "name": "Michael Chen",
        "email": "michael@mergington.edu",
        "password": "password123",
        "phone": "555-0101",
        "graduation_year": 2025,
        "role": "student",
        "activities": ["Chess Club", "Programming Class"],
        "created_at": "2025-01-15"
    },
    "daniel@mergington.edu": {
        "name": "Daniel Smith",
        "email": "daniel@mergington.edu",
        "password": "password123",
        "phone": "555-0102",
        "graduation_year": 2026,
        "role": "student",
        "activities": ["Chess Club"],
        "created_at": "2025-01-16"
    },
    "emma@mergington.edu": {
        "name": "Emma Johnson",
        "email": "emma@mergington.edu",
        "password": "password123",
        "phone": "555-0103",
        "graduation_year": 2025,
        "role": "student",
        "activities": ["Programming Class"],
        "created_at": "2025-01-17"
    },
    "sophia@mergington.edu": {
        "name": "Sophia Rodriguez",
        "email": "sophia@mergington.edu",
        "password": "password123",
        "phone": "555-0104",
        "graduation_year": 2026,
        "role": "student",
        "activities": ["Programming Class"],
        "created_at": "2025-01-18"
    },
    "john@mergington.edu": {
        "name": "John Williams",
        "email": "john@mergington.edu",
        "password": "password123",
        "phone": "555-0105",
        "graduation_year": 2025,
        "role": "student",
        "activities": ["Gym Class"],
        "created_at": "2025-01-19"
    },
    "olivia@mergington.edu": {
        "name": "Olivia Brown",
        "email": "olivia@mergington.edu",
        "password": "password123",
        "phone": "555-0106",
        "graduation_year": 2026,
        "role": "student",
        "activities": ["Gym Class"],
        "created_at": "2025-01-20"
    },
    "admin@mergington.edu": {
        "name": "Admin User",
        "email": "admin@mergington.edu",
        "password": "admin123",
        "phone": "555-0001",
        "graduation_year": None,
        "role": "admin",
        "activities": [],
        "created_at": "2024-01-01"
    }
}

# Activity history tracking
activity_history = {
    "michael@mergington.edu": [
        {"activity": "Chess Club", "action": "signup", "timestamp": "2025-02-01T10:30:00"},
        {"activity": "Programming Class", "action": "signup", "timestamp": "2025-02-05T14:00:00"}
    ],
    "emma@mergington.edu": [
        {"activity": "Programming Class", "action": "signup", "timestamp": "2025-02-03T09:15:00"}
    ]
}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# ============================================================================
# ADMIN ENDPOINTS FOR USER MANAGEMENT
# ============================================================================

def verify_admin(admin_password: Optional[str] = Header(None)):
    """Simple admin verification middleware"""
    if admin_password != "admin123":
        raise HTTPException(
            status_code=403,
            detail="Admin access denied. Invalid admin password."
        )


@app.get("/admin/users")
def get_all_users(admin_password: Optional[str] = Header(None)):
    """View all student and admin accounts"""
    verify_admin(admin_password)
    
    result = []
    for email, user_data in users.items():
        result.append({
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
            "phone": user_data["phone"],
            "graduation_year": user_data["graduation_year"],
            "activities_count": len(user_data["activities"]),
            "created_at": user_data["created_at"]
        })
    return result


@app.get("/admin/users/{email}")
def get_user_details(email: str, admin_password: Optional[str] = Header(None)):
    """Get detailed information for a specific user"""
    verify_admin(admin_password)
    
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[email]
    return {
        "email": user["email"],
        "name": user["name"],
        "phone": user["phone"],
        "graduation_year": user["graduation_year"],
        "role": user["role"],
        "activities": user["activities"],
        "created_at": user["created_at"]
    }


@app.put("/admin/users/{email}")
def update_user(email: str, user_update: UserUpdate, admin_password: Optional[str] = Header(None)):
    """Update user information"""
    verify_admin(admin_password)
    
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[email]
    
    if user_update.name:
        user["name"] = user_update.name
    if user_update.email and user_update.email != email:
        # Handle email change
        users[user_update.email] = user
        del users[email]
        user["email"] = user_update.email
    if user_update.phone:
        user["phone"] = user_update.phone
    if user_update.graduation_year:
        user["graduation_year"] = user_update.graduation_year
    
    return {"message": "User updated successfully", "user": user}


@app.post("/admin/users/{email}/password-reset")
def reset_password(email: str, reset_data: PasswordReset, admin_password: Optional[str] = Header(None)):
    """Reset user password"""
    verify_admin(admin_password)
    
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    users[email]["password"] = reset_data.new_password
    return {"message": f"Password reset for {email}"}


@app.get("/admin/users/{email}/history")
def get_user_activity_history(email: str, admin_password: Optional[str] = Header(None)):
    """View user activity history"""
    verify_admin(admin_password)
    
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = activity_history.get(email, [])
    return {
        "email": email,
        "name": users[email]["name"],
        "activity_history": history,
        "total_activities": len(users[email]["activities"])
    }


@app.put("/admin/users/{email}/role")
def assign_user_role(email: str, role_data: RoleAssignment, admin_password: Optional[str] = Header(None)):
    """Assign or update user role"""
    verify_admin(admin_password)
    
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    valid_roles = ["student", "admin", "teacher"]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Valid roles: {valid_roles}"
        )
    
    users[email]["role"] = role_data.role
    return {"message": f"Role updated to {role_data.role}", "email": email}


@app.post("/admin/users/bulk-update")
def bulk_user_operations(bulk_op: BulkUserOperation, admin_password: Optional[str] = Header(None)):
    """Perform bulk operations on multiple users"""
    verify_admin(admin_password)
    
    results = []
    
    for email in bulk_op.emails:
        if email not in users:
            results.append({"email": email, "status": "failed", "reason": "User not found"})
            continue
        
        try:
            if bulk_op.operation == "assign_role" and bulk_op.role:
                users[email]["role"] = bulk_op.role
                results.append({"email": email, "status": "success", "operation": bulk_op.operation})
            elif bulk_op.operation == "activate":
                # Could be used to mark user as active
                results.append({"email": email, "status": "success", "operation": bulk_op.operation})
            elif bulk_op.operation == "deactivate":
                # Could be used to mark user as inactive
                results.append({"email": email, "status": "success", "operation": bulk_op.operation})
            else:
                results.append({"email": email, "status": "failed", "reason": "Invalid operation"})
        except Exception as e:
            results.append({"email": email, "status": "failed", "reason": str(e)})
    
    return {
        "operation": bulk_op.operation,
        "total_users": len(bulk_op.emails),
        "results": results
    }


@app.get("/admin/statistics")
def get_user_statistics(admin_password: Optional[str] = Header(None)):
    """Get user and system statistics"""
    verify_admin(admin_password)
    
    total_users = len(users)
    total_students = len([u for u in users.values() if u["role"] == "student"])
    total_admins = len([u for u in users.values() if u["role"] == "admin"])
    
    total_registrations = sum(len(activity["participants"]) for activity in activities.values())
    avg_registrations_per_user = total_registrations / total_students if total_students > 0 else 0
    
    activity_stats = []
    for activity_name, activity_data in activities.items():
        activity_stats.append({
            "name": activity_name,
            "participants": len(activity_data["participants"]),
            "capacity": activity_data["max_participants"],
            "fill_rate": round((len(activity_data["participants"]) / activity_data["max_participants"]) * 100, 2)
        })
    
    return {
        "user_statistics": {
            "total_users": total_users,
            "total_students": total_students,
            "total_admins": total_admins
        },
        "registration_statistics": {
            "total_registrations": total_registrations,
            "average_for_user": round(avg_registrations_per_user, 2),
            "total_activities": len(activities)
        },
        "activity_statistics": activity_stats,
        "top_activities": sorted(activity_stats, key=lambda x: x["participants"], reverse=True)[:3]
    }
