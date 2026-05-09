import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

METRIC_LABELS: dict[str, str] = {
    "mood_score": "Ánimo",
    "energy_score": "Energía",
    "stress_score": "Estrés",
    "meaningfulness_level": "Significado",
}

METRIC_COLORS: dict[str, str] = {
    "mood_score": "#4CAF50",
    "energy_score": "#2196F3",
    "stress_score": "#F44336",
    "meaningfulness_level": "#9C27B0",
}

_CATEGORY_COLORS = px.colors.qualitative.Set2


def timeline_chart(df: pd.DataFrame, metrics: list[str]) -> go.Figure:
    fig = go.Figure()
    for metric in metrics:
        if metric not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df["checkin_date"],
            y=df[metric],
            mode="lines+markers",
            name=METRIC_LABELS.get(metric, metric),
            line=dict(color=METRIC_COLORS.get(metric, "#888"), width=2),
            marker=dict(size=7),
        ))
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Puntuación",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
        height=380,
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def activity_frequency_chart(df: pd.DataFrame) -> go.Figure:
    plot_df = df.sort_values("times_done", ascending=True).tail(15)
    fig = px.bar(
        plot_df,
        x="times_done",
        y="activity_name",
        orientation="h",
        color="activity_category",
        text="times_done",
        labels={
            "times_done": "Veces realizadas",
            "activity_name": "",
            "activity_category": "Categoría",
        },
        color_discrete_sequence=_CATEGORY_COLORS,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        margin=dict(l=0, r=40, t=10, b=0),
        height=max(250, len(plot_df) * 38 + 60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig


def activity_metric_chart(df: pd.DataFrame, metric: str) -> go.Figure:
    col_map = {
        "mood_score": "avg_mood",
        "stress_score": "avg_stress",
        "meaningfulness_level": "avg_meaningfulness",
    }
    col = col_map.get(metric)
    label = METRIC_LABELS.get(metric, metric)

    if col is None or col not in df.columns or df.empty:
        return go.Figure()

    plot_df = df.sort_values(col, ascending=True)
    fig = px.bar(
        plot_df,
        x=col,
        y="activity_name",
        orientation="h",
        color="activity_category",
        text=col,
        labels={
            col: f"Promedio {label}",
            "activity_name": "",
            "activity_category": "Categoría",
        },
        color_discrete_sequence=_CATEGORY_COLORS,
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        margin=dict(l=0, r=40, t=10, b=0),
        height=max(250, len(plot_df) * 38 + 60),
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig
