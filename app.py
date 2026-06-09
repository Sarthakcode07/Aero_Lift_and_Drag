import streamlit as st

from aero_dashboard.app_main import main as dashboard_main


def _render_signin_page() -> None:
    st.title("Welcome to the Aero Dashboard")
    st.write("Sign in to access the aerodynamic simulator and tools.")

    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign in"):
            if username.strip() == "":
                st.error("Please enter a username.")
            else:
                # Simple session-based sign-in (not secure — for demo only)
                st.session_state["user"] = username.strip()
                st.success(f"Signed in as {st.session_state['user']}")
                st.experimental_rerun()
    with col2:
        if st.button("Continue as Guest"):
            st.session_state["user"] = "guest"
            st.info("Continuing as guest")
            st.experimental_rerun()


def _render_signed_in_header() -> None:
    user = st.session_state.get("user")
    if user:
        st.sidebar.markdown(f"**Signed in as:** {user}")
        if st.sidebar.button("Sign out"):
            del st.session_state["user"]
            st.experimental_rerun()


def main() -> None:
    if "user" not in st.session_state:
        _render_signin_page()
    else:
        _render_signed_in_header()
        dashboard_main()


if __name__ == "__main__":
    main()
