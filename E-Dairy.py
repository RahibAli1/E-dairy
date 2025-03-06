import streamlit as st
import sqlite3

st.markdown(
    """
    <style>
    .stApp {
        background-color:rgb(98, 141, 228);  /* Light gray background */
    }
    .social-media-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    .social-media-links a {
        text-decoration: none;
        color: white;
        font-size: 24px;
        transition: color 0.3s ease;
    }
    .social-media-links a:hover {
        color: #ffcc00;  /* Yellow color on hover */
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)


def init_db():
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
   
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            comment TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = "RM"


init_db()


users = {
    "RM": "123456",
    "Ali": "654321",
}

def login(username, password):
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("✅ Login successful!")
    else:
        st.error("❌ Invalid username or password.")

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("✅ Logged out successfully!")

# Task management functions
def add_task(task, category):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (task, completed, category) VALUES (?, ?, ?)', (task, False, category))
    conn.commit()
    conn.close()

def get_tasks(category=None, show_completed=False):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    query = 'SELECT * FROM tasks'
    if category and category != "All":
        query += f" WHERE category = '{category}'"
    if not show_completed:
        if "WHERE" in query:
            query += " AND completed = 0"
        else:
            query += " WHERE completed = 0"
    c.execute(query)
    tasks = [{'id': row[0], 'task': row[1], 'completed': bool(row[2]), 'category': row[3]} for row in c.fetchall()]
    conn.close()
    return tasks

def delete_task(task_id):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def toggle_task_completion(task_id, completed):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    conn.commit()
    conn.close()

def update_task(task_id, new_task):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET task = ? WHERE id = ?', (new_task, task_id))
    conn.commit()
    conn.close()


def add_feedback(username, comment):
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (username, comment) VALUES (?, ?)', (username, comment))
    conn.commit()
    conn.close()

def get_feedback():
    conn = sqlite3.connect('e_diary.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedback')
    feedback = [{'username': row[1], 'comment': row[2]} for row in c.fetchall()]
    conn.close()
    return feedback

st.title("🔒 Login to E-Diary")

if st.session_state.logged_in:
    st.write(f"👋 Welcome, {st.session_state.username}!")
    if st.button("🚪 Logout"):
        logout()
        st.rerun()
else:
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("🔓 Login"):
        login(username, password)
        st.rerun()

if not st.session_state.logged_in:
    st.warning("⚠️ Please log in to access the app.")
    st.stop()


st.title("📝 E-Diary")

st.sidebar.header("🔍 Filters")
category_filter = st.sidebar.selectbox("📂 Category", ["All", "Work", "Personal", "Shopping", "Other"])
show_completed = st.sidebar.checkbox("✅ Show Completed Tasks")

with st.form("add_task_form"):
    task = st.text_input("➕ Add a new task:").strip()
    category = st.selectbox("📂 Category", ["Work", "Personal", "Shopping", "Other"])
    if st.form_submit_button("➕ Add Task") and task:
        add_task(task, category)
        st.rerun()

st.subheader("📋 Your Tasks:")
tasks = get_tasks(category_filter, show_completed)
if not tasks:
    st.write("📭 No tasks found. Add a task above!")
else:
    for task in tasks:
        col1, col2, col3, col4 = st.columns([0.6, 0.2, 0.1, 0.1])
        with col1:
            if task['completed']:
                st.write(f"~~{task['task']}~~ ({task['category']})")
            else:
                st.write(f"- {task['task']} ({task['category']})")
        with col2:
            new_task = st.text_input("✏️ Edit Task", value=task['task'], key=f"edit_{task['id']}")
            if new_task != task['task']:
                update_task(task['id'], new_task)
                st.rerun()
        with col3:
            if st.button("✅", key=f"complete_{task['id']}"):
                toggle_task_completion(task['id'], not task['completed'])
                st.rerun()
        with col4:
            if st.button("❌", key=f"delete_{task['id']}"):
                delete_task(task['id'])
                st.rerun()

st.title("💬 Comments and Feedback")

with st.form("feedback_form"):
    comment = st.text_area("💭 Leave your feedback or comment:")
    if st.form_submit_button("📤 Submit Feedback"):
        if comment:
            add_feedback(st.session_state.username, comment)
            st.success("✅ Thank you for your feedback!")
        else:
            st.error("❌ Please enter a comment before submitting.")

st.subheader("🗨️ Feedback from Users:")
feedback = get_feedback()
if not feedback:
    st.write("📭 No feedback yet. Be the first to leave a comment!")
else:
    for fb in feedback:
        st.write(f"👤 **{fb['username']}**: 💬 {fb['comment']}")

st.markdown(
    """
    <div class="social-media-links">
        <a href="https://youtube.com/@graphicswithrmdesigning?si=bmk_W2vlkDh7boDJ" target="_blank"><i class="fab fa-youtube"></i></a>
        <a href="https://www.whatsapp.com/" target="_blank"><i class="fab fa-whatsapp"></i></a>
        <a href="https://www.facebook.com/" target="_blank"><i class="fab fa-facebook"></i></a>
        <a href="https://twitter.com/" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="https://www.instagram.com/" target="_blank"><i class="fab fa-instagram"></i></a>
        <a href="https://www.linkedin.com/" target="_blank"><i class="fab fa-linkedin"></i></a>
    </div>
    """,
    unsafe_allow_html=True
)