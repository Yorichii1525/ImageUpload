import streamlit as st
import requests
import os

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Media Feed", page_icon="📸", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def login(email: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state.token = token
            me_response = requests.get(
                f"{API_BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if me_response.status_code == 200:
                user_data = me_response.json()
                st.session_state.user_email = user_data["email"]
                st.session_state.user_id = user_data["id"]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    except Exception as e:
        st.error(f"Error: {e}")

def register(email: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"email": email, "password": password}
        )
        if response.status_code == 201:
            st.success("Registered successfully! Please login.")
        else:
            st.error(f"Registration failed: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")

def logout():
    st.session_state.token = None
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.rerun()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def upload_file(file, caption):
    try:
        files = {"file": (file.name, file, file.type)}
        data = {"caption": caption}
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            data=data,
            headers=get_headers()
        )
        if response.status_code == 200:
            st.success("Uploaded successfully!")
            st.rerun()
        else:
            st.error(f"Upload failed: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")

def get_feed():
    try:
        response = requests.get(f"{API_BASE_URL}/feed", headers=get_headers())
        if response.status_code == 200:
            return response.json()["posts"]
        else:
            st.error(f"Failed to load feed: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")
    return []

def delete_post(post_id):
    try:
        response = requests.delete(
            f"{API_BASE_URL}/posts/{post_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            st.success("Post deleted!")
            st.rerun()
        else:
            st.error(f"Delete failed: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")

def render_auth_page():
    st.title("📸 Media Feed")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            if email and password:
                login(email, password)
            else:
                st.warning("Please enter email and password")
    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register", use_container_width=True):
            if email and password:
                register(email, password)
            else:
                st.warning("Please enter email and password")

def render_feed_page():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📸 Media Feed")
    with col2:
        st.write(f"👤 {st.session_state.user_email}")
        if st.button("Logout", use_container_width=True):
            logout()

    st.divider()

    with st.expander("📤 Upload New Post", expanded=False):
        uploaded_file = st.file_uploader("Choose image or video", type=["png", "jpg", "jpeg", "gif", "mp4", "mov", "avi"])
        caption = st.text_area("Caption", placeholder="What's on your mind?")
        if st.button("Upload", use_container_width=True):
            if uploaded_file:
                upload_file(uploaded_file, caption)
            else:
                st.warning("Please select a file")

    st.divider()

    posts = get_feed()
    if not posts:
        st.info("No posts yet. Be the first to upload!")
        return

    for post in posts:
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.write(f"**{post['email']}**")
                st.caption(post['created_at'][:16].replace('T', ' '))
            with col2:
                st.write(post['caption'] or "_No caption_")
            
            if post['file_type'] == 'image':
                st.image(post['url'], use_container_width=True)
            else:
                st.video(post['url'])
            
            if post['is_owner']:
                if st.button("🗑️ Delete", key=f"del_{post['id']}", use_container_width=True):
                    delete_post(post['id'])
            
            st.divider()

def main():
    if st.session_state.token is None:
        render_auth_page()
    else:
        render_feed_page()

if __name__ == "__main__":
    main()