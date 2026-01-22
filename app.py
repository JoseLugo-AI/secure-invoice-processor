import streamlit as st
import pandas as pd
import io
from datetime import datetime
from extract import extract_invoice_data, security_audit

# 1. Page Configuration
st.set_page_config(page_title="Secure Invoice AI", layout="wide", page_icon="🛡️")

# --- CUSTOM CSS FOR THE RISK GAUGE ---
st.markdown("""
    <style>
    .risk-low { color: #28a745; font-size: 24px; font-weight: bold; }
    .risk-med { color: #fd7e14; font-size: 24px; font-weight: bold; }
    .risk-high { color: #dc3545; font-size: 24px; font-weight: bold; }
    .audit-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True) 

st.title("🛡️ Secure Invoice Enterprise")
st.caption(f"Batch Processing | EU/US Tax Compliant | System Date: {datetime.now().strftime('%d.%m.%Y')}")

# 2. Multi-File Uploader
uploaded_files = st.file_uploader("Upload Invoices", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    all_results = []
    
    for uploaded_file in uploaded_files:
        # Create a container for each invoice
        with st.container():
            st.markdown(f"### 📄 File: {uploaded_file.name}")
            file_bytes = uploaded_file.read()
            is_pdf = (uploaded_file.type == "application/pdf")
            
            col1, col2 = st.columns([1, 1.5])
            
            # --- PHASE 1: EXTRACTION (UI MESSAGE DISAPPEARS WHEN DONE) ---
            with col1:
                try:
                    # The 'with' block makes the message vanish once data is ready
                    with st.spinner("🔍 Extracting Data..."):
                        data = extract_invoice_data(file_bytes)
                    
                    st.success(f"**Vendor:** {data['vendor']}")
                    st.write(f"**Total:** {data['total']}")
                    st.write(f"**VAT/Tax:** {data['tax']}")
                    if data['items']:
                        st.dataframe(pd.DataFrame(data['items']), height=150)
                except Exception as e:
                    st.error(f"Extraction Error: {e}")
                    continue

            # --- PHASE 2: SECURITY AUDIT (UI MESSAGE DISAPPEARS WHEN DONE) ---
            with col2:
                report_key = f"report_{uploaded_file.name}"
                if report_key not in st.session_state:
                    try:
                        # The spinner message will vanish once the audit is complete
                        with st.spinner("🛡️ Performing Security Audit..."):
                            report = security_audit(file_bytes, data, is_pdf=is_pdf, original_name=uploaded_file.name)
                            st.session_state[report_key] = report
                    except Exception as e:
                        st.error(f"Audit Error: {e}")
                        continue
                
                report = st.session_state[report_key]
                
                # SINGLE SOURCE OF TRUTH: Parse the score once
                score = 0
                if "RISK_SCORE:" in report:
                    try:
                        raw_score_text = report.split("RISK_SCORE:")[1][:10]
                        score_digits = "".join(filter(str.isdigit, raw_score_text))
                        score = int(score_digits)
                    except:
                        score = 50 
                
                # Display the Gauge
                if score < 30: 
                    st.markdown(f"Risk Assessment: <span class='risk-low'>SAFE ({score}/100)</span>", unsafe_allow_html=True)
                elif score < 70: 
                    st.markdown(f"Risk Assessment: <span class='risk-med'>CAUTION ({score}/100)</span>", unsafe_allow_html=True)
                else: 
                    st.markdown(f"Risk Assessment: <span class='risk-high'>HIGH RISK ({score}/100)</span>", unsafe_allow_html=True)
                
                st.info(report)
                
                all_results.append({
                    "Filename": uploaded_file.name,
                    "Vendor": data['vendor'],
                    "Total": data['total'],
                    "Tax": data['tax'],
                    "Date": data['date'],
                    "Risk_Score": score
                })
            st.markdown("---")

    # --- EXCEL EXPORT ---
    if all_results:
        st.subheader("📊 Export Batch Results")
        df = pd.DataFrame(all_results)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Security_Audit')
        
        st.download_button(
            label="📥 Download Audit Report (Excel)",
            data=output.getvalue(),
            file_name=f"Security_Audit_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )