import streamlit as st


def _auth_users() -> dict[str, str]:
    try:
        users = dict(st.secrets.get("users", {}) or {})
    except Exception:
        users = {}

    users.update(st.session_state.setdefault("mock_users", {}))
    if not users:
        users["demo"] = "demo123"
    return users


def _auth_check(username: str, password: str) -> bool:
    users = _auth_users()
    if users:
        return users.get(username) == password
    return bool(username.strip())


def _register_user(username: str, password: str) -> None:
    st.session_state.setdefault("mock_users", {})[username] = password


def current_user() -> str | None:
    return st.session_state.get("user")


def is_authenticated() -> bool:
    user = current_user()
    return bool(user) and user != "guest"


def sign_out() -> None:
    for key in [
        "user",
        "show_signin",
        "signin_username",
        "signin_password",
        "signin_remember",
        "remember_me",
        "auth_view",
    ]:
        st.session_state.pop(key, None)


def get_user_profile(username: str) -> dict[str, str]:
    if not username:
        return {
            "display_name": "Pilot",
            "pilot_alias": "Aero Operator",
            "preferred_aircraft": "Cessna 172",
            "recent_session": "No active sessions yet",
            "saved_presets": "0",
            "pilot_tier": "Observer",
            "summary": "Sign in to see your dashboard preferences.",
        }

    name_key = username.replace("@", "").replace(".", "").lower()
    seed = sum(ord(char) for char in name_key)
    options = [
        {
            "display_name": username.title(),
            "pilot_alias": "Windshadow",
            "preferred_aircraft": "Cessna 172",
            "recent_session": "High-lift takeoff study",
            "saved_presets": "5",
            "pilot_tier": "Lift Captain",
            "summary": "You have saved personalized presets and recent aerodynamic sessions waiting.",
        },
        {
            "display_name": username.title(),
            "pilot_alias": "Sky Beacon",
            "preferred_aircraft": "Boeing 737-800",
            "recent_session": "Cruise drag polar analysis",
            "saved_presets": "3",
            "pilot_tier": "Drag Analyst",
            "summary": "Your dashboard is tuned for long-range flight planning and performance checks.",
        },
        {
            "display_name": username.title(),
            "pilot_alias": "Nightwing",
            "preferred_aircraft": "F-16 Falcon",
            "recent_session": "Supersonic climb profile",
            "saved_presets": "7",
            "pilot_tier": "Aero Ace",
            "summary": "Fast pilot workflows and mission-ready presets are already prepared.",
        },
    ]
    return options[seed % len(options)]


def _auth_page_style() -> str:
    return """
    <style>
        body, .stApp, .main, .block-container {
            min-height: 100vh !important;
            background: radial-gradient(circle at top right, rgba(37, 99, 235, 0.18), transparent 22%),
                        radial-gradient(circle at bottom left, rgba(14, 165, 233, 0.12), transparent 20%),
                        #020617 !important;
            color: #f8fafc !important;
        }

        .auth-card {
            max-width: 720px;
            margin: 3rem auto 4rem auto;
            padding: 2rem 2.25rem;
            border-radius: 1.25rem;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(7, 16, 40, 0.94);
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.48);
            backdrop-filter: blur(8px);
        }

        .auth-card h1,
        .auth-card h2,
        .auth-card p,
        .auth-card label,
        .auth-card .stMarkdown,
        .auth-card .stTextInput,
        .auth-card .stCheckbox,
        .stRadio label,
        .stRadio div,
        .stRadio span,
        .stCheckbox label,
        .stCheckbox div,
        .stCheckbox span {
            color: #f8fafc !important;
        }

        .auth-tab-row {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 1.75rem;
        }

        .auth-tab {
            padding: 0.75rem 1.1rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(148, 163, 184, 0.06);
            color: #f8fafc !important;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.18s ease;
        }

        .auth-tab-active {
            background: rgba(59, 130, 246, 0.45);
            border-color: rgba(59, 130, 246, 0.56);
            color: #ffffff !important;
            box-shadow: 0 18px 34px rgba(59, 130, 246, 0.18);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
        }

        .auth-small-link {
            color: #60a5fa !important;
            text-decoration: none;
            font-size: 0.92rem;
        }

        .auth-small-link:hover {
            text-decoration: underline;
        }

        .auth-note {
            color: #cbd5e1 !important;
            font-size: 0.95rem;
            margin-top: 1rem;
        }

        .auth-card .stButton>button,
        .auth-card .stButton>button span {
            border-radius: 0.85rem !important;
            color: #000000 !important;
        }

        .stTextInput>label,
        .stTextInput>div>label,
        .stTextInput>div>div {
            color: #f8fafc !important;
        }

        .stTextInput input,
        .stTextInput>div>div>input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox select {
            color: #000000 !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: rgba(15, 23, 42, 0.5) !important;
        }
    </style>
    """


