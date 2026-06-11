import streamlit as st

from aero_dashboard import auth
from aero_dashboard.app_main import main as dashboard_main


def main() -> None:
    if not auth.require_login():
        return

    if st.sidebar.button("Sign out"):
        auth.sign_out()
        st.experimental_rerun()

    dashboard_main()


if __name__ == "__main__":
    main()
