import os
import pandas as pd
import numpy as np
from fpdf import FPDF

# ── Color Palette Constants ──────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UBER_GREEN = (6, 193, 103)
TILE_BORDER = (226, 232, 240)
TEXT_DARK = (15, 23, 42)
TEXT_MUTED = (148, 163, 184)
TEXT_BODY = (71, 85, 105)
GREEN_MUTED = (6, 150, 80)

# ── Static/Computed Metrics ──────────────────────────────────────────
INSIGHTS = {
    "total_trips": 191822,
    "avg_fare": 11.36,
    "avg_distance_km": 3.4,
    "peak_hour": 18,
    "micro_trip_pct": 82.2
}

# Demand volume per hour for NYC Uber fares
HOURLY = [
    5420, 4810, 4120, 3210, 2430, 2810, 4920, 7810, 10420, 11050,
    9810, 10230, 11420, 10980, 11120, 11840, 12940, 14210, 15980,
    14810, 12940, 10810, 8940, 7120
]

CLUSTERS = [
    ("Standard Commuter", 33.0),
    ("Peak-Hour Suburban", 18.2),
    ("Afternoon Moderate", 15.4),
    ("Short Daytime Urban", 12.1),
    ("Mid-Range Business", 10.3),
    ("Evening Group Ride", 8.9),
    ("Long Night Ride", 2.0),
    ("Ultra-Premium", 0.1),
]

CLUSTER_COLORS = {
    "Standard Commuter": (14, 165, 233),
    "Peak-Hour Suburban": (249, 115, 22),
    "Afternoon Moderate": (16, 185, 129),
    "Short Daytime Urban": (99, 102, 241),
    "Mid-Range Business": (245, 158, 11),
    "Evening Group Ride": (236, 72, 153),
    "Long Night Ride": (139, 92, 246),
    "Ultra-Premium": (239, 68, 68),
}

# ── Helper FPDF Drawing Functions ────────────────────────────────────
class UberPDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

def fill(pdf, x, y, w, h, color):
    pdf.set_fill_color(*color)
    pdf.rect(x, y, w, h, "F")

def box(pdf, x, y, w, h):
    pdf.set_fill_color(248, 250, 252) # Light light grey (slate-50)
    pdf.set_draw_color(*TILE_BORDER)
    pdf.rect(x, y, w, h, "FD")

def kpi_tile(pdf, x, y, w, h, label, value, color):
    box(pdf, x, y, w, h)
    # Draw top accent bar on the tile
    fill(pdf, x, y, w, 1.5, UBER_GREEN)
    # Label
    pdf.set_xy(x, y + 3)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(w, 4, label.upper(), align="C")
    # Value
    pdf.set_xy(x, y + 9)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*color)
    pdf.cell(w, 8, value, align="C")

def section_label(pdf, x, y, text):
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(0, 4, text.upper())

def bar_chart_h(pdf, x, y, w, h, clusters, colors):
    # Title
    pdf.set_xy(x + 4, y + 3)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*TEXT_DARK)
    pdf.cell(0, 4, "Rider Segment Share")
    
    # Find max percentage to scale bars
    max_val = max(c[1] for c in clusters)
    bar_h = (h - 12) / len(clusters)
    for i, (name, val) in enumerate(clusters):
        by = y + 8 + i * bar_h
        # Label
        pdf.set_xy(x + 4, by)
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(*TEXT_BODY)
        pdf.cell(32, bar_h * 0.65, name, align="L")
        
        # Bar
        bar_w = (w - 56) * val / max_val
        color = colors.get(name, UBER_GREEN)
        fill(pdf, x + 38, by + 0.5, bar_w, bar_h * 0.55, color)
        
        # Value
        pdf.set_xy(x + 39 + bar_w, by)
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(14, bar_h * 0.65, f"{val:.1f}%")

