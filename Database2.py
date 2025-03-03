import streamlit as st


st.markdown(
    """
    <style>
    .stApp {
        background-color:rgb(98, 141, 228);  /* Light gray background */
    }
    </style>
    """,
    unsafe_allow_html=True
)


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""


users = {
    "user1": "password1",
    "user2": "password2",
}


def login(username, password):
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully!")


st.title("🔒 Login to E-Diary")


if st.session_state.logged_in:
    st.write(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        logout()
        st.rerun()
else:
   
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)
        st.rerun()


if not st.session_state.logged_in:
    st.warning("Please log in to access the app.")
    st.stop()  
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

def add_task(task, category):
    st.session_state.tasks.append({
        'id': len(st.session_state.tasks) + 1,
        'task': task,
        'completed': False,
        'category': category
    })

def get_tasks(category=None, show_completed=False):
    tasks = st.session_state.tasks
    if category and category != "All":
        tasks = [task for task in tasks if task['category'] == category]
    if not show_completed:
        tasks = [task for task in tasks if not task['completed']]
    return tasks

def delete_task(task_id):
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]

def toggle_task_completion(task_id, completed):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = completed
            break

def update_task(task_id, new_task):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['task'] = new_task
            break

st.title("📝 E-Diary")

st.sidebar.header("Filters")
category_filter = st.sidebar.selectbox("Category", ["All", "Work", "Personal", "Shopping", "Other"])
show_completed = st.sidebar.checkbox("Show Completed Tasks")

with st.form("add_task_form"):
    task = st.text_input("Add a new task:").strip()
    category = st.selectbox("Category", ["Work", "Personal", "Shopping", "Other"])
    if st.form_submit_button("Add Task") and task:
        add_task(task, category)
        st.rerun()

st.subheader("Your Tasks:")
tasks = get_tasks(category_filter, show_completed)
if not tasks:
    st.write("No tasks found. Add a task above!")
else:
    for task in tasks:
        col1, col2, col3, col4 = st.columns([0.6, 0.2, 0.1, 0.1])
        with col1:
            if task['completed']:
                st.write(f"~~{task['task']}~~ ({task['category']})")
            else:
                st.write(f"- {task['task']} ({task['category']})")
        with col2:
            new_task = st.text_input("Edit Task", value=task['task'], key=f"edit_{task['id']}")
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