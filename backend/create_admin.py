"""
One-time script to create the first admin user.

Usage (from the backend folder with venv active):
    python create_admin.py

Or to promote an existing user to admin:
    python create_admin.py --promote admin@example.com
"""
import sys
import os

# Ensure app modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.services.user_service import get_user_by_email, create_user
from datetime import datetime


def create_admin(email: str, password: str, full_name: str = "Admin") -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            # Promote existing user to admin + active
            existing.role = UserRole.ADMIN
            existing.status = UserStatus.ACTIVE
            existing.is_active = True
            existing.approved_at = datetime.utcnow()
            db.commit()
            print(f"✓ Promoted existing user '{email}' to admin.")
        else:
            user = create_user(
                db,
                email=email,
                password=password,
                full_name=full_name,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )
            # Mark as self-approved
            user.approved_at = datetime.utcnow()
            user.is_active = True
            db.commit()
            print(f"✓ Created admin user '{email}'.")
    finally:
        db.close()


if __name__ == "__main__":
    if "--promote" in sys.argv:
        idx = sys.argv.index("--promote")
        email = sys.argv[idx + 1]
        create_admin(email=email, password="")
    else:
        print("=== Create First Admin ===")
        email = input("Admin email: ").strip()
        password = input("Admin password: ").strip()
        full_name = input("Full name (optional): ").strip() or "Admin"
        create_admin(email=email, password=password, full_name=full_name)