def render_signin_card() -> None:
    if "signin_username" not in st.session_state:
        st.session_state["signin_username"] = ""
    if "signin_password" not in st.session_state:
        st.session_state["signin_password"] = ""
    if "signin_remember" not in st.session_state:
        st.session_state["signin_remember"] = False
    if "signup_username" not in st.session_state:
        st.session_state["signup_username"] = ""
    if "signup_password" not in st.session_state:
        st.session_state["signup_password"] = ""
    if "signup_confirm" not in st.session_state:
        st.session_state["signup_confirm"] = ""
    if "auth_view" not in st.session_state:
        st.session_state["auth_view"] = "signin"

    st.markdown(_auth_page_style(), unsafe_allow_html=True)
    auth_view = st.radio(
        "",
        ["Sign in", "Sign up"],
        index=0 if st.session_state["auth_view"] == "signin" else 1,
        horizontal=True,
        key="auth_view",
        label_visibility="collapsed",
    )

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<h1>Welcome to Aero control</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="margin:0 0 1.5rem 0; color: #ffffff;">Use secure access to unlock aerodynamic presets, personalized mission data, and simulator controls.</p>',
        unsafe_allow_html=True,
    )

    if auth_view == "Sign in":
        with st.form("signin_form"):
            username = st.text_input("Username", key="signin_username")
            password = st.text_input("Password", type="password", key="signin_password")
            remember = st.checkbox("Remember me", key="signin_remember")

            col1, col2 = st.columns([2, 1])
            with col1:
                submitted = st.form_submit_button("Sign in")
            with col2:
                forgot = st.form_submit_button("Forgot password")

        if submitted:
            if not username.strip():
                st.error("Please enter your username.")
            elif not password:
                st.error("Please enter your password.")
            else:
                ok = _auth_check(username.strip(), password)
                if ok:
                    st.session_state["user"] = username.strip()
                    st.session_state["remember_me"] = remember
                    st.success(f"Signed in as {st.session_state['user']}")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")

        if "forgot" in locals() and forgot:
            st.info(
                "Forgot password support is UI-only in this demo. Create a new account or reuse your current credentials."
            )

        if st.session_state.get("remember_me"):
            st.caption("Your username will be kept in the session until you sign out.")

    else:
        with st.form("signup_form"):
            username = st.text_input("Choose username", key="signup_username")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
            remember = st.checkbox("Remember me", key="signin_remember")
            agreement = st.checkbox("I agree to use this demo account responsibly.", value=True)

            submitted = st.form_submit_button("Create account")

        if submitted:
            if not username.strip():
                st.error("Please choose a username.")
            elif username.strip() in _auth_users():
                st.error("This username is already taken. Please choose another one.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not agreement:
                st.error("You must agree to the demo terms to create an account.")
            else:
                _register_user(username.strip(), password)
                st.session_state["user"] = username.strip()
                st.session_state["remember_me"] = remember
                st.success(f"Account created for {username.strip()}. You are now signed in.")
                st.experimental_rerun()

        st.markdown(
            '<p class="auth-note">Your signup is stored for this browser session only in demo mode. No backend credentials are transmitted.</p>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
