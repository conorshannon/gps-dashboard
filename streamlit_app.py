import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GPS Dashboard", layout="wide")
st.title("📊 Live GPS Dashboard (STATSports data)")

uploaded = st.file_uploader("Upload a STATSports / Sonra CSV", type=["csv"])

def find_col(df, candidates):
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    # fuzzy: try contains
    lc = {c.lower(): c for c in df.columns}
    for cand in candidates:
        for k in lc:
            if cand.lower() in k:
                return lc[k]
    return None

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = [c.strip() for c in df.columns]

    with st.expander("Raw data preview"):
        st.dataframe(df.head(50))

    # Try to map common Sonra column names (edit these if your export uses different labels)
    player_col = find_col(df, ["Player", "Athlete", "Name"])
    td_col     = find_col(df, ["Total Distance", "TotalDistance", "Distance (m)", "Distance_m"])
    hsr_col    = find_col(df, ["High Speed Running", "HSR (m)", "HSR", "High-Speed Running"])
    sprint_col = find_col(df, ["Sprint Count", "Sprints"])
    vmax_col   = find_col(df, ["Max Speed", "MaxSpeed", "Vmax (km/h)"])
    load_col   = find_col(df, ["Player Load", "Load", "PlayerLoad"])

    # Metrics
    st.subheader("📌 Key metrics")
    mcols = st.columns(5)
    if td_col and td_col in df:
        mcols[0].metric("Total Distance (m)", f"{df[td_col].sum():,.0f}")
    if hsr_col and hsr_col in df:
        mcols[1].metric("HSR (m)", f"{df[hsr_col].sum():,.0f}")
    if sprint_col and sprint_col in df:
        mcols[2].metric("Sprints", f"{int(df[sprint_col].sum())}")
    if vmax_col and vmax_col in df:
        try:
            mcols[3].metric("Max Speed (km/h)", f"{df[vmax_col].max():.1f}")
        except Exception:
            mcols[3].metric("Max Speed", f"{df[vmax_col].max()}")
    if load_col and load_col in df:
        mcols[4].metric("Player Load", f"{df[load_col].sum():.1f}")

    # Per-player breakdowns
    if player_col:
        st.subheader("Per-player summaries")
        # Choose which metric to compare
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        default_metric = td_col if td_col else (hsr_col if hsr_col else (load_col if load_col else (numeric_cols[0] if numeric_cols else None)))
        metric = st.selectbox("Choose a metric to compare:", options=numeric_cols, index=(numeric_cols.index(default_metric) if default_metric in numeric_cols else 0) if numeric_cols else 0)
        if metric:
            agg = df.groupby(player_col, dropna=False)[metric].sum().reset_index()
            fig = px.bar(agg, x=player_col, y=metric, title=f"{metric} by player")
            st.plotly_chart(fig, use_container_width=True)

        # Optional: second chart for HSR or distance if available
        if hsr_col and hsr_col in df.columns:
            agg_hsr = df.groupby(player_col, dropna=False)[hsr_col].sum().reset_index()
            fig2 = px.bar(agg_hsr, x=player_col, y=hsr_col, title=f"{hsr_col} by player")
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No Player column found. You can still explore numeric columns below.")

    # Quick describe of main numeric columns
    st.subheader("Quick stats")
    st.dataframe(df.select_dtypes(include=["number"]).describe().T)

else:
    st.info("👆 Upload a CSV exported from STATSports / Sonra to begin.")
