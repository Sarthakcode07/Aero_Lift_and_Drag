import matplotlib.pyplot as plt
from typing import Tuple

# Visual constants
BG_MAIN = "#0a0e17"
BG_SIDEBAR = "#0f1623"
BG_CARD_GRADIENT = (
    "linear-gradient(155deg, #3d4f66 0%, #4d6178 48%, #42566c 100%)"
)
BG_CARD_BORDER = "#6b7f96"
TEXT_WHITE = "#ffffff"
TEXT_PRIMARY = TEXT_WHITE
TEXT_MUTED = TEXT_WHITE
TEXT_DIM = TEXT_WHITE
TEXT_ON_CARD_LABEL = TEXT_WHITE
TEXT_ON_CARD_VALUE = TEXT_WHITE
ACCENT_SKY = "#38bdf8"
ACCENT_CYAN = "#22d3ee"
ACCENT_AMBER = "#f59e0b"
ACCENT_WARNING = "#ef4444"
PLOT_LIFT = "#38bdf8"
PLOT_DRAG = "#22d3ee"
PLOT_MARKER = "#f59e0b"
PLOT_BG = "#0f172a"
PLOT_PANEL = "#151d2e"
FONT_STACK = "'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif"


# Plot helpers

def _style_axes(ax: plt.Axes, title: str, xlabel: str, ylabel: str):
    ax.set_xlabel(xlabel, color=TEXT_WHITE, fontsize=10, labelpad=8)
    ax.set_ylabel(ylabel, color=TEXT_WHITE, fontsize=10, labelpad=8)
    ax.set_title(title, color=TEXT_WHITE, fontsize=12, fontweight=600, pad=12)
    ax.tick_params(colors=TEXT_WHITE, labelsize=9)
    ax.grid(True, linestyle="--", alpha=0.35, color=BG_CARD_BORDER)
    legend = ax.legend(
        loc="upper left",
        framealpha=0.95,
        facecolor=PLOT_PANEL,
        edgecolor=BG_CARD_BORDER,
        labelcolor=TEXT_WHITE,
        fontsize=9,
    )
    for spine in ax.spines.values():
        spine.set_color(BG_CARD_BORDER)
    return legend


def _new_figure() -> Tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(PLOT_PANEL)
    ax.set_facecolor(PLOT_BG)
    return fig, ax


# Plots

def build_lift_plot(
    rho: float,
    wing_area: float,
    lift_coefficient: float,
    current_velocity: float,
    current_lift_n: float,
):
    import numpy as np

    velocities = np.linspace(0.0, 300.0, 300)
    lift_curve = 0.5 * rho * velocities**2 * wing_area * lift_coefficient

    fig, ax = _new_figure()
    ax.plot(velocities, lift_curve, color=PLOT_LIFT, linewidth=2, label="Lift (L)")
    ax.scatter(
        [current_velocity],
        [current_lift_n],
        color=PLOT_MARKER,
        s=80,
        zorder=5,
        edgecolors=TEXT_PRIMARY,
        linewidths=1,
        label=f"Current v = {current_velocity:.0f} m/s",
    )
    _style_axes(ax, "Lift vs Velocity", "Velocity (m/s)", "Lift (N)")
    ax.set_xlim(0, 300)
    fig.tight_layout()
    return fig


def build_lift_vs_drag_plot(
    rho: float,
    wing_area: float,
    lift_coefficient: float,
    drag_coefficient: float,
    current_velocity: float,
    current_lift_n: float,
    current_drag_n: float,
):
    import numpy as np

    velocities = np.linspace(0.0, 300.0, 300)
    dynamic = 0.5 * rho * velocities**2 * wing_area
    lift_curve = dynamic * lift_coefficient
    drag_curve = dynamic * drag_coefficient

    fig, ax = _new_figure()
    scatter = ax.scatter(
        drag_curve,
        lift_curve,
        c=velocities,
        cmap="cividis",
        s=10,
        alpha=0.9,
        label="v = 0 → 300 m/s",
    )
    ax.plot(drag_curve, lift_curve, color=PLOT_DRAG, linewidth=1.25, alpha=0.6)
    ax.scatter(
        [current_drag_n],
        [current_lift_n],
        color=PLOT_MARKER,
        s=90,
        zorder=5,
        edgecolors=TEXT_PRIMARY,
        linewidths=1,
        label=f"Current v = {current_velocity:.0f} m/s",
    )
    _style_axes(ax, "Lift vs Drag (Drag Polar)", "Drag (N)", "Lift (N)")
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Velocity (m/s)", color=TEXT_WHITE, fontsize=9)
    cbar.ax.yaxis.set_tick_params(color=TEXT_WHITE, labelsize=8)
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=TEXT_WHITE)
    cbar.outline.set_edgecolor(BG_CARD_BORDER)
    fig.tight_layout()
    return fig


# UI helpers (markup)

