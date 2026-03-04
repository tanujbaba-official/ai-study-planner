import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pickle
import random
import os

st.set_page_config(page_title="AI Study Planner", page_icon="📅", layout="wide")
st.title("📅 AI Study Planner")

# ====================== LOGIN SCREEN (No Sidebar) ======================
if "mode" not in st.session_state:
    st.session_state.mode = None
    st.session_state.is_admin = False

st.subheader("👤 Welcome! Select Your Mode")

col1, col2 = st.columns(2)

with col1:
    if st.button("👨‍🎓 Student Mode", use_container_width=True, type="secondary"):
        st.session_state.mode = "student"
        st.session_state.is_admin = False
        st.rerun()

with col2:
    if st.button("🔑 Admin Mode", use_container_width=True, type="primary"):
        st.session_state.mode = "admin"

# Admin Password Check
if st.session_state.mode == "admin":
    admin_pass = st.text_input("🔒 Enter Admin Password", type="password")
    if admin_pass == "admin123":          
        st.session_state.is_admin = True
        st.success("✅ Admin Mode Activated!")
        st.rerun()
    elif admin_pass:
        st.error("❌ Wrong Password")
        st.stop()

is_admin = st.session_state.is_admin

# ====================== DATA & FOLDERS ======================
os.makedirs("uploads", exist_ok=True)
UPLOAD_FOLDER = "uploads"

DB_FILE = "study_planner.pkl"

def load_data():
    try:
        with open(DB_FILE, "rb") as f:
            data = pickle.load(f)
    except:
        data = {"subjects": []}
    
    for sub in data.get("subjects", []):
        if "exam" not in sub or not isinstance(sub.get("exam"), datetime.date):
            sub["exam"] = datetime.now().date() + timedelta(days=30)
        if "difficulty" not in sub: sub["difficulty"] = 5
        if "syllabus" not in sub: sub["syllabus"] = []
        if "progress" not in sub: sub["progress"] = {t: False for t in sub.get("syllabus", [])}
        if "syllabus_pdf" not in sub: sub["syllabus_pdf"] = None
        if "pyq_pdf" not in sub: sub["pyq_pdf"] = None
        if "book_pdf" not in sub: sub["book_pdf"] = None
    return data

def save_data(data):
    with open(DB_FILE, "wb") as f:
        pickle.dump(data, f)

data = load_data()

st.markdown("**Admin Syllabus + Exam Calendar + Smart Timetable + Pomodoro**")

# ====================== TABS (Student & Admin both) ======================
is_admin = st.session_state.is_admin
# ====================== PLANNER ONLY AFTER LOGIN ======================
if st.session_state.mode is None:
    st.info("Select Student or Admin Mode from above 👆")
    st.stop() 


st.markdown("**Admin Syllabus + Exam Calendar + Smart Timetable + Pomodoro**")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Exam Calendar", 
    "📚 AI Timetable", 
    "✅ Progress Tracker", 
    "⏰ Pomodoro Timer", 
    "💡 AI Tips"
])
# Admin features
if st.session_state.is_admin:
    st.divider()
    st.subheader("🔧 Admin Panel - Add / Edit / Delete Subjects")
    
# Tab 1: Calendar
with tab1:
    st.subheader("📅 Upcoming Exams Calendar")
    if not data["subjects"]:
        st.info("Admin Login for Professors")
    else:
        df = pd.DataFrame([{
            "Subject": s["name"],
            "Exam Date": s["exam"],
            "Days Left": (s["exam"] - datetime.now().date()).days,
            "Difficulty": "🔴" * s["difficulty"]
        } for s in data["subjects"]])
        df = df.sort_values("Days Left")
        st.dataframe(df, use_container_width=True, hide_index=True)

# Tab 2: AI Timetable
with tab2:
    if st.button("🚀 Generate Smart AI Timetable", type="primary"):
        if not data["subjects"]:
            st.warning("Pehle subjects add karo!")
        else:
            with st.spinner("AI timetable bana raha hai..."):
                df = pd.DataFrame(data["subjects"])
                df["days_left"] = df["exam"].apply(lambda x: (x - datetime.now().date()).days)
                df["priority"] = (30 - df["days_left"]) * 0.7 + df["difficulty"] * 0.3
                df = df.sort_values("priority", ascending=False)
                total = df["priority"].sum() or 1
                daily_hours = 6
                st.success("✅ AI Timetable Ready!")
                for day in range(7):
                    st.write(f"**Day {day+1} - {(datetime.now() + timedelta(days=day)).strftime('%A')}**")
                    cols = st.columns(len(df))
                    for i, row in df.iterrows():
                        hrs = round((row["priority"] / total) * daily_hours, 1)
                        with cols[i % len(cols)]:
                            st.metric(row["name"], f"{hrs} hrs")

