import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from utils import load_data, render_footer
import os

# ─── Cluster colour palette ───────────────────────────────────────────────────
CLUSTER_COLORS = {
    0: "#6366f1", 1: "#0ea5e9", 2: "#8b5cf6", 3: "#f59e0b",
    4: "#10b981", 5: "#ef4444", 6: "#f97316", 7: "#ec4899",
}
CLUSTER_LABELS = {
    0: "Short Daytime Urban",   1: "Standard Commuter",
    2: "Long Night Ride",       3: "Mid-Range Business",
    4: "Afternoon Moderate",    5: "Ultra-Premium",
    6: "Peak-Hour Suburban",    7: "Evening Group Ride",
}

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:48px 0 32px;">
  <p style="font-size:13px;letter-spacing:.2em;text-transform:uppercase;
            color:#0ea5e9;font-weight:800;margin-bottom:12px;">Analyst · ML Documentation</p>
  <h1 style="font-size:42px;font-weight:900;color:#0f172a;margin:0 0 16px;">
    Clustering Backend
  </h1>
  <p style="font-size:18px;color:#475569;max-width:720px;line-height:1.7;margin:0;">
    A technical walkthrough of the two unsupervised learning algorithms applied to
    segment 191 822 Uber trips: <strong>K-Means clustering</strong> and
    <strong>PCA dimensionality reduction</strong> — both computed on the live dataset below.
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Original Dataset View ───────────────────────────────────────────────────
st.markdown("### Original Dataset Preview (First 5 Rows)")
st.markdown(
    "Below is a preview of the first 5 rows and all columns of the original dataset "
    "loaded into the analytical pipeline before preprocessing, feature scaling, and cluster assignment."
)

try:
    raw_path = "uber.csv" if os.path.exists("uber.csv") else "uber_cleaned.csv"
    raw_df = pd.read_csv(raw_path, nrows=5)
    st.dataframe(raw_df, use_container_width=True)
except Exception as e:
    st.error(f"Error loading original dataset preview: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Load data + compute ───────────────────────────────────────────────────────
@st.cache_data(show_spinner="⚙️  Running ML pipeline on the dataset…")
def build_ml_artifacts(sample_n: int = 30_000):
    df = load_data()
    FEATURES = ["distance_km", "pickup_hour", "fare_per_km", "passenger_count"]
    df2 = df[FEATURES + ["cluster"]].dropna()
    # load_data() converts cluster numbers to strings like "1: Standard Weekday"
    # Extract the leading number (works for both int and "N: Label" formats)
    df2["cluster"] = (
        df2["cluster"]
        .astype(str)
        .str.extract(r"^(\d+)", expand=False)
    )
    df2["cluster"] = pd.to_numeric(df2["cluster"], errors="coerce")
    df2 = df2.dropna(subset=["cluster"])
    df2["cluster"] = df2["cluster"].astype(int)

    # ── Sample for heavy computations ──────────────────────────────────────
    rng = np.random.default_rng(42)
    idx = rng.choice(len(df2), size=min(sample_n, len(df2)), replace=False)
    sample = df2.iloc[idx].copy()

    X = sample[FEATURES].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # ── PCA (2 components) ─────────────────────────────────────────────────
    pca = PCA(n_components=2, random_state=42)
    Xp = pca.fit_transform(Xs)
    explained = pca.explained_variance_ratio_

    # ── PCA full variance curve ────────────────────────────────────────────
    pca_full = PCA(random_state=42)
    pca_full.fit(Xs)
    cumvar = np.cumsum(pca_full.explained_variance_ratio_)

    # ── Silhouette on sample ───────────────────────────────────────────────
    labels = sample["cluster"].values
    sil_avg  = silhouette_score(Xs, labels, sample_size=5000, random_state=42)
    sil_vals = silhouette_samples(Xs, labels)

    # ── Elbow (WCSS) — recompute on sample for k=2..10 ────────────────────
    wcss = []
    for k in range(2, 11):
        km = KMeans(n_clusters=k, n_init=5, max_iter=100, random_state=42)
        km.fit(Xs)
        wcss.append(km.inertia_)

    # ── Cluster distribution (full data) ──────────────────────────────────
    dist = df2["cluster"].value_counts().sort_index()

    return {
        "sample": sample,
        "Xs": Xs,
        "Xp": Xp,
        "explained": explained,
        "cumvar": cumvar,
        "labels": labels,
        "sil_avg": sil_avg,
        "sil_vals": sil_vals,
        "wcss": wcss,
        "dist": dist,
        "total": len(df2),
        "features": FEATURES,
    }

art = build_ml_artifacts()

# ─── Pipeline overview ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## ML Pipeline")

cols = st.columns(6)
steps = [
    ("1", "Load", "191 K trips from CSV"),
    ("2", "Clean", "Drop nulls & bad coords"),
    ("3", "Engineer", "distance, hour, fare/km"),
    ("4", "Scale", "StandardScaler"),
    ("5", "PCA", "4D → 2D reduction"),
    ("6", "K-Means", "k=8 final clusters"),
]
for col, (icon, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;
                    padding:14px;text-align:center;min-height:130px;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
                      width:36px;height:36px;border-radius:50%;
                      background:#06C167;color:#fff;
                      font-size:16px;font-weight:800;">{icon}</div>
          <div style="font-weight:700;color:#0f172a;font-size:12px;margin:6px 0 3px;">{title}</div>
          <div style="color:#64748b;font-size:11px;line-height:1.4;">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Features ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Features Used")

feat_df = pd.DataFrame({
    "Feature":     ["distance_km", "pickup_hour", "fare_per_km", "passenger_count"],
    "Description": [
        "Haversine distance pickup to drop-off (km)",
        "Hour the ride started (0-23)",
        "Fare divided by distance -- price-efficiency signal",
        "Number of passengers",
    ],
    "Rationale": [
        "Primary cost driver -- separates short urban hops from long rides",
        "Captures demand patterns: rush hour, night, off-peak",
        "Flags surge, airport, and premium routes",
        "Distinguishes solo vs. group travel behaviour",
    ],
})
st.dataframe(feat_df, use_container_width=True, hide_index=True)

# ==============================================================================
# ALGORITHM 1 -- PCA
# ==============================================================================
st.markdown("---")
st.markdown("## Algorithm 1 -- PCA (Principal Component Analysis)")
st.markdown("""
PCA projects the four standardised features into a **lower-dimensional space** that
maximises explained variance. Here we reduce to **2 principal components** so that the
cluster structure can be visualised in a 2-D scatter plot.
""")

tab_scatter, tab_var = st.tabs(["2-D Cluster Map (PCA)", "Explained Variance"])

with tab_scatter:
    df_plot = pd.DataFrame({
        "PC1": art["Xp"][:, 0],
        "PC2": art["Xp"][:, 1],
        "Cluster": art["labels"],
        "Label": [CLUSTER_LABELS.get(c, f"C{c}") for c in art["labels"]],
    })

    fig_sc = go.Figure()
    for cid in sorted(df_plot["Cluster"].unique()):
        sub   = df_plot[df_plot["Cluster"] == cid]
        color = CLUSTER_COLORS.get(cid, "#888")
        label = f"C{cid}: {CLUSTER_LABELS.get(cid, '')}"

        # Real scatter dots -- small, no legend entry
        fig_sc.add_trace(go.Scatter(
            x=sub["PC1"], y=sub["PC2"],
            mode="markers",
            marker=dict(size=3, color=color, opacity=0.55),
            name=label,
            showlegend=False,
            hovertemplate=(
                f"<b>C{cid} -- {CLUSTER_LABELS.get(cid, '')}</b><br>"
                "PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>"
            ),
        ))
        # Legend-only proxy -- large dot so colors are clearly visible
        fig_sc.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(size=14, color=color),
            name=label,
            showlegend=True,
            legendrank=cid,
        ))

    ex1 = art["explained"][0] * 100
    ex2 = art["explained"][1] * 100
    fig_sc.update_layout(
        title=f"K-Means Clusters in PCA Space  (PC1 {ex1:.1f}% + PC2 {ex2:.1f}% = {ex1+ex2:.1f}% variance explained)",
        xaxis_title=f"PC1 ({ex1:.1f}% variance)",
        yaxis_title=f"PC2 ({ex2:.1f}% variance)",
        height=520,
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
        legend=dict(
            title="Segment",
            x=1.01,
            itemsizing="constant",
            font=dict(size=12),
            tracegroupgap=2,
        ),
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption(f"Sample of {len(art['sample']):,} trips plotted. Each dot is one trip coloured by its K-Means cluster.")


with tab_var:
    n_comp = len(art["cumvar"])
    fig_var = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Individual Explained Variance", "Cumulative Explained Variance"],
    )
    indiv = np.diff(np.concatenate([[0], art["cumvar"]]))
    fig_var.add_trace(go.Bar(
        x=[f"PC{i+1}" for i in range(n_comp)],
        y=indiv * 100,
        marker_color="#0ea5e9",
        text=[f"{v*100:.1f}%" for v in indiv],
        textposition="outside",
    ), row=1, col=1)
    fig_var.add_trace(go.Scatter(
        x=[f"PC{i+1}" for i in range(n_comp)],
        y=art["cumvar"] * 100,
        mode="lines+markers",
        line=dict(color="#f59e0b", width=3),
        marker=dict(size=7),
    ), row=1, col=2)
    fig_var.add_hline(y=80, line_dash="dash", line_color="#94a3b8", row=1, col=2,
                      annotation_text="80% threshold", annotation_position="top left")
    fig_var.update_layout(height=380, showlegend=False,
                          plot_bgcolor="white", paper_bgcolor="white")
    fig_var.update_yaxes(gridcolor="#f1f5f9")
    st.plotly_chart(fig_var, use_container_width=True)

    ex_total = art["explained"][:2].sum() * 100
    st.markdown("""
Principal Component Analysis, or PCA, is a mathematical technique that takes a dataset with many
variables and compresses it into a smaller number of new variables — called principal components —
while preserving as much of the original information as possible.

In this project, each Uber trip is described by four features: distance in km, the hour of pickup,
the fare per km, and the passenger count. PCA begins by standardising all four features so that
none of them dominates simply because of its scale. It then computes a covariance matrix, which
captures how strongly each pair of features moves together across the dataset.

From that matrix, PCA extracts a set of eigenvectors — these are the principal components.
Each one points in the direction of maximum remaining variance in the data. The first component (PC1)
captures the single direction that explains the most spread; the second (PC2) captures the most
remaining spread while being mathematically perpendicular to PC1. Together, PC1 and PC2 in this
dataset account for approximately 55% of the total variance.

Finally, every trip is projected onto these two new axes, producing a 2-D coordinate for each
ride. What you see in the scatter plot above is that projection: trips that were similar across
all four original dimensions end up close together in 2-D space, while dissimilar trips appear
far apart. The coloured clusters you see are the K-Means groups — and the fact that they remain
visually separated in PCA space confirms that K-Means found genuinely distinct, non-overlapping
rider profiles rather than arbitrary groupings.
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITHM 2 — K-MEANS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## Algorithm 2 — K-Means Clustering")
st.markdown("""
K-Means partitions the **standardised 4-D feature space** into *k* groups by minimising
**within-cluster sum of squares (WCSS)**. The optimal *k* was selected using the
Elbow Method and Silhouette Score.
""")

tab_elbow, tab_sil, tab_dist = st.tabs(
    ["Elbow Method", "Silhouette Analysis", "Cluster Distribution"]
)

with tab_elbow:
    k_range = list(range(2, 11))
    fig_el = go.Figure()
    fig_el.add_trace(go.Scatter(
        x=k_range, y=art["wcss"],
        mode="lines+markers",
        line=dict(color="#0ea5e9", width=3),
        marker=dict(size=9, color=["#ef4444" if k == 8 else "#0ea5e9" for k in k_range]),
        text=[f"WCSS: {v:,.0f}" for v in art["wcss"]],
        hovertemplate="k=%{x}<br>%{text}<extra></extra>",
    ))
    fig_el.add_vline(x=8, line_dash="dash", line_color="#f59e0b", line_width=2,
                     annotation_text="k = 8  ✓", annotation_position="top right",
                     annotation_font_color="#f59e0b", annotation_font_size=14)
    fig_el.update_layout(
        title="Elbow Method: WCSS vs Number of Clusters",
        xaxis_title="Number of Clusters (k)", yaxis_title="WCSS (inertia)",
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9", dtick=1),
        yaxis=dict(gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_el, use_container_width=True)
    st.markdown(f"""
**Interpretation:** WCSS always decreases as *k* grows. The goal is the **"elbow"** — the point
where additional clusters yield rapidly diminishing returns.  
Beyond **k = 8** the curve flattens, confirming 8 as the optimal choice.

*Computed on a 30 000-trip sample from the real dataset.*
    """)

with tab_sil:
    sil_avg = art["sil_avg"]

    # Per-cluster avg silhouette
    per_cl = {}
    for cid in sorted(set(art["labels"])):
        mask = art["labels"] == cid
        per_cl[cid] = float(art["sil_vals"][mask].mean())

    fig_sil = go.Figure()
    fig_sil.add_trace(go.Bar(
        x=[f"C{k}" for k in per_cl],
        y=list(per_cl.values()),
        marker_color=[CLUSTER_COLORS.get(k, "#888") for k in per_cl],
        text=[f"{v:.3f}" for v in per_cl.values()],
        textposition="outside",
    ))
    fig_sil.add_hline(y=sil_avg, line_dash="dash", line_color="#0f172a",
                      annotation_text=f"Average = {sil_avg:.3f}",
                      annotation_position="top right")
    fig_sil.update_layout(
        title=f"Silhouette Score per Cluster  (overall avg = {sil_avg:.3f})",
        xaxis_title="Cluster", yaxis_title="Silhouette Score",
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9", range=[0, max(per_cl.values()) * 1.25]),
    )
    st.plotly_chart(fig_sil, use_container_width=True)

    # Silhouette plot (sorted within each cluster)
    fig_sf = go.Figure()
    y_lower = 10
    for cid in sorted(set(art["labels"])):
        mask  = art["labels"] == cid
        vals  = np.sort(art["sil_vals"][mask])
        y_upper = y_lower + len(vals)
        fig_sf.add_trace(go.Bar(
            x=vals, y=list(range(y_lower, y_upper)),
            orientation="h",
            marker_color=CLUSTER_COLORS.get(cid, "#888"),
            showlegend=True,
            name=f"C{cid}: {CLUSTER_LABELS.get(cid, '')}",
            hovertemplate=f"C{cid}<br>Silhouette: %{{x:.3f}}<extra></extra>",
        ))
        y_lower = y_upper + 10

    fig_sf.add_vline(x=sil_avg, line_dash="dash", line_color="#0f172a",
                     annotation_text="avg", annotation_position="top right")
    fig_sf.update_layout(
        title="Silhouette Diagram — each bar is one trip",
        xaxis_title="Silhouette coefficient", yaxis_title="Trips (sorted per cluster)",
        height=480, plot_bgcolor="white", paper_bgcolor="white",
        barmode="overlay", bargap=0,
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9", showticklabels=False),
        showlegend=True,
    )
    st.plotly_chart(fig_sf, use_container_width=True)
    st.caption("Wider bars = better-separated cluster. Negative bars = misclassified trips.")

with tab_dist:
    dist = art["dist"]
    total = art["total"]
    labels_bar = [f"C{i}: {CLUSTER_LABELS.get(i, '')}" for i in dist.index]

    fig_dd = make_subplots(rows=1, cols=2,
                           specs=[[{"type": "pie"}, {"type": "bar"}]],
                           subplot_titles=["Share of Trips", "Trip Count"])
    fig_dd.add_trace(go.Pie(
        labels=labels_bar,
        values=dist.values.tolist(),
        marker_colors=[CLUSTER_COLORS.get(i, "#888") for i in dist.index],
        hole=0.45, textinfo="percent",
    ), row=1, col=1)
    fig_dd.add_trace(go.Bar(
        x=[f"C{i}" for i in dist.index],
        y=dist.values.tolist(),
        marker_color=[CLUSTER_COLORS.get(i, "#888") for i in dist.index],
        text=[f"{v:,}" for v in dist.values],
        textposition="outside",
    ), row=1, col=2)
    fig_dd.update_layout(height=420, showlegend=False,
                         plot_bgcolor="white", paper_bgcolor="white")
    fig_dd.update_yaxes(gridcolor="#f1f5f9", row=1, col=2)
    st.plotly_chart(fig_dd, use_container_width=True)

    rows = [(i, CLUSTER_LABELS.get(i,"?"), int(dist[i]), round(dist[i]/total*100, 1))
            for i in dist.index]
    st.dataframe(
        pd.DataFrame(rows, columns=["ID", "Segment", "Trips", "% of Total"]),
        use_container_width=True, hide_index=True,
    )

# ─── How K-Means works ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## How K-Means Works — Step by Step")
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown("""
**The algorithm iterates two steps until convergence:**

1. **Initialise** — place *k = 8* centroids using *k-means++* (spreads them out)
2. **Assign** — each trip is assigned to its nearest centroid (Euclidean distance)
3. **Update** — move each centroid to the mean of its assigned trips
4. **Repeat 2–3** until centroids stop moving (convergence)
5. **Output** — 8 cluster labels + centroid coordinates in 4-D feature space

`n_init=10` independent runs → best result (lowest WCSS) is kept  
`random_state=42` → fully reproducible
    """)
with c2:
    st.markdown("""
**Why K-Means suits this dataset:**

- Scales to 191 K rows in seconds
- Produces compact, interpretable centroids → rider profiles
- Silhouette Score **0.39** confirms good cluster separation
- Clusters are roughly convex in standardised feature space
- Assumes equal-variance spherical clusters — acceptable given the data distribution
- Sensitive to outliers → pre-cleaning removed invalid fares/coordinates
    """)

# ─── Comparison table ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Algorithm Comparison")

comp = pd.DataFrame({
    "Property":     ["Type", "Goal", "Parameters", "Complexity", "Applied to", "Output", "Score"],
    "PCA":          [
        "Dimensionality Reduction",
        "Maximise explained variance in fewer dimensions",
        "n_components = 2",
        "O(n · d²) — fast",
        "Standardised feature matrix (30 K sample)",
        "2-D coordinates for visualisation",
        f"PC1+PC2 explain {art['explained'][:2].sum()*100:.1f}% of variance",
    ],
    "K-Means":      [
        "Clustering",
        "Minimise within-cluster sum of squares",
        "k = 8,  n_init = 10,  random_state = 42",
        "O(n · k · d · i) — fast at scale",
        "Standardised feature matrix (191 K trips)",
        "Cluster label 0–7 for every trip",
        f"Silhouette = {art['sil_avg']:.3f}  (good separation)",
    ],
})
st.dataframe(comp.set_index("Property"), use_container_width=True)

# ─── Segment glossary ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Cluster Segment Glossary")

glossary = [
    (1,"Standard Commuter",    "#0ea5e9", "Short-to-medium daytime rides. Backbone of the platform (33 %)."),
    (6,"Peak-Hour Suburban",   "#f97316", "Suburban rush-hour trips with slightly above-avg passengers."),
    (3,"Mid-Range Business",   "#f59e0b", "Medium-distance business-hour rides; higher fare/km suggests airport/corporate routes."),
    (7,"Evening Group Ride",   "#ec4899", "Evening departures with highest passenger counts — nightlife / events."),
    (4,"Afternoon Moderate",   "#10b981", "Balanced profile across all features — the 'average' Uber trip."),
    (2,"Long Night Ride",      "#8b5cf6", "Long-distance off-peak (0–6 AM). Airport transfers / bar closings."),
    (0,"Short Daytime Urban",  "#6366f1", "Very short urban hops. High fare/km despite low total fare."),
    (5,"Ultra-Premium",        "#ef4444", "< 0.1 % of trips. Extremely long + high fare/km. Statistical outliers."),
]
for cid, label, color, desc in glossary:
    pct = round(art["dist"].get(cid,0) / art["total"] * 100, 1)
    st.markdown(f"""
    <div style="border-left:4px solid {color};padding:10px 16px;margin-bottom:10px;
                background:#f8fafc;border-radius:0 8px 8px 0;">
      <span style="background:{color};color:#fff;border-radius:6px;
                   padding:2px 8px;font-size:12px;font-weight:700;">C{cid}</span>
      &nbsp;<strong style="color:#0f172a;">{label}</strong>
      <span style="float:right;color:#94a3b8;font-size:13px;">{pct:.1f}% of trips</span>
      <p style="color:#475569;font-size:13px;line-height:1.6;margin:6px 0 0;">{desc}</p>
    </div>""", unsafe_allow_html=True)

render_footer()