def metric_card(
    title: str,
    value: str,
    unit: str,
    value_color: str,
    border_accent: str,
) -> str:
    return f"""
    <div style="
        font-family: {FONT_STACK};
        background: {BG_CARD_GRADIENT};
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        border: 1px solid {BG_CARD_BORDER};
        border-left: 4px solid {border_accent};
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    ">
        <p style="
            margin: 0 0 0.5rem 0;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {TEXT_ON_CARD_LABEL};
        ">{title}</p>
        <p style="
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
            color: {value_color};
            letter-spacing: -0.02em;
        ">{value} <span style="font-size: 0.9rem; font-weight: 500; color: {TEXT_ON_CARD_LABEL};">{unit}</span></p>
    </div>
    """


def settings_card(
    rho: float,
    velocity: float,
    wing_area: float,
    lift_coefficient: float,
    drag_coefficient: float,
    ld_ratio: float,
    empty_weight_kg: float | None = None,
) -> str:
    def row(label: str, val: str) -> str:
        return (
            f'<tr><td style="padding: 0.45rem 0; color: {TEXT_ON_CARD_LABEL}; font-size: 0.875rem;">'
            f"{label}</td>"
            f'<td style="text-align: right; font-weight: 600; color: {TEXT_ON_CARD_VALUE}; '
            f'font-size: 0.875rem;">{val}</td></tr>'
        )

    items = [
        ("Air density ρ", f"{rho:.3f} kg/m³"),
        ("Velocity", f"{velocity:.1f} m/s"),
        ("Wing area", f"{wing_area:.2f} m²"),
        ("Cl / Cd", f"{lift_coefficient:.3f} / {drag_coefficient:.3f}"),
        ("L/D ratio", f"{ld_ratio:.2f}"),
    ]
    if empty_weight_kg is not None:
        items.insert(2, ("Empty weight", f"{empty_weight_kg:,.0f} kg"))

    rows = "".join(row(l, v) for l, v in items)
    return f"""
    <div style="
        font-family: {FONT_STACK};
        background: {BG_CARD_GRADIENT};
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        border: 1px solid {BG_CARD_BORDER};
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    ">
        <p style="
            margin: 0 0 0.75rem 0;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {TEXT_ON_CARD_LABEL};
        ">Flight parameters</p>
        <table style="width: 100%; border-collapse: collapse;">{rows}</table>
    </div>
    """


def section_heading(text: str) -> str:
    return f"""
    <p style="
        font-family: {FONT_STACK};
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {TEXT_WHITE};
        margin: 0 0 0.5rem 0;
    ">{text}</p>
    """


def simulate_takeoff(
    rho: float,
    wing_area: float,
    lift_coefficient: float,
    drag_coefficient: float,
    total_weight_kg: float,
    runway_length_m: float,
    thrust_n: float,
    rolling_friction_coeff: float = 0.02,
    dt: float = 0.1,
    max_time: float = 120.0,
):
    """Simulate a ground-roll takeoff.

    Returns a dict containing time-series arrays and an outcome summary.

    Physics (simplified):
    - dynamic pressure q = 0.5 * rho * v^2
    - lift = q * S * Cl
    - drag = q * S * Cd
    - rolling friction = mu * mass * g
    - net_force = thrust - drag - rolling_friction
    - accel = net_force / mass

    The simulation advances in steps of `dt` seconds until either lift >= weight (lift-off)
    or the aircraft reaches the end of the runway or max_time.
    """
    import math

    g = 9.81
    mass = float(total_weight_kg)

    times = []
    positions = []
    velocities = []
    lifts = []
    drags = []

    s = 0.0
    v = 0.0
    t = 0.0

    lift_off = False
    lift_off_time = None
    lift_off_distance = None

    max_steps = int(max_time / dt)
    for step in range(max_steps):
        q = 0.5 * rho * v * v
        lift = q * wing_area * lift_coefficient
        drag = q * wing_area * drag_coefficient
        rolling = rolling_friction_coeff * mass * g

        net_force = thrust_n - drag - rolling
        accel = net_force / mass
        # Prevent negative velocities dropping below 0
        v = max(0.0, v + accel * dt)
        s = s + v * dt
        t = t + dt

        times.append(t)
        positions.append(s)
        velocities.append(v)
        lifts.append(lift)
        drags.append(drag)

        if not lift_off and lift >= mass * g:
            lift_off = True
            lift_off_time = t
            lift_off_distance = s
            break

        if s >= runway_length_m:
            # ran out of runway before lift
            break

    outcome = {
        "lift_off": lift_off,
        "lift_off_time": lift_off_time,
        "lift_off_distance": lift_off_distance,
        "final_time": t,
        "final_distance": s,
        "final_velocity": v,
    }

    return {
        "times": times,
        "positions": positions,
        "velocities": velocities,
        "lifts": lifts,
        "drags": drags,
        "outcome": outcome,
    }
