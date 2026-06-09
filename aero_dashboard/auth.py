import streamlit as st


def _auth_check(username: str, password: str) -> bool:
    """Check credentials against `st.secrets['users']` if present.

    If no users are configured in secrets, allow any non-empty username
    (demo mode).
    """
    try:
        users = st.secrets.get("users", {})
    except Exception:
        users = {}

    if users:
        return users.get(username) == password

    return bool(username.strip())


def current_user() -> str | None:
    return st.session_state.get("user")


def sign_out() -> None:
    st.session_state.pop("user", None)
    st.session_state.pop("show_signin", None)
    st.session_state.pop("signin_username", None)
    st.session_state.pop("signin_password", None)
    st.session_state.pop("signin_remember", None)
    return


def render_signin_card() -> None:
    # Clear form fields for fresh login
    if "signin_username" not in st.session_state:
        st.session_state["signin_username"] = ""
    if "signin_password" not in st.session_state:
        st.session_state["signin_password"] = ""
    if "signin_remember" not in st.session_state:
        st.session_state["signin_remember"] = False
    
    st.markdown(
        """
        <style>
        .signin-card {max-width:600px;margin:3rem auto;padding:2rem;border-radius:8px;
            box-shadow:0 6px 30px rgba(2,6,23,0.2);background:#ffffff;}
        .signin-title{font-family:Inter, sans-serif;color:#0f172a;margin:0 0 0.25rem 0}
        .signin-sub{color:#475569;margin:0 0 1rem 0}
        .signin-note{color:#64748b;margin-top:1rem;font-size:0.95rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="signin-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="signin-title">Aero Dashboard sign in</h2>', unsafe_allow_html=True)
    st.markdown(
        '<div class="signin-sub">Sign in to access the aerodynamic simulator content.</div>',
        unsafe_allow_html=True,
    )

    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")
    remember = st.checkbox("Remember me", key="signin_remember")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign in", key="auth_signin"):
            if not username.strip():
                st.error("Please enter a username.")
            else:
                try:
                    ok = _auth_check(username.strip(), password)
                except Exception as exc:
                    st.error(f"Authentication error: {exc}")
                    ok = False

                if ok:
                    st.session_state["user"] = username.strip()
                    st.session_state["show_signin"] = False
                    if remember:
                        st.session_state["remember"] = True
                    st.success(f"Signed in as {st.session_state['user']}")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    with col2:
        if st.button("Continue as Guest", key="auth_guest"):
            st.session_state["user"] = "guest"
            st.session_state["show_signin"] = False
            st.info("Continuing as guest")
            st.rerun()

    try:
        if st.secrets.get("users"):
            st.caption("Tip: configured users detected in Streamlit secrets.")
    except Exception:
        pass

    st.markdown('</div>', unsafe_allow_html=True)
