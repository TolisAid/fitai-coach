from modules.firebase_config import db


# Αποθήκευση αρχικού προγράμματος στο Firebase
def save_plan(user_id, plan_data):

    db.collection("users").document(user_id).collection("plans").add(plan_data)


# Αποθήκευση progress update στο Firebase
def save_progress(user_id, progress_data):

    db.collection("users").document(user_id).collection("progress_updates").add(progress_data)


# Φόρτωση προγραμμάτων χρήστη
def get_user_plans(user_id):

    docs = (
        db.collection("users")
        .document(user_id)
        .collection("plans")
        .stream()
    )

    plans = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        plans.append(item)

    return plans


# Φόρτωση progress updates χρήστη
def get_user_progress(user_id):

    docs = (
        db.collection("users")
        .document(user_id)
        .collection("progress_updates")
        .stream()
    )

    progress = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        progress.append(item)

    return progress

def clear_user_history(user_id):

    plans = (
        db.collection("users")
        .document(user_id)
        .collection("plans")
        .stream()
    )

    for doc in plans:
        doc.reference.delete()

    progress = (
        db.collection("users")
        .document(user_id)
        .collection("progress_updates")
        .stream()
    )

    for doc in progress:
        doc.reference.delete()