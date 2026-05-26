# =========================
# ΥΠΟΛΟΓΙΣΜΟΣ BMI
# =========================

def calculate_bmi(weight, height):

    # Μετατρέπουμε το ύψος από cm σε μέτρα
    height_in_meters = height / 100

    # Υπολογισμός BMI
    bmi = weight / (height_in_meters ** 2)

    # Επιστρέφουμε BMI με 2 δεκαδικά
    return round(bmi, 2)


# =========================
# ΚΑΤΗΓΟΡΙΑ BMI
# =========================

def get_bmi_category(bmi):

    if bmi < 18.5:
        return "Λιποβαρής"

    elif bmi < 25:
        return "Φυσιολογικό βάρος"

    elif bmi < 30:
        return "Υπέρβαρος"

    else:
        return "Παχύσαρκος"


# =========================
# ΥΠΟΛΟΓΙΣΜΟΣ ΘΕΡΜΙΔΩΝ
# =========================

def calculate_calories(weight, goal):

    # Βασικός υπολογισμός θερμίδων
    base_calories = weight * 30

    # Αν ο στόχος είναι απώλεια λίπους
    if goal == "Απώλεια λίπους":

        # Μικρό θερμιδικό έλλειμμα
        return int(base_calories - 300)

    # Αν ο στόχος είναι μυϊκή ανάπτυξη
    elif goal == "Μυϊκή ανάπτυξη":

        # Μικρό θερμιδικό πλεόνασμα
        return int(base_calories + 300)

    # Συντήρηση
    else:
        return int(base_calories)


# =========================
# ΥΠΟΛΟΓΙΣΜΟΣ ΠΡΩΤΕΪΝΗΣ
# =========================

def calculate_protein(weight):

    # 1.8g πρωτεΐνης ανά κιλό
    protein = weight * 1.8

    return int(protein)