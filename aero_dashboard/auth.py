import streamlit as st
from datetime import datetime

MIN_PASSWORD_LENGTH = 6
DEFAULT_USERS = {"demo": "demo123"}


def _init_user_store() -> None:
    if "mock_users" not in st.session_state:
        try:
            configured = dict(st.secrets.get("users", {}))
        except Exception:
            configured = {}

        if not configured:
            configured = DEFAULT_USERS.copy()

        st.session_state["mock_users"] = configured


def _auth_check(username: str, password: str) -> bool:
    _init_user_store()
    return bool(username and password and st.session_state["mock_users"].get(username) == password)


def _user_exists(username: str) -> bool:
    _init_user_store()
    return username in st.session_state["mock_users"]


def _register_user(username: str, password: str) -> tuple[bool, str | None]:
    _init_user_store()
    if _user_exists(username):
        return False, "Username already exists."
    st.session_state["mock_users"][username] = password
    return True, None


def current_user() -> str | None:
    return st.session_state.get("user")


def user_session_profile() -> dict[str, str]:
    user = current_user()
    if not user:
        return {}

    started = st.session_state.setdefault(
        "session_started",
        datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    )
    return {
        "username": user,
        "session_started": started,
        "recent_project": f"{user.title()}'s lift optimization",
        "user_tier": "Aero Pilot",
        "user_zone": "Midnight Ops",
    }


def sign_out() -> None:
    for key in [
        "user",
        "auth_mode",
        "signin_username",
        "signin_password",
        "signup_username",
        "signup_password",
        "signup_confirm_password",
        "remember_me",
        "forgot_password_clicked",
    ]:
        st.session_state.pop(key, None)
    return


def require_login() -> bool:
    if current_user():
        return True
    render_auth_page()
    return False


def _set_default_auth_state() -> None:
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    if "remember_me" not in st.session_state:
        st.session_state["remember_me"] = False
    if "forgot_password_clicked" not in st.session_state:
        st.session_state["forgot_password_clicked"] = False
    if "signin_username" not in st.session_state:
        st.session_state["signin_username"] = ""
    if "signin_password" not in st.session_state:
        st.session_state["signin_password"] = ""
    if "signup_username" not in st.session_state:
        st.session_state["signup_username"] = ""
    if "signup_password" not in st.session_state:
        st.session_state["signup_password"] = ""
    if "signup_confirm_password" not in st.session_state:
        st.session_state["signup_confirm_password"] = ""


def render_auth_page() -> None:
    _set_default_auth_state()
    params = st.experimental_get_query_params()
    if "signup" in params:
        st.session_state["auth_mode"] = "signup"
    elif "login" in params:
        st.session_state["auth_mode"] = "login"

    st.markdown(
        """
        <style>
        html, body, .stApp, .main, .block-container {
            background: #020617 !important;
            color: #f8fafc !important;
        }
        .stApp {
            background-image:
                radial-gradient(circle at 18% 18%, rgba(56, 189, 248, 0.16), transparent 18%),
                radial-gradient(circle at 82% 16%, rgba(14, 165, 233, 0.10), transparent 22%),
                radial-gradient(circle at 52% 90%, rgba(59, 130, 246, 0.12), transparent 24%);
            background-color: #020617 !important;
        }
        .auth-card {
            background: rgba(8, 17, 38, 0.94);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 24px;
            box-shadow: 0 28px 70px rgba(2, 4, 18, 0.42);
            padding: 2.4rem;
        }
        .auth-panel {
            padding: 2rem 1.8rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 24px;
            background: rgba(7, 14, 30, 0.7);
            backdrop-filter: blur(12px);
        }
        .auth-title {
            font-family: Inter, sans-serif;
            font-size: 2.4rem;
            font-weight: 700;
            line-height: 1.05;
            margin-bottom: 0.6rem;
            color: #e2e8f0;
        }
        .auth-subtitle {
            margin: 0 0 1.8rem 0;
            color: #94a3b8;
            font-size: 0.96rem;
            line-height: 1.7;
        }
        .auth-label {
            color: #e2e8f0 !important;
        }
        .auth-link {
            color: #60a5fa;
            text-decoration: none;
        }
        .auth-link:hover {
            color: #93c5fd;
        }
        .auth-footer {
            margin-top: 1.5rem;
            color: #94a3b8;
            font-size: 0.95rem;
        }
        .auth-columns > div {
            min-height: 18rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown('<div class="auth-panel">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">Aero Dashboard Access</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-subtitle">Welcome to your simulated flight operations workspace. Sign in or create a new account to continue to the protected dashboard.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <ul style="padding-left:1.3rem;color:#cbd5e1;line-height:1.9;">
                <li>Front-end sign in and sign up experience</li>
                <li>Remember me option and password reset placeholder</li>
                <li>Protected dashboard access for logged-in sessions</li>
                <li>Midnight radial glow styling for a polished landing page</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        mode = st.session_state["auth_mode"]
        if mode == "login":
            st.markdown('<div class="auth-title" style="font-size:1.65rem;">Sign in to your account</div>', unsafe_allow_html=True)
            with st.form("signin_form"):
                username = st.text_input("Username", key="signin_username", label_visibility="visible")
                password = st.text_input("Password", type="password", key="signin_password", label_visibility="visible")
                remember = st.checkbox("Remember me", key="remember_me")
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    submitted = st.form_submit_button("Sign in")
                with col_b:
                    forgot = st.form_submit_button("Forgot password")

            if forgot:
                st.session_state["forgot_password_clicked"] = True
            if submitted:
                if not username.strip():
                    st.error("Please enter a username.")
                elif not password:
                    st.error("Please enter your password.")
                elif not _auth_check(username.strip(), password):
                    st.error("Invalid username or password.")
                else:
                    st.session_state["user"] = username.strip()
                    st.session_state["remember_me"] = remember
                    st.success(f"Welcome back, {st.session_state['user']}!")
                    st.experimental_rerun()

            if st.session_state["forgot_password_clicked"]:
                st.info(
                    "This is a UI-only placeholder for password recovery. "
                    "In a production app, you'd send an email reset link from the backend."
                )
            if st.button("Create an account", key="goto_signup"):
                st.session_state["auth_mode"] = "signup"
                st.experimental_rerun()

        else:
            st.markdown('<div class="auth-title" style="font-size:1.65rem;">Create your account</div>', unsafe_allow_html=True)
            with st.form("signup_form"):
                username = st.text_input("Choose a username", key="signup_username", label_visibility="visible")
                password = st.text_input("Create a password", type="password", key="signup_password", label_visibility="visible")
                confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm_password", label_visibility="visible")
                remember = st.checkbox("Remember me", key="remember_me")
                submitted = st.form_submit_button("Sign up")

            if submitted:
                if not username.strip():
                    st.error("Please choose a username.")
                elif len(password) < MIN_PASSWORD_LENGTH:
                    st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif _user_exists(username.strip()):
                    st.error("That username is already taken.")
                else:
                    success, message = _register_user(username.strip(), password)
                    if success:
                        st.session_state["user"] = username.strip()
                        st.session_state["remember_me"] = remember
                        st.success("Account created successfully. Redirecting to dashboard...")
                        st.experimental_rerun()
                    else:
                        st.error(message or "Unable to create account.")

            if st.button("Already have an account? Sign in", key="goto_login"):
                st.session_state["auth_mode"] = "login"
                st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)
