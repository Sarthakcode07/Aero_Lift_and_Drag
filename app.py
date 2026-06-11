import streamlit as st

from aero_dashboard import auth
from aero_dashboard.app_main import main as dashboard_main


def main() -> None:
    if not auth.is_authenticated():
        st.markdown("# Welcome to the Aero Dashboard")
        st.markdown("Access the simulator with a signed-in account.")
        if st.session_state.get("show_signin", True):
            auth.render_signin_card()
        return

    if st.sidebar.button("Sign out"):
        auth.sign_out()
        return

    dashboard_main()


if __name__ == "__main__":
    main()
