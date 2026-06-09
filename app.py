import streamlit as st

from aero_dashboard import auth
from aero_dashboard.app_main import main as dashboard_main


def main() -> None:
    if auth.current_user() is None:
        st.markdown("# Welcome to the Aero Dashboard")
        st.markdown("Click the button below to sign in and access the simulator.")

        if st.button("Sign in"):
            st.session_state["show_signin"] = True
            return

        if st.session_state.get("show_signin"):
            auth.render_signin_card()

        return

    if st.sidebar.button("Sign out"):
        auth.sign_out()
        return

    dashboard_main()


if __name__ == "__main__":
    main()
