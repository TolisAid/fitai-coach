import hashlib

from firebase_admin import auth
from modules.firebase_config import db


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(email, password, username):

    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )

        db.collection("users").document(user.uid).set({
            "email": email,
            "username": username,
            "password_hash": hash_password(password)
        })

        return {
            "success": True,
            "uid": user.uid,
            "email": email,
            "username": username
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def login_user(email, password):

    try:
        user = auth.get_user_by_email(email)

        user_doc = db.collection("users").document(user.uid).get()

        if not user_doc.exists:
            return {
                "success": False,
                "error": "Δεν βρέθηκαν στοιχεία χρήστη."
            }

        data = user_doc.to_dict()

        if data.get("password_hash") != hash_password(password):
            return {
                "success": False,
                "error": "Λάθος email ή password."
            }

        username = data.get("username") or user.display_name or user.email

        return {
            "success": True,
            "uid": user.uid,
            "email": user.email,
            "username": username
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }