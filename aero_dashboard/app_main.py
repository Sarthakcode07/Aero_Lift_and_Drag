import streamlit as st
import matplotlib.pyplot as plt

from aero_dashboard import auth, visuals, agent


def main() -> None:
    st.set_page_config(
        page_title="Aero Lift & Drag Simulator",
        page_icon="✈️",
        layout="wide",
    )

    if auth.current_user() is None:
        st.markdown("# Access Restricted")
        st.markdown("Please sign in to access the aerodynamic simulator.")
        if st.button("Sign in", key="page_signin"):
            # Immediately continue as guest and show dashboard
            st.session_state["user"] = "guest"
            st.session_state["show_signin"] = False
            st.experimental_rerun()

        if st.session_state.get("show_signin"):
            auth.render_signin_card()

        return

    # inject styling
    st.markdown(visuals._style_axes.__doc__ or "", unsafe_allow_html=True)
    # NOTE: we still call visuals functions directly for markup
    visuals_apply = getattr(visuals, 'apply_aerospace_theme', None)
    if visuals_apply:
        visuals_apply()

    site_header = getattr(visuals, 'site_header', None)
    if site_header:
        site_header()

    # Top-right Sign in / Switch user button
    try:
        header_cols = st.columns([8, 1])
        with header_cols[1]:
            current_user = st.session_state.get("user")
            if current_user:
                st.markdown(f"**{current_user}**")
                if st.button("Switch user"):
                    st.session_state.pop("user", None)
                    return
            else:
                if st.button("Sign in"):
                    st.session_state.pop("user", None)
                    return
    except Exception:
        # If session state isn't available for any reason, ignore header button
        pass

    if st.sidebar.button("Sign out"):
        auth.sign_out()
        return

    # Aircraft presets for `Select Aircraft Profile`
    aircraft_presets = {
        "Cessna 172": {
            "wing_area": 16.2,  # m^2 (≈174 ft^2)
            "empty_weight_kg": 767.0,  # kg (approx)
            "max_velocity": 70.0,  # m/s (≈135 kt)
        },
        "Boeing 737-800": {
            "wing_area": 125.0,  # m^2 (approx)
            "empty_weight_kg": 41000.0,  # kg (operating empty weight approx)
            "max_velocity": 250.0,  # m/s (cruise ~250 m/s)
        },
        "F-16 Falcon": {
            "wing_area": 27.9,  # m^2 (≈300 ft^2)
            "empty_weight_kg": 3890.0,  # kg (approx)
            "max_velocity": 700.0,  # m/s (approx top speed)
        },
    }

    # Top-of-page aircraft selector
    selected_aircraft = st.selectbox(
        "Select Aircraft Profile",
        options=list(aircraft_presets.keys()),
        index=0,
        key="aircraft_profile_selected",
    )
    profile = aircraft_presets.get(selected_aircraft, aircraft_presets["Cessna 172"])

    with st.sidebar:
        st.markdown(
            f'<p style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:{visuals.TEXT_WHITE};margin-bottom:1rem;">'
            f"Control panel</p>",
            unsafe_allow_html=True,
        )
        # Configure sliders according to selected aircraft profile
        velocity_max = float(profile.get("max_velocity", 300.0))
        velocity_default = float(profile.get("max_velocity", 300.0) * 0.5)
        velocity = st.slider(
            "Velocity (m/s)",
            min_value=0.0,
            max_value=max(velocity_max, 1000.0),
            value=velocity_default,
            step=1.0,
        )

        default_wing = float(profile.get("wing_area", 20.0))
        wing_min = max(0.1, default_wing * 0.2)
        wing_max = max(default_wing * 3.0, default_wing + 1.0)
        wing_area = st.slider(
            "Wing area (m²)",
            min_value=wing_min,
            max_value=wing_max,
            value=default_wing,
            step=0.1,
        )
        lift_coefficient = st.slider(
            "Lift coefficient (Cl)",
            min_value=0.0,
            max_value=2.0,
            value=0.5,
            step=0.01,
        )
        drag_coefficient = st.slider(
            "Drag coefficient (Cd)",
            min_value=0.0,
            max_value=0.5,
            value=0.03,
            step=0.001,
            format="%.3f",
        )
        rho = st.slider(
            "Air density ρ (kg/m³)",
            min_value=0.5,
            max_value=1.5,
            value=1.225,
            step=0.001,
            format="%.3f",
        )

        # model selector
        available_models = agent.get_ollama_models()
        if available_models:
            model_options = available_models
        else:
            model_options = [agent.OLLAMA_MODEL]
        st.selectbox("AI model (Ollama)", model_options, index=0, key="ollama_model_selected")

        # Takeoff simulation inputs
        st.markdown("---")
        st.markdown("**Takeoff simulator inputs**")
        runway_length = st.number_input(
            "Available runway length (m)", min_value=50, max_value=5000, value=800, step=10
        )
        aircraft_weight_kg = st.number_input(
            "Aircraft weight (kg)",
            min_value=100.0,
            max_value=200000.0,
            value=float(profile.get("empty_weight_kg", 1000.0)),
            step=10.0,
        )
        payload_kg = st.number_input(
            "Payload + fuel (kg)", min_value=0.0, max_value=50000.0, value=100.0, step=10.0
        )
        # Estimate a default thrust as a fraction of the loaded weight
        est_total = aircraft_weight_kg + float(payload_kg)
        default_thrust = float(est_total * 9.81 * 0.2)
        thrust_n = st.number_input(
            "Available thrust (N)", min_value=0.0, max_value=1e6, value=default_thrust, step=100.0
        )
        rolling_friction = st.slider(
            "Rolling friction μ",
            min_value=0.0,
            max_value=0.2,
            value=0.02,
            step=0.005,
        )

        # Fluid Dynamics Diagnostics
        st.markdown("---")
        st.markdown("**Fluid Dynamics Diagnostics**")
        # characteristic length (simple proxy): square root of wing area
        import math

        char_len = math.sqrt(float(wing_area)) if wing_area and wing_area > 0 else 1.0
        # standard kinematic viscosity of air (m^2/s) at ~15°C
        nu = 1.5e-5
        reynolds = (float(velocity) * char_len) / nu
        # speed of sound (m/s) approximate at sea level
        speed_of_sound = 340.29
        mach = float(velocity) / speed_of_sound if speed_of_sound > 0 else 0.0

        st.metric("Reynolds number (Re)", f"{reynolds:,.2e}")
        st.metric("Mach number (M)", f"{mach:.3f}")

        if mach > 0.3:
            st.warning("Mach > 0.3: Compressibility effects may be significant.")

        # change visual accent if supersonic
        if not hasattr(visuals, "_accent_backup"):
            visuals._accent_backup = visuals.ACCENT_SKY
        if mach > 1.0:
            visuals.ACCENT_SKY = visuals.ACCENT_WARNING
        else:
            visuals.ACCENT_SKY = visuals._accent_backup

    lift_n = 0.5 * rho * velocity**2 * wing_area * lift_coefficient
    drag_n = 0.5 * rho * velocity**2 * wing_area * drag_coefficient
    ld_ratio = lift_n / drag_n if drag_n > 0 else float("inf")

    col_lift, col_drag, col_params = st.columns([1, 1, 1])

    with col_lift:
        st.markdown(
            visuals.metric_card("Lift (L)", f"{lift_n:,.2f}", "N", visuals.TEXT_WHITE, visuals.ACCENT_SKY),
            unsafe_allow_html=True,
        )
    with col_drag:
        st.markdown(
            visuals.metric_card("Drag (D)", f"{drag_n:,.2f}", "N", visuals.TEXT_WHITE, visuals.ACCENT_CYAN),
            unsafe_allow_html=True,
        )
    with col_params:
        st.markdown(
            visuals.settings_card(
                rho,
                velocity,
                wing_area,
                lift_coefficient,
                drag_coefficient,
                ld_ratio,
                empty_weight_kg=aircraft_weight_kg,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<p style="font-family:{visuals.FONT_STACK};font-size:0.9rem;color:{visuals.TEXT_WHITE};'
        f'margin:1rem 0 0 0;">Operating point: '
        f'<span style="color:{visuals.TEXT_WHITE};font-weight:600;">{velocity:.0f} m/s</span> · '
        f'<span style="color:{visuals.TEXT_WHITE};font-weight:600;">S = {wing_area:.1f} m²</span></p>',
        unsafe_allow_html=True,
    )

    st.divider()

    col_v, col_ld = st.columns(2)

    with col_v:
        st.markdown(visuals.section_heading("Performance curve"), unsafe_allow_html=True)
        fig_lift = visuals.build_lift_plot(
            rho, wing_area, lift_coefficient, velocity, lift_n
        )
        st.pyplot(fig_lift)
        plt.close(fig_lift)

    with col_ld:
        st.markdown(visuals.section_heading("Drag polar"), unsafe_allow_html=True)
        fig_ld = visuals.build_lift_vs_drag_plot(
            rho,
            wing_area,
            lift_coefficient,
            drag_coefficient,
            velocity,
            lift_n,
            drag_n,
        )
        st.pyplot(fig_ld)
        plt.close(fig_ld)

    # Takeoff Performance Simulator
    st.divider()
    st.markdown(visuals.section_heading("Takeoff Performance Simulator"), unsafe_allow_html=True)

    # Compute total weight from aircraft weight + payload
    total_weight = float(aircraft_weight_kg) + float(payload_kg)

    sim_col, sim_out = st.columns([2, 1])
    with sim_col:
        run_sim = st.button("Run Takeoff Simulator")
        chart_placeholder = st.empty()
        progress_placeholder = st.empty()

    with sim_out:
        st.markdown(visuals.metric_card("Runway (m)", f"{runway_length}", "m", visuals.TEXT_WHITE, visuals.ACCENT_AMBER), unsafe_allow_html=True)
        st.markdown(visuals.metric_card("Total weight (kg)", f"{total_weight:,.0f}", "kg", visuals.TEXT_WHITE, visuals.ACCENT_CYAN), unsafe_allow_html=True)

    if run_sim:
        import time

        sim = visuals.simulate_takeoff(
            rho,
            wing_area,
            lift_coefficient,
            drag_coefficient,
            total_weight,
            float(runway_length),
            float(thrust_n),
            rolling_friction_coeff=float(rolling_friction),
            dt=0.1,
            max_time=120.0,
        )

        times = sim["times"]
        positions = sim["positions"]
        velocities = sim["velocities"]
        lifts = sim["lifts"]
        drags = sim["drags"]
        outcome = sim["outcome"]

        total_steps = max(1, len(times))
        pb = progress_placeholder.progress(0)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_facecolor(visuals.PLOT_BG)
        fig.patch.set_facecolor(visuals.PLOT_PANEL)
        ax.set_xlabel("Time (s)", color=visuals.TEXT_WHITE)
        ax.set_ylabel("Velocity (m/s)", color=visuals.TEXT_WHITE)

        for i in range(total_steps):
            ax.clear()
            ax.plot(times[: i + 1], velocities[: i + 1], color=visuals.PLOT_LIFT, linewidth=2)
            ax.fill_between(times[: i + 1], velocities[: i + 1], color=visuals.PLOT_LIFT, alpha=0.08)
            ax.set_xlim(0, max(5, times[-1]))
            ax.set_ylim(0, max(10, max(velocities) * 1.1))
            ax.set_facecolor(visuals.PLOT_BG)
            ax.tick_params(colors=visuals.TEXT_WHITE)
            ax.set_xlabel("Time (s)", color=visuals.TEXT_WHITE)
            ax.set_ylabel("Velocity (m/s)", color=visuals.TEXT_WHITE)
            chart_placeholder.pyplot(fig)
            pb.progress(int((i / total_steps) * 100))
            time.sleep(0.02)

        # final progress
        pb.progress(100)

        if outcome.get("lift_off"):
            st.success(
                f"Lift-off! Time: {outcome['lift_off_time']:.1f}s, Distance: {outcome['lift_off_distance']:.1f} m, V={outcome['final_velocity']:.1f} m/s"
            )
        else:
            st.error(
                f"Failed to lift before runway end. Distance covered: {outcome['final_distance']:.1f} m, V={outcome['final_velocity']:.1f} m/s"
            )

    # Render simple agent UI
    st.divider()
    if "aero_conversation_history" not in st.session_state:
        st.session_state["aero_conversation_history"] = []

    st.markdown(
        f"<h3 style='color:{visuals.TEXT_WHITE}'>AI Aero Expert Agent</h3>",
        unsafe_allow_html=True,
    )

    if st.session_state["aero_conversation_history"]:
        for exchange in st.session_state["aero_conversation_history"]:
            st.markdown(f"**Q:** {exchange['question']}")
            st.markdown(f"**A:** {exchange['answer']}")

    with st.form("aero_agent_form", clear_on_submit=True):
        question = st.text_input(
            "Your question",
            placeholder="e.g. Is my L/D ratio good for a light aircraft?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Ask the Aero Expert")

    if submitted:
        if not question.strip():
            st.error("Please enter a question before submitting.")
        else:
            if not agent.check_ollama_connection():
                st.error("Ollama is not available. Start `ollama serve` and pull a model.")
            else:
                history_text = ""
                for exchange in st.session_state["aero_conversation_history"]:
                    history_text += f"Q: {exchange['question']}\nA: {exchange['answer']}\n\n"
                model_to_use = st.session_state.get("ollama_model_selected", agent.OLLAMA_MODEL)
                try:
                    answer = agent.ask_aero_agent(question.strip(), agent.build_flight_context(
                        rho, velocity, wing_area, lift_coefficient, drag_coefficient, lift_n, drag_n, ld_ratio
                    ), history_text, model=model_to_use)
                    st.session_state["aero_conversation_history"].append({"question": question.strip(), "answer": answer})
                    return
                except Exception as exc:
                    st.error(f"Agent error: {exc}")
