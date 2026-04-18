import streamlit as st
import requests
from PIL import Image
import io
import json

# Page configuration
st.set_page_config(
    page_title="Leaf Disease Detection",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .analysis-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .disease-indicator {
        display: inline-flex;
        align-items: center;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 10px 0;
    }
    .diseased {
        background-color: #ffebee;
        border: 3px solid #f44336;
        color: #c62828;
    }
    .healthy {
        background-color: #e8f5e9;
        border: 3px solid #4caf50;
        color: #2e7d32;
    }
    .status-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }
    .red-dot {
        background-color: #f44336;
        box-shadow: 0 0 10px #f44336;
    }
    .green-dot {
        background-color: #4caf50;
        box-shadow: 0 0 10px #4caf50;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Header
st.markdown('<h1 class="main-header">🌿 AI Leaf Disease Detection System</h1>', unsafe_allow_html=True)
st.markdown("### Upload a leaf image to detect diseases and get treatment recommendations")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    This system uses **Llama Vision** (Groq) to:
    - Detect plant diseases
    - Assess severity levels
    - Recommend treatments
    - Provide prevention tips
    """)
    
    st.header("📊 Supported Features")
    st.success("""
    ✅ Multiple disease detection
    ✅ Severity assessment
    ✅ Treatment recommendations
    ✅ Organic alternatives
    ✅ Prevention measures
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of the plant leaf"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("🔍 Analyze Leaf", type="primary"):
            with st.spinner("Analyzing image..."):
                try:
                    # Prepare file for API
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    
                    # Send request to API
                    response = requests.post(f"{API_URL}/analyze-leaf", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store in session state
                        st.session_state['analysis'] = result['analysis']
                        st.session_state['structured_data'] = result['structured_data']
                        st.session_state['model'] = result['model_used']
                        
                        st.success("✅ Analysis complete!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
                    st.info("Make sure the FastAPI server is running on http://localhost:8000")

with col2:
    st.subheader("📋 Analysis Results")
    
    if 'analysis' in st.session_state:
        # Display structured data first for disease status
        try:
            structured = json.loads(st.session_state['structured_data'])
            is_diseased = structured.get('is_diseased', True)
            disease_name = structured.get('disease_name', 'Unknown')
            
            # Disease Status Indicator with colored dot
            if is_diseased:
                st.markdown(f"""
                    <div class="disease-indicator diseased">
                        <span class="status-dot red-dot"></span>
                        <span>⚠️ DISEASE DETECTED: {disease_name}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="disease-indicator healthy">
                        <span class="status-dot green-dot"></span>
                        <span>✅ HEALTHY LEAF</span>
                    </div>
                """, unsafe_allow_html=True)
            
        except json.JSONDecodeError:
            st.warning("Could not parse disease status")
        
        # Display full analysis
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown(st.session_state['analysis'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display detailed structured data
        st.subheader("📊 Detailed Analysis")
        try:
            structured = json.loads(st.session_state['structured_data'])
            
            col_a, col_b = st.columns(2)
            with col_a:
                disease_display = structured.get('disease_name', 'N/A')
                severity_display = structured.get('severity', 'N/A')
                
                # Color code the metrics
                if is_diseased:
                    st.markdown(f"**Disease:** :red[{disease_display}]")
                    st.markdown(f"**Severity:** :red[{severity_display}]")
                else:
                    st.markdown(f"**Status:** :green[{disease_display}]")
                    st.markdown(f"**Severity:** :green[{severity_display}]")
                    
            with col_b:
                st.metric("Confidence", structured.get('confidence', 'N/A'))
                st.metric("Model", st.session_state.get('model', 'N/A'))
            
            if 'symptoms' in structured and structured['symptoms']:
                st.write("**🔍 Symptoms Observed:**")
                for symptom in structured['symptoms']:
                    st.write(f"- {symptom}")
            
            if 'treatments' in structured and structured['treatments']:
                st.write("**💊 Recommended Treatments:**")
                for treatment in structured['treatments']:
                    st.write(f"- {treatment}")
            
            if 'prevention' in structured and structured['prevention']:
                st.write("**🛡️ Prevention Measures:**")
                for prevention in structured['prevention']:
                    st.write(f"- {prevention}")
                    
        except json.JSONDecodeError:
            st.warning("Could not parse detailed analysis data")
        
        # Download report
        if st.button("📥 Download Report"):
            report = f"""
LEAF DISEASE ANALYSIS REPORT
{'=' * 50}

{st.session_state['analysis']}

{'=' * 50}
Generated by AI Leaf Disease Detection System
Model: {st.session_state.get('model', 'N/A')}
"""
            st.download_button(
                label="Download as TXT",
                data=report,
                file_name="leaf_analysis_report.txt",
                mime="text/plain"
            )
    else:
        st.info("👆 Upload and analyze a leaf image to see results here")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Powered by Llama Vision (Groq) | FastAPI | Streamlit</p>",
    unsafe_allow_html=True
)