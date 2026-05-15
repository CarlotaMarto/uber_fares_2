import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def create_executive_pdf_report(user_name):
    # Set dark theme for matplotlib
    plt.style.use('dark_background')
    
    # Load sample data
    try:
        df = pd.read_csv('uber_cleaned_sample.csv')
    except Exception as e:
        print(f"Error loading data for report: {e}")
        return None
    
    # 1. Fare Amount Distribution Chart
    plt.figure(figsize=(6, 4), facecolor='#000000')
    ax1 = plt.axes()
    ax1.set_facecolor('#000000')
    df['fare_amount'].hist(bins=30, color='#06C167', edgecolor='black', alpha=0.8, ax=ax1)
    plt.title('Fare Amount Distribution', color='white', fontsize=12, pad=15)
    plt.xlabel('Fare ($)', color='#A6A6A6')
    plt.ylabel('Frequency', color='#A6A6A6')
    plt.grid(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('#333333')
    ax1.spines['left'].set_color('#333333')
    
    chart1_path = "chart1_temp.png"
    plt.tight_layout()
    plt.savefig(chart1_path, facecolor='#000000', dpi=150)
    plt.close()
    
    # 2. Rides by Passenger Count
    plt.figure(figsize=(6, 4), facecolor='#000000')
    ax2 = plt.axes()
    ax2.set_facecolor('#000000')
    passenger_counts = df['passenger_count'].value_counts().sort_index()
    passenger_counts.plot(kind='bar', color='#06C167', ax=ax2)
    plt.title('Rides by Passenger Count', color='white', fontsize=12, pad=15)
    plt.xlabel('Passenger Count', color='#A6A6A6')
    plt.ylabel('Number of Rides', color='#A6A6A6')
    plt.xticks(rotation=0)
    plt.grid(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color('#333333')
    ax2.spines['left'].set_color('#333333')
    
    chart2_path = "chart2_temp.png"
    plt.tight_layout()
    plt.savefig(chart2_path, facecolor='#000000', dpi=150)
    plt.close()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Fill background with black
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Add Logo
    if os.path.exists('uber_logo.jpg'):
        pdf.image('uber_logo.jpg', x=10, y=10, w=30)
    elif os.path.exists('uber_logo.png'):
        pdf.image('uber_logo.png', x=10, y=10, w=30)
        
    pdf.ln(15)
    
    # Title
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 15, "Executive Insights Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(166, 166, 166)
    pdf.cell(0, 10, f"Prepared for: {user_name}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Section 1
    pdf.set_text_color(6, 193, 103) # #06C167
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(200, 200, 200)
    summary_text = (
        "This automated report provides a high-level overview of the latest Uber fare "
        "and passenger trends. Busiest periods correlate heavily with peak commuter hours, "
        "and geospatial clustering reveals optimal positioning for driver fleets."
    )
    pdf.multi_cell(0, 6, summary_text)
    
    pdf.ln(10)
    
    # Section 2 - Charts
    pdf.set_text_color(6, 193, 103)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Key Metrics", ln=True)
    
    # Insert Charts
    pdf.image(chart1_path, x=10, y=pdf.get_y() + 5, w=90)
    pdf.image(chart2_path, x=110, y=pdf.get_y() + 5, w=90)
    
    pdf.ln(70) # Move down past images
    
    # Footer
    pdf.set_y(-30)
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Uber Fare Explorer - Academic Project by Carlota Marto & Francisca Teixeira", ln=True, align='C')
    
    # Save PDF
    pdf_path = "analyst_report.pdf"
    pdf.output(pdf_path)
    
    # Cleanup temp images
    try:
        os.remove(chart1_path)
        os.remove(chart2_path)
    except:
        pass
        
    return pdf_path

if __name__ == "__main__":
    create_executive_pdf_report("Test User")
