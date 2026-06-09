import streamlit as st
from typing import Optional

from aero_dashboard.app_main import main as dashboard_main


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
        # secrets should be like: {"users": {"alice": "s3cret", ...}}
        return users.get(username) == password

    # Demo mode: accept any non-empty username (no password required)
    return bool(username.strip())


def _render_signin_page() -> None:
    # Centered card layout
    st.markdown(
        """
        <style>
        .signin-card {max-width:600px;margin:3rem auto;padding:2rem;border-radius:8px;
            box-shadow:0 6px 30px rgba(2,6,23,0.2);background:#ffffff;}
        .signin-title{font-family:Inter, sans-serif;color:#0f172a;margin:0 0 0.25rem 0}
        .signin-sub{color:#475569;margin:0 0 1rem 0}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="signin-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="signin-title">Aero Dashboard</h2>', unsafe_allow_html=True)
    st.markdown('<div class="signin-sub">Sign in to continue to the aerodynamic simulator</div>', unsafe_allow_html=True)

    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")
    remember = st.checkbox("Remember me", key="signin_remember")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign in"):
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
                    if remember:
                        st.session_state["remember"] = True
                    st.success(f"Signed in as {st.session_state['user']}")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
    with col2:
        if st.button("Continue as Guest"):
            st.session_state["user"] = "guest"
            st.info("Continuing as guest")
            st.experimental_rerun()

    # Helpful hints if using secrets
    try:
        if st.secrets.get("users"):
            st.caption("Tip: configured users detected in Streamlit secrets.")
    except Exception:
        pass

    st.markdown('</div>', unsafe_allow_html=True)


def _render_signed_in_header() -> None:
    user = st.session_state.get("user")
    if user:
        st.sidebar.markdown(f"**Signed in as:** {user}")
        if st.sidebar.button("Sign out"):
            st.session_state.pop("user", None)
            st.experimental_rerun()


def main() -> None:
    # Ensure session state keys exist
    if "user" not in st.session_state:
        _render_signin_page()
    else:
        _render_signed_in_header()
        dashboard_main()


if __name__ == "__main__":
    main()