def hour_sparkline(pdf, x, y, w, h, values):
    max_v = max(values)
    bar_w = w / len(values)
    for i, v in enumerate(values):
        bh = max(1, h * v / max_v)
        bx = x + i * bar_w
        by = y + h - bh
        intensity = int(100 + 155 * v / max_v)
        fill(pdf, bx + 0.3, by, bar_w - 0.6, bh, (6, intensity, int(intensity * 0.53)))
    pdf.set_draw_color(*TILE_BORDER)
    pdf.line(x, y + h, x + w, y + h)
    for label, pos in [("0h", 0), ("6h", 6), ("12h", 12), ("18h", 18), ("23h", 23)]:
        lx = x + pos * bar_w
        pdf.set_xy(lx - 2, y + h + 1)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(*TEXT_MUTED)
        pdf.cell(8, 4, label)

# ── Main Report PDF Builder ──────────────────────────────────────────
def create_executive_pdf_report(user_name: str) -> str | None:
    try:
        pdf = UberPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(False)
        pdf.add_page()
        W, H = 210, 297

        # ── White page background ────────────────────────────────────────────
        fill(pdf, 0, 0, W, H, WHITE)

        # ── Top green accent bar (3 mm) ──────────────────────────────────────
        fill(pdf, 0, 0, W, 3, UBER_GREEN)

        # ── Logo + brand + title (inline, shifted down for elegant padding) ──
        logo_path = "uber_logo.jpg"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=10, w=18)

        # "Uber" in bold black
        pdf.set_xy(32, 10)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(*BLACK)
        pdf.cell(18, 10, "Uber", ln=0)

        # Thin vertical separator between "Uber" and title
        pdf.set_draw_color(*TILE_BORDER)
        pdf.line(52, 11, 52, 27)

        # "EXECUTIVE INSIGHTS REPORT" inline to the right of Uber
        pdf.set_xy(56, 10)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 10, "EXECUTIVE INSIGHTS REPORT")

        # "FARE EXPLORER" subtitle under Uber (fully padded, no cut-offs)
        pdf.set_xy(32, 20)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*UBER_GREEN)
        pdf.cell(20, 5, "FARE EXPLORER")

        # Dataset subtitle under the title
        pdf.set_xy(56, 20)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*TEXT_MUTED)
        pdf.cell(0, 5, "NYC UBER FARE ANALYSIS  |  191,822 TRIPS  |  2009 - 2015")

        # Full-width separator line with generous padding
        pdf.set_draw_color(*TILE_BORDER)
        pdf.line(10, 30, 200, 30)

        # ── KPI tiles (perfectly centered from x=10 to x=200) ────────────────
        section_label(pdf, 10, 35, "Key Performance Indicators")

        # Mathematically centered width: 5 tiles of 36.4mm + 4 gaps of 2mm = 190mm total width
        tile_w = 36.4
        tile_h = 24
        kpis = [
            ("Total Trips",  f"{INSIGHTS['total_trips']:,}",         TEXT_DARK),
            ("Avg Fare",     f"EUR {INSIGHTS['avg_fare']:.2f}",       GREEN_MUTED),
            ("Avg Distance", f"{INSIGHTS['avg_distance_km']:.1f} km", TEXT_DARK),
            ("Peak Hour",    f"{INSIGHTS['peak_hour']:02d}:00",        GREEN_MUTED),
            ("Micro-Trips",  f"{INSIGHTS['micro_trip_pct']:.1f}%",    TEXT_DARK),
        ]
        for i, (lbl, val, col) in enumerate(kpis):
            kpi_tile(pdf, 10 + i * (tile_w + 2), 41, tile_w, tile_h, lbl, val, col)

        # ── Strategic Summary (justified text alignment for clean look) ──────
        y0 = 71
        box_h = 42
        box(pdf, 10, y0, 190, box_h)
        fill(pdf, 10, y0, 3, box_h, UBER_GREEN)   # green left accent

        pdf.set_xy(16, y0 + 4)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 6, "STRATEGIC SUMMARY")

        summary = (
            "This report synthesises geospatial, temporal and pricing data from 191,822 NYC Uber "
            "trips into actionable business intelligence. Key findings point to clear micro-rush-hour "
            "demand spikes at 08:00 and 18:00, high-density pickup clusters in Midtown Manhattan, "
            "JFK and LaGuardia corridors, and a surge-pricing opportunity yielding an estimated "
            "+15.4% operational efficiency when fleet distribution is re-aligned to the 8 identified "
            "rider-profile clusters."
        )
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*TEXT_BODY)
        pdf.set_xy(16, y0 + 11)
        pdf.multi_cell(182, 5.2, summary, align="J")

        # ── Charts (y = 121 … 169) ────────────────────────────────────────────
        y1 = 121
        chart_h = 48

        section_label(pdf, 10, y1, "Intraday Demand Volume")
        section_label(pdf, 108, y1, "Rider Segment Distribution")

        # sparkline box
        box(pdf, 10, y1 + 6, 92, chart_h)
        hour_sparkline(pdf, 14, y1 + 9, 84, chart_h - 14, HOURLY)
        pdf.set_xy(10, y1 + chart_h - 2)
        pdf.set_font("Helvetica", "I", 6)
        pdf.set_text_color(*TEXT_MUTED)
        pdf.cell(92, 5, "Peak demand: 18:00 -- rush-hour surge window", align="C")

        # bar chart box
        box(pdf, 108, y1 + 6, 92, chart_h)
        bar_chart_h(pdf, 108, y1 + 7, 92, chart_h - 2, CLUSTERS, CLUSTER_COLORS)

        # ── Recommendations (y = 177 … 251) ───────────────────────────────────
        y2 = 177
        section_label(pdf, 10, y2, "Actionable Recommendations")

        recs = [
            ("1", "Fleet Surge Positioning",
             "Re-deploy 20-30% of fleet to Midtown and FiDi between 07:30-09:30 and 17:00-19:30 "
             "to capture peak demand and reduce rider wait times below the 3-minute threshold."),
            ("2", "Airport Corridor Optimisation",
             "JFK and LaGuardia corridors generate the highest fare/km ratios. Dedicated driver "
             "incentives during departure windows (05:00-08:00 and 14:00-17:00) can improve "
             "revenue per hour by an estimated 22%."),
            ("3", "Late-Night Group Ride Packages",
             "Cluster 7 (Evening Group Ride -- 8.9% of trips) shows peak 4-passenger loads after "
             "21:00 on Fridays and Saturdays. Flat-rate group pricing can grow this segment by "
             "an additional 12-15%."),
        ]

        rec_y = y2 + 6
        for r, title, body in recs:
            box(pdf, 10, rec_y, 190, 21)
            # numbered badge
            fill(pdf, 10, rec_y, 8, 21, UBER_GREEN)
            pdf.set_xy(10, rec_y + 6.5)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*WHITE)
            pdf.cell(8, 8, r, align="C")
            # title
            pdf.set_xy(22, rec_y + 3)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*TEXT_DARK)
            pdf.cell(0, 6, title)
            # body
            pdf.set_xy(22, rec_y + 9)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*TEXT_BODY)
            pdf.multi_cell(176, 4.0, body)
            rec_y += 23.5

        # ── Bottom footer band ────────────────────────────────────────────────
        fill(pdf, 0, H - 14, W, 14, (245, 245, 245))
        fill(pdf, 0, H - 2, W, 2, UBER_GREEN)
        pdf.set_xy(10, H - 11)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*TEXT_MUTED)
        pdf.cell(130, 5, "(c) 2026 Uber Fare Explorer | Academic Project | Machine Learning II")
        pdf.set_xy(140, H - 11)
        pdf.set_text_color(*GREEN_MUTED)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.cell(60, 5, "uberfares2-bwwu3ppswfnzujfisnbeoc.streamlit.app", align="R")

        out = "Analyst_Executive_Report.pdf"
        pdf.output(out)
        return out

    except Exception as e:
        print(f"PDF generation error: {e}")
        return None

if __name__ == "__main__":
    path = create_executive_pdf_report("Carlota Marto")
    print("Generated:", path)
