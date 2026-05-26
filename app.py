import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from prompts.fitness_prompt import create_fitness_prompt
from prompts.progress_prompt import create_progress_prompt

from modules.ai_service import get_ai_response

from modules.auth import register_user, login_user

from modules.storage import (
    save_to_history,
    get_recent_history,
    clear_history,
    get_weight_progress,
    get_dashboard_summary,
    get_latest_profile
)

from modules.firebase_storage import (
    save_plan,
    save_progress,
    get_user_plans,
    get_user_progress,
    clear_user_history,
    delete_plan,
    delete_progress,
)

from modules.health_metrics import (
    calculate_bmi,
    get_bmi_category,
    calculate_calories,
    calculate_protein
)

from modules.pdf_export import create_pdf

from streamlit_cookies_manager import EncryptedCookieManager


# =========================
# SETUP
# =========================

load_dotenv()

st.set_page_config(
    page_title="FitAI Coach",
    page_icon="🏋️",
    layout="wide"
)

# =========================
# COOKIES
# =========================

cookies = EncryptedCookieManager(
    prefix="fitai_",
    password="fitai_secret_password"
)

if not cookies.ready():
    st.stop()

with open("styles/style.css", "r", encoding="utf-8") as css:
    st.markdown(
        f"<style>{css.read()}</style>",
        unsafe_allow_html=True
    )


# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "username" not in st.session_state:
    st.session_state.username = None

# =========================
# AUTO LOGIN FROM COOKIES
# =========================

if cookies.get("logged_in") == "true":

    st.session_state.logged_in = True
    st.session_state.user_id = cookies.get("user_id")
    st.session_state.user_email = cookies.get("user_email")
    st.session_state.username = cookies.get("username")


# =========================
# DATA HELPERS
# =========================

def get_current_history():
    if st.session_state.logged_in:
        plans = get_user_plans(st.session_state.user_id)
        progress = get_user_progress(st.session_state.user_id)
        return plans + progress

    return get_recent_history(limit=50)


def get_current_weight_progress():
    history = get_current_history()

    weight_data = []

    for item in history:
        if item.get("type") == "initial_plan":
            weight_data.append({
                "date": item.get("created_at", "Χωρίς ημερομηνία"),
                "weight": item.get("weight")
            })

        elif item.get("type") == "progress_update":
            weight_data.append({
                "date": item.get("created_at", "Χωρίς ημερομηνία"),
                "weight": item.get("current_weight")
            })

    return [
        item for item in weight_data
        if item["weight"] is not None
    ]


def get_current_summary():
    if st.session_state.logged_in:
        history = get_current_history()

        total_plans = len([
            item for item in history
            if item.get("type") == "initial_plan"
        ])

        total_updates = len([
            item for item in history
            if item.get("type") == "progress_update"
        ])

        weight_progress = get_current_weight_progress()

        latest_weight = (
            weight_progress[-1]["weight"]
            if len(weight_progress) > 0
            else "-"
        )

        latest_goal = "-"

        for item in reversed(history):
            if item.get("type") == "initial_plan":
                latest_goal = item.get("goal", "-")
                break

        return {
            "total_plans": total_plans,
            "total_updates": total_updates,
            "latest_weight": latest_weight,
            "latest_goal": latest_goal
        }

    return get_dashboard_summary()


def get_current_profile():
    if st.session_state.logged_in:
        history = get_current_history()

        for item in reversed(history):
            if item.get("type") == "initial_plan":
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

    return get_latest_profile()


# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## 🏋️ FitAI Coach")
st.sidebar.caption("AI Fitness & Nutrition Assistant")