# Tab 3: Progress Tracker + PDF Download
with tab3:
    st.subheader("Mark Syllabus Progress")
    for i, sub in enumerate(data["subjects"]):
        with st.expander(f"📖 {sub['name']} (Exam: {sub['exam']})"):
            for topic in sub.get("syllabus", []):
                done = st.checkbox(topic, value=sub["progress"].get(topic, False), key=f"prog_{i}_{topic}")
                sub["progress"][topic] = done

            st.subheader("📥 Download Resources")
            col1, col2, col3 = st.columns(3)
            with col1:
                if sub.get("syllabus_pdf"):
                    with open(sub["syllabus_pdf"], "rb") as f:
                        st.download_button("📘 Syllabus PDF", f, file_name=os.path.basename(sub["syllabus_pdf"]))
            with col2:
                if sub.get("pyq_pdf"):
                    with open(sub["pyq_pdf"], "rb") as f:
                        st.download_button("📝 PYQs PDF", f, file_name=os.path.basename(sub["pyq_pdf"]))
            with col3:
                if sub.get("book_pdf"):
                    with open(sub["book_pdf"], "rb") as f:
                        st.download_button("📚 Book/Notes PDF", f, file_name=os.path.basename(sub["book_pdf"]))

    if st.button("Save All Progress"):
        save_data(data)
        st.success("Saved!")

# Tab 4: Pomodoro
with tab4:
    st.subheader("⏰ Pomodoro Timer")
    if st.button("Start 25 min Study Session"):
        st.success("Focus mode ON! 25 minutes baad break lo ☕")
        st.balloons()

# Tab 5: AI Tips
with tab5:
    tips = [
        "Exam se 7 din pehle full syllabus revise karo",
        "Hard chapters subah padho",
        "Har Pomodoro ke baad 5 min break lo",
        "Phone silent mode rakhna",
        "Daily 10 min previous year questions solve karo"
    ]
    st.info("💡 Today's AI Tip: " + random.choice(tips))

# ====================== ADMIN FEATURES (Only when Admin logged in) ======================
if is_admin:
    st.divider()
    st.subheader("🔧 Admin Panel - Add / Edit / Delete Subjects")

    # Add New Subject
    st.subheader("➕ Add New Subject")
    name = st.text_input("Subject Name", key="add_name")
    exam_date = st.date_input("Exam Date", value=datetime.now().date() + timedelta(days=30), key="add_date")
    difficulty = st.slider("Difficulty (1-10)", 1, 10, 5, key="add_diff")
    syllabus = st.text_area("Syllabus Topics (one per line)", placeholder="Chapter 1: Algebra\nChapter 2: Trigonometry", key="add_syl")
    
    if st.button("Add Subject & Syllabus", type="primary"):
        topics = [t.strip() for t in syllabus.split("\n") if t.strip()]
        data["subjects"].append({
            "name": name,
            "exam": exam_date,
            "difficulty": difficulty,
            "syllabus": topics,
            "progress": {t: False for t in topics},
            "syllabus_pdf": None,
            "pyq_pdf": None,
            "book_pdf": None
        })
        save_data(data)
        st.success("✅ Added!")
        st.rerun()

    # Manage Subjects (Edit + Delete + PDF Upload)
    st.subheader("✏️ Manage Subjects")
    for idx, sub in enumerate(data["subjects"]):
        with st.expander(f"📖 {sub['name']}"):
            new_name = st.text_input("Name", value=sub["name"], key=f"name_{idx}")
            new_exam = st.date_input("Exam Date", value=sub["exam"], key=f"date_{idx}")
            new_diff = st.slider("Difficulty", 1, 10, sub["difficulty"], key=f"diff_{idx}")
            new_syl = st.text_area("Syllabus", value="\n".join(sub["syllabus"]), key=f"syl_{idx}")

            st.subheader("📎 Upload Resources")
            syl_pdf = st.file_uploader("Syllabus PDF", type="pdf", key=f"syl_pdf_{idx}")
            pyq_pdf = st.file_uploader("PYQs PDF", type="pdf", key=f"pyq_pdf_{idx}")
            book_pdf = st.file_uploader("Book PDF", type="pdf", key=f"book_pdf_{idx}")

            if syl_pdf:
                path = os.path.join(UPLOAD_FOLDER, f"syl_{idx}_{syl_pdf.name}")
                with open(path, "wb") as f: f.write(syl_pdf.getbuffer())
                sub["syllabus_pdf"] = path
            if pyq_pdf:
                path = os.path.join(UPLOAD_FOLDER, f"pyq_{idx}_{pyq_pdf.name}")
                with open(path, "wb") as f: f.write(pyq_pdf.getbuffer())
                sub["pyq_pdf"] = path
            if book_pdf:
                path = os.path.join(UPLOAD_FOLDER, f"book_{idx}_{book_pdf.name}")
                with open(path, "wb") as f: f.write(book_pdf.getbuffer())
                sub["book_pdf"] = path

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", key=f"save_{idx}"):
                    topics = [t.strip() for t in new_syl.split("\n") if t.strip()]
                    data["subjects"][idx] = {
                        "name": new_name, "exam": new_exam, "difficulty": new_diff,
                        "syllabus": topics, "progress": {t: False for t in topics},
                        "syllabus_pdf": sub.get("syllabus_pdf"),
                        "pyq_pdf": sub.get("pyq_pdf"),
                        "book_pdf": sub.get("book_pdf")
                    }
                    save_data(data)
                    st.success("✅ Updated!")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Subject", key=f"del_{idx}", type="primary"):
                    if st.checkbox("Confirm Delete?", key=f"conf_{idx}"):
                        del data["subjects"][idx]
                        save_data(data)
                        st.success("✅ Deleted!")
                        st.rerun()
                    else:
                        st.error("Confirm Delete tick karo!")

else:
    st.info("👨‍🎓 Student Mode: View only")

st.caption("AI Study Planner • Student + Admin Login • Made for Students")













