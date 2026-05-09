from datetime import date, timedelta

import pandas as pd
import streamlit as st

from charts import activity_frequency_chart, activity_metric_chart, timeline_chart
from data_loader import (
    db_exists,
    get_activity_names,
    load_checkins_with_activities,
    load_detailed_activity_data,
)
from filters import apply_activity_filter, apply_date_filter, apply_meaningfulness_filter

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tracker Diario",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guard: DB must exist ─────────────────────────────────────────────────────

if not db_exists():
    st.title("📊 Tracker Diario")
    st.error(
        "No se encontró `tracker.db`. Créala primero:\n\n"
        "```bash\n"
        "sqlite3 tracker.db < database/schema.sql\n"
        "sqlite3 tracker.db < database/seed.sql\n"
        "```"
    )
    st.stop()

# ── Data loading (cached 30 s) ───────────────────────────────────────────────

@st.cache_data(ttl=30)
def _load_all() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    return (
        load_checkins_with_activities(),
        load_detailed_activity_data(),
        get_activity_names(),
    )


checkins_df, activity_raw_df, activity_names = _load_all()

# ── Constants ────────────────────────────────────────────────────────────────

MEANING_MAP = {1: "Poco", 2: "Normal", 3: "Mucho"}
METRIC_DISPLAY = {
    "mood_score": "Ánimo",
    "energy_score": "Energía",
    "stress_score": "Estrés",
    "meaningfulness_level": "Significado (1–3)",
}

# ── Helper ───────────────────────────────────────────────────────────────────

def _compute_activity_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    result = (
        df.groupby(["activity_name", "activity_category"])
        .agg(
            times_done=("activity_name", "count"),
            avg_mood=("mood_score", "mean"),
            avg_stress=("stress_score", "mean"),
            avg_meaningfulness=("meaningfulness_level", "mean"),
        )
        .reset_index()
        .sort_values("times_done", ascending=False)
    )
    result["avg_mood"] = result["avg_mood"].round(1)
    result["avg_stress"] = result["avg_stress"].round(1)
    result["avg_meaningfulness"] = result["avg_meaningfulness"].round(2)
    return result

# ── Sidebar filters ──────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Filtros")

    if not checkins_df.empty:
        min_date = checkins_df["checkin_date"].dt.date.min()
        max_date = checkins_df["checkin_date"].dt.date.max()
    else:
        min_date = date.today() - timedelta(days=30)
        max_date = date.today()

    date_input = st.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_input, (list, tuple)):
        if len(date_input) == 2:
            start_date, end_date = date_input
        else:
            start_date = end_date = date_input[0]
    else:
        start_date = end_date = date_input

    selected_meanings = st.multiselect(
        "Significado del día",
        options=[1, 2, 3],
        default=[1, 2, 3],
        format_func=lambda x: MEANING_MAP[x],
    )
    active_meanings = selected_meanings or [1, 2, 3]

    activity_filter = st.selectbox(
        "Actividad",
        options=["Todas"] + activity_names,
    )
    selected_activity = "" if activity_filter == "Todas" else activity_filter

    st.divider()
    st.caption(
        "Los filtros de fecha, significado y actividad se aplican al "
        "resumen, timeline y tabla.\n\n"
        "Fecha y significado también aplican a las estadísticas de actividades."
    )
    st.caption("Los datos se actualizan cada 30 s.")

# ── Apply filters ─────────────────────────────────────────────────────────────

# All three filters → checkins (summary, timeline, table)
filtered_df = apply_date_filter(checkins_df, start_date, end_date)
filtered_df = apply_meaningfulness_filter(filtered_df, active_meanings)
filtered_df = apply_activity_filter(filtered_df, selected_activity)

# Date + meaningfulness only → activity data (activity stats section)
filtered_activity_raw = apply_date_filter(activity_raw_df, start_date, end_date)
filtered_activity_raw = apply_meaningfulness_filter(filtered_activity_raw, active_meanings)
activity_stats = _compute_activity_stats(filtered_activity_raw)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Tracker Diario")
n = len(filtered_df)
if n > 0:
    st.caption(
        f"{n} check-in{'s' if n != 1 else ''} · "
        f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"
    )
st.divider()

# ── Sección 1: Resumen general ───────────────────────────────────────────────

st.subheader("Resumen general")

if filtered_df.empty:
    st.info("No hay check-ins para los filtros seleccionados.")
else:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Check-ins", n)
    c2.metric("Ánimo promedio",      f"{filtered_df['mood_score'].mean():.1f} / 10")
    c3.metric("Energía promedio",    f"{filtered_df['energy_score'].mean():.1f} / 10")
    c4.metric("Estrés promedio",     f"{filtered_df['stress_score'].mean():.1f} / 10")
    c5.metric("Significado promedio",f"{filtered_df['meaningfulness_level'].mean():.1f} / 3")

st.divider()

# ── Sección 2: Timeline ───────────────────────────────────────────────────────

st.subheader("Timeline")

if filtered_df.empty:
    st.info("No hay check-ins para los filtros seleccionados.")
else:
    selected_metrics = st.multiselect(
        "Métricas",
        options=list(METRIC_DISPLAY.keys()),
        default=["mood_score", "energy_score", "stress_score"],
        format_func=lambda m: METRIC_DISPLAY[m],
        key="timeline_metrics",
    )
    if not selected_metrics:
        st.info("Selecciona al menos una métrica para ver la gráfica.")
    else:
        st.plotly_chart(
            timeline_chart(filtered_df, selected_metrics),
            use_container_width=True,
        )
        if "meaningfulness_level" in selected_metrics:
            st.caption("Nota: Significado usa escala 1–3; el resto usa 1–10.")

st.divider()

# ── Sección 3: Actividades ────────────────────────────────────────────────────

st.subheader("Actividades")

if activity_stats.empty:
    st.info("No hay actividades registradas para el período seleccionado.")
else:
    tab_freq, tab_mood, tab_stress, tab_meaning = st.tabs(
        ["📊 Frecuencia", "😊 Ánimo promedio", "😰 Estrés promedio", "✨ Significado promedio"]
    )
    with tab_freq:
        st.plotly_chart(activity_frequency_chart(activity_stats), use_container_width=True)
    with tab_mood:
        st.plotly_chart(activity_metric_chart(activity_stats, "mood_score"), use_container_width=True)
    with tab_stress:
        st.plotly_chart(activity_metric_chart(activity_stats, "stress_score"), use_container_width=True)
    with tab_meaning:
        st.plotly_chart(activity_metric_chart(activity_stats, "meaningfulness_level"), use_container_width=True)

st.divider()

# ── Sección 4: Tabla detallada ────────────────────────────────────────────────

st.subheader("Tabla detallada")

if filtered_df.empty:
    st.info("No hay check-ins para los filtros seleccionados.")
else:
    display_df = (
        filtered_df
        .copy()
        .sort_values("checkin_date", ascending=False)
    )
    display_df["checkin_date"] = display_df["checkin_date"].dt.strftime("%Y-%m-%d")
    display_df["meaningfulness_level"] = display_df["meaningfulness_level"].map(MEANING_MAP)
    display_df = display_df.fillna("—")
    display_df = display_df.rename(columns={
        "checkin_date":        "Fecha",
        "mood_score":          "Ánimo",
        "energy_score":        "Energía",
        "stress_score":        "Estrés",
        "meaningfulness_level":"Significado",
        "activities":          "Actividades",
        "best_part_of_day":    "Lo mejor del día",
        "energy_drainer":      "Qué te drenó",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)