if st.session_state.logged_in:

    with st.sidebar.container():

        st.markdown(
            f"""
            <div class="profile-avatar">👤</div>

            <div class="profile-name">
                {st.session_state.username}
            </div>

            <div class="profile-role">
                FitAI Premium Member
            </div>

            <div class="profile-online">
                ● Online
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.button("🚪 Logout", key="sidebar_logout")

    if st.session_state.get("sidebar_logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.username = None

        cookies["logged_in"] = ""
        cookies["user_id"] = ""
        cookies["user_email"] = ""
        cookies["username"] = ""

        cookies.save()

        st.rerun()
else:

    if st.sidebar.button("🔐 Login / Register"):

        @st.dialog("🔐 Login / Register")
        def login_dialog():

            login_tab, register_tab = st.tabs(["Σύνδεση", "Εγγραφή"])

            with login_tab:

                email = st.text_input("Email", key="login_email")
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                if st.button("Σύνδεση", key="login_submit"):

                    result = login_user(email, password)

                    if result["success"]:
                        st.session_state.logged_in = True
                        st.session_state.user_id = result["uid"]
                        st.session_state.user_email = result["email"]
                        st.session_state.username = result["username"]

                        cookies["logged_in"] = "true"
                        cookies["user_id"] = result["uid"]
                        cookies["user_email"] = result["email"]
                        cookies["username"] = result["username"]

                        cookies.save()

                        st.success("Επιτυχής σύνδεση!")
                        st.rerun()

                    else:
                        st.error("Λάθος email ή password.")

            with register_tab:

                username = st.text_input(
                    "Όνομα χρήστη",
                    key="register_username_popup"
                )

                new_email = st.text_input(
                    "Email",
                    key="register_email_popup"
                )

                new_password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password_popup"
                )

                if st.button("Εγγραφή", key="register_submit"):

                    if username.strip() == "":
                        st.error("Πρέπει να συμπληρώσεις όνομα χρήστη.")

                    elif "@" not in new_email or "." not in new_email:
                        st.error("Πρέπει να βάλεις έγκυρο email.")

                    elif len(new_password) < 6:
                        st.error("Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.")

                    else:

                        result = register_user(
                        new_email,
                        new_password,
                         username
                        )

                    if result["success"]:
                        st.success("Ο λογαριασμός δημιουργήθηκε! Τώρα κάνε σύνδεση.")
    
                    else:
                        st.error(result["error"])


        login_dialog()


page = st.sidebar.radio(
    "Πλοήγηση",
    [
        "🏠 Αρχική",
        "📋 Δημιουργία Προγράμματος",
        "📈 Προσαρμογή Προόδου",
        "📜 Ιστορικό",
        "📊 Στατιστικά",
        "ℹ️ About"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Η εφαρμογή δημιουργεί εξατομικευμένα προγράμματα "
    "γυμναστικής και διατροφής με χρήση AI."
)


# =========================
# HEADER
# =========================

st.markdown("# 🏋️ FitAI Coach")
st.markdown("### Εξατομικευμένο AI πρόγραμμα γυμναστικής και διατροφής")


# =========================
# HOME PAGE
# =========================

if page == "🏠 Αρχική":

    summary = get_current_summary()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Συνολικά Προγράμματα", summary["total_plans"])
    c2.metric("Progress Updates", summary["total_updates"])
    c3.metric("Τελευταίο Βάρος", f"{summary['latest_weight']} kg")
    c4.metric("Τελευταίος Στόχος", summary["latest_goal"])

    st.markdown("## 🏋️ AI Fitness Dashboard")

    st.write(
        "Δημιούργησε έξυπνα προγράμματα γυμναστικής και διατροφής "
        "με AI προσαρμογή προόδου."
    )

    b1, b2, b3, b4 = st.columns(4)

    b1.info("🤖 AI Plans")
    b2.info("📈 Progress Tracking")
    b3.info("🍽️ Nutrition")
    b4.info("📊 Analytics")

    st.markdown("## 🧠 AI Coach Insights")

    i1, i2 = st.columns(2)

    with i1:
        st.markdown(f"""
        <div class="custom-card">
            <h3>🎯 Τρέχων Στόχος</h3>
            <p>{summary["latest_goal"]}</p>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown(f"""
        <div class="custom-card">
            <h3>⚖️ Τελευταίο Βάρος</h3>
            <p>{summary["latest_weight"]} kg</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="custom-card">
            <h3>📋 AI Πρόγραμμα</h3>
            <p>Δημιουργία εξατομικευμένου προγράμματος γυμναστικής και διατροφής.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="custom-card">
            <h3>📈 AI Progress</h3>
            <p>Προσαρμογή προγράμματος βάσει της προόδου του χρήστη.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="custom-card">
            <h3>📊 Analytics</h3>
            <p>Παρακολούθηση βάρους, στόχων και ιστορικού.</p>
        </div>
        """, unsafe_allow_html=True)


# =========================
# CREATE PLAN PAGE
# =========================

elif page == "📋 Δημιουργία Προγράμματος":

    st.markdown("## 🧠 Δημιουργία Προγράμματος")

    profile = get_current_profile()

    if profile is None:
        profile = {
            "age": 10,
            "weight": 30.0,
            "height": 100,
            "goal": "Απώλεια λίπους",
            "experience": "Αρχάριος",
            "gender": "Άνδρας",
            "training_days": 1,
            "equipment": "Γυμναστήριο",
            "diet_type": "Χωρίς περιορισμούς"
        }

    left, right = st.columns(2, gap="large")

    with left:

        st.markdown("""
        <div class="section-title">
            <div class="section-icon">👤</div>
            <h3>Βασικά Στοιχεία</h3>
        </div>
        """, unsafe_allow_html=True)

        age = st.number_input(
            "📅 Ηλικία",
            min_value=10,
            max_value=100,
            value=int(profile["age"])
        )

        weight = st.number_input(
            "⚖️ Βάρος (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(profile["weight"])
        )

        height = st.number_input(
            "📏 Ύψος (cm)",
            min_value=100,
            max_value=250,
            value=int(profile["height"])
        )

        gender_options = ["Άνδρας", "Γυναίκα"]

        gender = st.selectbox(
            "🧍 Φύλο",
            gender_options,
            index=gender_options.index(profile["gender"])
        )

    with right:

        st.markdown("""
        <div class="section-title">
            <div class="section-icon">🎯</div>
            <h3>Στόχος & Εμπειρία</h3>
        </div>
        """, unsafe_allow_html=True)

        goal_options = [
            "Απώλεια λίπους",
            "Μυϊκή ανάπτυξη",
            "Συντήρηση"
        ]

        goal = st.selectbox(
            "🎯 Στόχος",
            goal_options,
            index=goal_options.index(profile["goal"])
        )

        experience_options = [
            "Αρχάριος",
            "Μέτριος",
            "Προχωρημένος"
        ]

        experience = st.selectbox(
            "📊 Επίπεδο εμπειρίας",
            experience_options,
            index=experience_options.index(profile["experience"])
        )

        training_days = st.slider(
            "📆 Ημέρες προπόνησης ανά εβδομάδα",
            1,
            7,
            value=int(profile["training_days"])
        )

        equipment_options = [
            "Γυμναστήριο",
            "Βάρη στο σπίτι",
            "Μόνο σωματικό βάρος"
        ]

        equipment = st.selectbox(
            "🏋️ Διαθέσιμος εξοπλισμός",
            equipment_options,
            index=equipment_options.index(profile["equipment"])
        )

    st.markdown("""
    <div class="section-title">
        <div class="section-icon">🍽️</div>
        <h3>Διατροφή & Περιορισμοί</h3>
    </div>
    """, unsafe_allow_html=True)

    diet_options = [
        "Χωρίς περιορισμούς",
        "Vegetarian",
        "Vegan",
        "Keto"
    ]

    diet_type = st.selectbox(
        "🥗 Τύπος διατροφής",
        diet_options,
        index=diet_options.index(profile["diet_type"])
    )

    injuries = st.text_area(
        "❤️ Τραυματισμοί ή προβλήματα υγείας",
        placeholder="Π.χ. πόνος στο γόνατο..."
    )

    bmi = calculate_bmi(weight, height)
    bmi_category = get_bmi_category(bmi)
    calories = calculate_calories(weight, goal)
    protein = calculate_protein(weight)

    st.markdown("""
    <div class="section-title">
        <div class="section-icon">📊</div>
        <h3>Υπολογισμοί</h3>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("BMI", bmi)
    m2.metric("Κατηγορία BMI", bmi_category)
    m3.metric("Θερμίδες", f"{calories} kcal")
    m4.metric("Πρωτεΐνη", f"{protein} g")

    if st.button("🚀 Δημιουργία Προγράμματος"):

        prompt = create_fitness_prompt(
            age,
            weight,
            height,
            goal,
            experience,
            gender,
            training_days,
            equipment,
            diet_type,
            injuries,
            bmi,
            bmi_category,
            calories,
            protein
        )

        with st.spinner("Το AI δημιουργεί το πρόγραμμά σου..."):
            response = get_ai_response(prompt)

        history_entry = {
            "type": "initial_plan",
            "created_at": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
            "age": age,
            "weight": weight,
            "height": height,
            "goal": goal,
            "experience": experience,
            "gender": gender,
            "training_days": training_days,
            "equipment": equipment,
            "diet_type": diet_type,
            "injuries": injuries,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "calories": calories,
            "protein": protein,
            "ai_response": response
        }

        if st.session_state.logged_in:
            save_plan(st.session_state.user_id, history_entry)
        else:
            save_to_history(history_entry)

        st.success("Το πρόγραμμα δημιουργήθηκε!")

        st.markdown("## 📋 Το Πρόγραμμά σου")
        st.markdown(response)


# =========================
# PROGRESS PAGE
# =========================

elif page == "📈 Προσαρμογή Προόδου":

    st.markdown("## 📈 Προσαρμογή Προγράμματος")

    history = get_current_history()

    initial_plans = [
        item for item in history
        if item.get("type") == "initial_plan"
    ]

    if len(initial_plans) == 0:

        st.warning("Δεν υπάρχει αποθηκευμένο πρόγραμμα.")

    else:

        plan_options = [
            f"{item.get('created_at', 'Χωρίς ημερομηνία')} - {item['goal']} - {item['weight']}kg"
            for item in initial_plans
        ]

        selected_index = st.selectbox(
            "📋 Επίλεξε πρόγραμμα",
            range(len(plan_options)),
            format_func=lambda i: plan_options[i]
        )

        selected_program = initial_plans[selected_index]

        selected_plan_text = selected_program["ai_response"]

        with st.expander("📄 Προβολή επιλεγμένου προγράμματος"):
            st.markdown(selected_plan_text)

        col1, col2 = st.columns(2)

        with col1:
            current_weight = st.number_input(
                "⚖️ Τρέχον βάρος",
                min_value=30.0,
                max_value=300.0
            )

        with col2:
            fatigue_level = st.selectbox(
                "😴 Επίπεδο κόπωσης",
                ["Χαμηλό", "Μέτριο", "Υψηλό"]
            )

        progress_feedback = st.text_area(
            "📝 Feedback προόδου",
            placeholder="Π.χ. Έχασα 2 κιλά..."
        )

        if st.button("🔄 Προσαρμογή Προγράμματος"):

            progress_prompt = create_progress_prompt(
                selected_plan_text,
                current_weight,
                selected_program["goal"],
                fatigue_level,
                progress_feedback
            )

            with st.spinner("Το AI προσαρμόζει το πρόγραμμα..."):
                adapted_response = get_ai_response(progress_prompt)

            progress_entry = {
                "type": "progress_update",
                "created_at": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "based_on_created_at": selected_program.get(
                    "created_at",
                    "Χωρίς ημερομηνία"
                ),
                "based_on_goal": selected_program["goal"],
                "current_weight": current_weight,
                "fatigue_level": fatigue_level,
                "progress_feedback": progress_feedback,
                "ai_response": adapted_response
            }

            if st.session_state.logged_in:
                save_progress(st.session_state.user_id, progress_entry)
            else:
                save_to_history(progress_entry)

            st.success("Το πρόγραμμα προσαρμόστηκε!")

            st.markdown("## 📈 Προσαρμοσμένο Πρόγραμμα")
            st.markdown(adapted_response)


# =========================
# HISTORY PAGE
# =========================

elif page == "📜 Ιστορικό":

    st.markdown("## 📜 Ιστορικό")

    if st.button("🗑️ Clear History"):

        if st.session_state.logged_in:

            clear_user_history(st.session_state.user_id)

            st.success("Το ιστορικό του λογαριασμού διαγράφηκε!")

            st.rerun()

        else:

            clear_history()

            st.success("Το τοπικό ιστορικό διαγράφηκε!")

            st.rerun()

    history = get_current_history()

    if len(history) == 0:

        st.info("Δεν υπάρχει ιστορικό.")

    else:

        for item in reversed(history):

            if item.get("type") == "initial_plan":

                with st.expander(
                    f"📋 Αρχικό Πρόγραμμα - {item.get('created_at', 'Χωρίς ημερομηνία')}"
                ):

                    st.write(f"🎯 Στόχος: {item['goal']}")
                    st.write(f"⚖️ Βάρος: {item['weight']} kg")
                    st.write(f"📏 Ύψος: {item['height']} cm")
                    st.write(f"📊 Εμπειρία: {item['experience']}")

                    st.markdown("### AI Πρόγραμμα")
                    st.markdown(item["ai_response"])

                    pdf_file = create_pdf(
                        "FitAI Coach - Πρόγραμμα Γυμναστικής & Διατροφής",
                        item["ai_response"]
                    )

                    st.download_button(
                        label="📄 Κατέβασμα PDF",
                        data=pdf_file,
                        file_name="fitai_program.pdf",
                        mime="application/pdf",
                        key=f"pdf_initial_{item.get('created_at', item.get('id', ''))}"
                    )

                if st.session_state.logged_in:

                    if st.button(
                        "🗑️ Διαγραφή αυτού του προγράμματος",
                        key=f"delete_plan_{item.get('id')}"
                    ):

                        delete_plan(
                            st.session_state.user_id,
                            item.get("id")
                        )

                        st.success("Το πρόγραμμα διαγράφηκε.")

                        st.rerun()

            elif item.get("type") == "progress_update":

                with st.expander(
                    f"📈 Progress Update - {item.get('created_at', 'Χωρίς ημερομηνία')}"
                ):

                    st.write(
                        f"📋 Βασίστηκε σε: {item.get('based_on_created_at', '-')}"
                    )

                    st.write(
                        f"🎯 Στόχος: {item.get('based_on_goal', '-')}"
                    )

                    st.write(f"⚖️ Βάρος: {item['current_weight']} kg")

                    st.markdown("### AI Προσαρμογή")
                    st.markdown(item["ai_response"])

                    pdf_file = create_pdf(
                        "FitAI Coach - Προσαρμοσμένο Πρόγραμμα",
                        item["ai_response"]
                    )

                    st.download_button(
                        label="📄 Κατέβασμα PDF",
                        data=pdf_file,
                        file_name="fitai_adapted_program.pdf",
                        mime="application/pdf",
                        key=f"pdf_progress_{item.get('created_at', item.get('id', ''))}"
                    )

                if st.session_state.logged_in:

                    if st.button(
                        "🗑️ Διαγραφή αυτού του update",
                        key=f"delete_progress_{item.get('id')}"
                    ):

                        delete_progress(
                            st.session_state.user_id,
                            item.get("id")
                        )

                        st.success("Το update διαγράφηκε.")

                        st.rerun()


# =========================
# STATS PAGE
# =========================

elif page == "📊 Στατιστικά":

    st.markdown("## 📊 Στατιστικά Προόδου")

    weight_progress = get_current_weight_progress()

    if len(weight_progress) == 0:

        st.info("Δεν υπάρχουν ακόμα δεδομένα.")

    else:

        first_weight = weight_progress[0]["weight"]
        latest_weight = weight_progress[-1]["weight"]

        weight_difference = round(
            latest_weight - first_weight,
            2
        )

        total_entries = len(weight_progress)

        history = get_current_history()

        latest_height = None

        for item in reversed(history):

            if item.get("type") == "initial_plan":

                latest_height = item.get("height")

                break

        s1, s2, s3 = st.columns(3)

        s1.metric("Αρχικό Βάρος", f"{first_weight} kg")
        s2.metric("Τελευταίο Βάρος", f"{latest_weight} kg")
        s3.metric("Μεταβολή", f"{weight_difference} kg")

        if latest_height is not None:

            bmi = calculate_bmi(latest_weight, latest_height)
            bmi_category = get_bmi_category(bmi)

            s4, s5 = st.columns(2)

            s4.metric("BMI", bmi)
            s5.metric("Κατηγορία BMI", bmi_category)

        st.markdown("### 📈 Εξέλιξη Βάρους")

        df = pd.DataFrame(weight_progress)

        df = df.rename(columns={
            "date": "Ημερομηνία",
            "weight": "Βάρος"
        })

        st.line_chart(
            data=df,
            x="Ημερομηνία",
            y="Βάρος"
        )

        st.markdown("### 🧠 AI Progress Insights")

        if weight_difference < 0:

            st.success(
                f"🔥 Έχεις μειώσει το βάρος σου κατά "
                f"{abs(weight_difference)} kg."
            )

        elif weight_difference > 0:

            st.warning(
                f"📈 Το βάρος σου αυξήθηκε κατά "
                f"{weight_difference} kg."
            )

        else:

            st.info("⚖️ Το βάρος σου παραμένει σταθερό.")

        if latest_height is not None:

            if bmi < 18.5:

                st.warning(
                    "⚠️ Το BMI δείχνει ότι βρίσκεσαι κάτω "
                    "από το φυσιολογικό βάρος."
                )

            elif bmi < 25:

                st.success(
                    "💪 Το BMI σου βρίσκεται σε φυσιολογικά επίπεδα."
                )

            elif bmi < 30:

                st.warning("📉 Το BMI δείχνει αυξημένο βάρος.")

            else:

                st.error("🚨 Το BMI βρίσκεται σε υψηλά επίπεδα.")

        if total_entries >= 5:

            st.success(
                "📊 Υπάρχει αρκετό ιστορικό για πιο αξιόπιστα analytics."
            )

        else:

            st.info(
                "📝 Συνέχισε να χρησιμοποιείς την εφαρμογή "
                "για καλύτερα AI insights."
            )

# =========================
# ABOUT PAGE
# =========================

elif page == "ℹ️ About":

    st.markdown("# ℹ️ About FitAI Coach")

    st.markdown("""
    ## 🏋️ Τι είναι το FitAI Coach;

    Το FitAI Coach είναι μία AI-powered εφαρμογή
    εξατομικευμένης γυμναστικής και διατροφής.

    Ο χρήστης μπορεί να:
    - δημιουργήσει AI fitness πρόγραμμα
    - παρακολουθήσει την πρόοδό του
    - προσαρμόσει το πρόγραμμα με AI
    - αποθηκεύσει ιστορικό στο cloud
    - εξάγει προγράμματα σε PDF
    """)

    st.markdown("---")

    st.markdown("""
    ## 🤖 AI Features

    - Δημιουργία fitness plans
    - AI progress adaptation
    - Personalized nutrition guidance
    - Smart analytics
    """)

    st.markdown("---")

    st.markdown("""
    ## ☁️ Technologies

    - Streamlit
    - Firebase Authentication
    - Firestore Database
    - OpenAI API
    - Python
    """)

    st.markdown("---")

    st.markdown("""
    ## 📊 Features

    ✅ Multi-user accounts  
    ✅ Persistent login  
    ✅ Progress tracking  
    ✅ PDF export  
    ✅ Cloud storage  
    ✅ AI insights  
    """)

    st.markdown("---")

    st.warning(
        "⚠️ Το FitAI Coach δεν αντικαθιστά "
        "επαγγελματική ιατρική ή διατροφική συμβουλή."
    )
    