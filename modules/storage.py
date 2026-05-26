# Εισάγουμε το json για να διαβάζουμε και να γράφουμε JSON αρχεία
import json

# Εισάγουμε datetime για ημερομηνία και ώρα
from datetime import datetime


# Path αρχείου ιστορικού
HISTORY_FILE = "data/user_history.json"


# =========================
# ΦΟΡΤΩΣΗ ΙΣΤΟΡΙΚΟΥ
# =========================

def load_history():

    # Ανοίγουμε το JSON αρχείο
    with open(HISTORY_FILE, "r", encoding="utf-8") as file:

        # Επιστρέφουμε τα δεδομένα
        return json.load(file)


# =========================
# ΑΠΟΘΗΚΕΥΣΗ ΙΣΤΟΡΙΚΟΥ
# =========================

def save_to_history(entry):

    # Φορτώνουμε το υπάρχον ιστορικό
    history = load_history()

    # Προσθέτουμε ημερομηνία και ώρα
    entry["created_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Προσθέτουμε τη νέα εγγραφή
    history.append(entry)

    # Αποθηκεύουμε πίσω στο JSON
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:

        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# ΤΕΛΕΥΤΑΙΟ ΙΣΤΟΡΙΚΟ
# =========================

def get_recent_history(limit=5):

    # Φορτώνουμε το ιστορικό
    history = load_history()

    # Επιστρέφουμε τις τελευταίες εγγραφές
    return history[-limit:]

    # =========================
# ΚΑΘΑΡΙΣΜΟΣ ΙΣΤΟΡΙΚΟΥ
# =========================

def clear_history():

    # Αδειάζουμε το ιστορικό
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:

        json.dump([], file)

# =========================
# ΕΞΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ΒΑΡΟΥΣ
# =========================

def get_weight_progress():

    # Φορτώνουμε όλο το ιστορικό
    history = load_history()

    # Λίστα για τα δεδομένα βάρους
    weight_data = []

    # Περνάμε κάθε εγγραφή ιστορικού
    for item in history:

        # Αν είναι αρχικό πρόγραμμα
        if item["type"] == "initial_plan":

            weight_data.append({
                "date": item.get("created_at", "Χωρίς ημερομηνία"),
                "weight": item.get("weight")
            })

        # Αν είναι progress update
        elif item["type"] == "progress_update":

            weight_data.append({
                "date": item.get("created_at", "Χωρίς ημερομηνία"),
                "weight": item.get("current_weight")
            })

    # Επιστρέφουμε μόνο όσα έχουν βάρος
    return [
        item for item in weight_data
        if item["weight"] is not None
    ]

# =========================
# DASHBOARD SUMMARY
# =========================

def get_dashboard_summary():

    # Φορτώνουμε όλο το ιστορικό
    history = load_history()

    # Μετράμε τα αρχικά προγράμματα
    total_plans = len([
        item for item in history
        if item["type"] == "initial_plan"
    ])

    # Μετράμε τα progress updates
    total_updates = len([
        item for item in history
        if item["type"] == "progress_update"
    ])

    # Παίρνουμε την εξέλιξη βάρους
    weight_progress = get_weight_progress()

    # Βρίσκουμε τελευταίο βάρος
    latest_weight = weight_progress[-1]["weight"] if len(weight_progress) > 0 else "-"

    # Βρίσκουμε τελευταίο στόχο
    latest_goal = "-"

    for item in reversed(history):
        if item["type"] == "initial_plan":
            latest_goal = item.get("goal", "-")
            break

    # Επιστρέφουμε τα δεδομένα
    return {
        "total_plans": total_plans,
        "total_updates": total_updates,
        "latest_weight": latest_weight,
        "latest_goal": latest_goal
    }

    # =========================
    # USER PROFILE
    # =========================

def get_latest_profile():

    history = get_recent_history(limit=50)

    for item in reversed(history):

        if item["type"] == "initial_plan":

            return {
                "age": item.get("age"),
                "weight": item.get("weight"),
                "height": item.get("height"),
                "goal": item.get("goal"),
                "experience": item.get("experience"),
                "gender": item.get("gender"),
                "training_days": item.get("training_days"),
                "equipment": item.get("equipment"),
                "diet_type": item.get("diet_type")
            }

    return None