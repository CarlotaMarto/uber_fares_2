import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return R * c


@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path, low_memory=False)
    df = df.loc[:, ~df.columns.str.match('^Unnamed')]
    df.columns = [c.strip() for c in df.columns]
    for col in ["pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "pickup_datetime" in df.columns:
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    if {"pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude"}.issubset(df.columns):
        df["distance_km"] = haversine_km(df["pickup_latitude"], df["pickup_longitude"], df["dropoff_latitude"], df["dropoff_longitude"])
    else:
        for alt in ["distance", "trip_distance", "Distance"]:
            if alt in df.columns:
                df["distance_km"] = pd.to_numeric(df[alt], errors="coerce")
                break
    if "fare_amount" in df.columns:
        df["fare"] = pd.to_numeric(df["fare_amount"], errors="coerce")
    elif "Fare" in df.columns:
        df["fare"] = pd.to_numeric(df["Fare"], errors="coerce")
    else:
        numeric = df.select_dtypes("number")
        if not numeric.empty:
            df["fare"] = numeric.iloc[:, 0]
        else:
            df["fare"] = pd.NA
    df = df.loc[df["fare"].notna() & df["distance_km"].notna()].copy()
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data
def run_clustering(df: pd.DataFrame, n_clusters: int):
    X = df[["fare", "distance_km"]].to_numpy()
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(Xs)
    return labels, kmeans, scaler


def main():
    st.set_page_config(page_title="Uber Clusters", layout="wide")
    # Branding / header
    st.sidebar.header("Branding")
    logo_file = st.sidebar.file_uploader("Upload a logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    logo_url = st.sidebar.text_input("Or logo URL (optional)", value="")
    palette_choice = st.sidebar.selectbox("Color palette", options=["Uber-inspired", "Default"], index=0)

    cols_h = st.columns([0.15, 0.85])
    with cols_h[0]:
        if logo_file is not None:
            st.image(logo_file, width=100)
        else:
            local_logo = "assets/uber_logo.png"
            try:
                with open(local_logo, "rb") as f:
                    st.image(f.read(), width=100)
            except Exception:
                st.markdown("<div style='font-size:32px'>🚕</div>", unsafe_allow_html=True)
    with cols_h[1]:
        st.markdown("<div style='font-size:28px; font-weight:600; color:#111'>Uber fares clustering viewer</div>", unsafe_allow_html=True)

    csv_path = st.sidebar.text_input("CSV path", value="uber.csv")
    n_clusters = st.sidebar.slider("Number of clusters", 2, 10, 4)
    sample_size = st.sidebar.number_input("Max rows to show/plot", value=5000, min_value=100, max_value=50000, step=100)

    try:
        df = load_data(csv_path)
    except FileNotFoundError:
        st.error(f"CSV not found: {csv_path}")
        return
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return

    if df.empty:
        st.warning("No usable rows found (need numeric fare and distance)")
        return

    labels, kmeans, scaler = run_clustering(df, int(n_clusters))
    df["cluster"] = labels.astype(int)

    st.subheader("Data sample with cluster assignments")
    cols = [c for c in ["fare", "distance_km", "passenger_count", "pickup_datetime"] if c in df.columns]
    cols += ["cluster"]
    st.dataframe(df[cols].head(int(sample_size)))

    st.subheader("Fare vs Distance (clusters)")
    plot_df = df.sample(n=min(len(df), int(sample_size)), random_state=1)

    # Color palettes
    uber_palette = [
        "#000000",
        "#111111",
        "#444444",
        "#06A77D",
        "#00C2A8",
        "#FFB300",
        "#E4002B",
        "#6A1B9A",
        "#FF7A00",
        "#00AEEF",
    ]
    default_palette = px.colors.qualitative.Safe
    color_seq = uber_palette if palette_choice == "Uber-inspired" else default_palette

    fig = px.scatter(
        plot_df,
        x="fare",
        y="distance_km",
        color=plot_df["cluster"].astype(str),
        color_discrete_sequence=color_seq,
        hover_data=[c for c in ["pickup_datetime", "passenger_count"] if c in plot_df.columns],
        labels={"fare": "Fare (USD)", "distance_km": "Distance (km)"},
        title=f"Fare vs Distance colored by {n_clusters} clusters",
    )
    fig.update_traces(marker=dict(opacity=0.85, size=7))
    st.plotly_chart(fig, use_container_width=True)

    if st.checkbox("Show cluster centers (approx.)"):
        centers_scaled = kmeans.cluster_centers_
        centers = scaler.inverse_transform(centers_scaled)
        centers_df = pd.DataFrame(centers, columns=["fare", "distance_km"])
        centers_df["cluster"] = centers_df.index
        st.table(centers_df)


if __name__ == "__main__":
    main()
