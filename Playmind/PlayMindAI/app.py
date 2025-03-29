import streamlit as st
import pandas as pd
from utils.ai_service import generate_strategy
from utils.database import save_to_database, get_previous_sessions
from utils.pdf_service import export_to_pdf, FPDF_AVAILABLE
import time
import uuid
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PlanMind AI - Business Strategy Consultant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar navigation
st.sidebar.title("PlanMind AI")
st.sidebar.subheader("Business Strategy Consultant")
page = st.sidebar.radio("Navigation", ["Generate Strategy", "My Sessions", "About"])

# About section in sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This app uses AI to generate business strategies based on your input problems.
    
    Simply describe your business problem, and the AI will provide you with three strategic 
    approaches, complete with resource allocation, steps, and risk analysis.
    """
)

# Main content
if page == "Generate Strategy":
    st.title("Business Strategy Generator")
    st.write("Describe your business problem below, and our AI consultant will generate strategic approaches to solve it.")
    
    with st.form("strategy_form"):
        business_problem = st.text_area(
            "Business Problem:",
            placeholder="Example: Our e-commerce company is struggling with high customer acquisition costs and low retention rates...",
            height=150
        )
        
        industry = st.selectbox(
            "Industry:",
            ["Technology", "Retail", "Healthcare", "Finance", "Manufacturing", "Education", "Other"]
        )
        
        company_size = st.selectbox(
            "Company Size:",
            ["Startup (1-10 employees)", "Small (11-50 employees)", "Medium (51-200 employees)", "Large (201-1000 employees)", "Enterprise (1000+ employees)"]
        )
        
        submitted = st.form_submit_button("Generate Strategic Plan")
    
    if submitted and business_problem:
        # Generate a unique ID for this session
        session_id = str(uuid.uuid4())
        
        # Create context from additional inputs
        context = f"Industry: {industry}\nCompany Size: {company_size}"
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate processing steps (for better UX)
        status_text.text("Analyzing business problem...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        status_text.text("Consulting industry best practices...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        status_text.text("Generating strategic approaches...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        status_text.text("Analyzing risks and limitations...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        status_text.text("Finalizing recommendations...")
        progress_bar.progress(100)
        
        # Generate the actual strategy
        with st.spinner("Finalizing your strategic plan..."):
            response = generate_strategy(business_problem, context)
            
            # Create timestamp in ISO format
            timestamp = datetime.now().isoformat()
            
            # Save to database
            session_data = {
                "session_id": session_id,
                "user_id": st.session_state.user_id,
                "problem": business_problem,
                "context": context,
                "response": response,
                "timestamp": timestamp
            }
            save_to_database(session_data)
            
            # Add to session state
            st.session_state.history.append({
                "id": session_id,
                "problem": business_problem[:50] + "..." if len(business_problem) > 50 else business_problem,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "response": response
            })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Success message
        st.success("Strategic plan generated successfully!")
        
        # Display the strategy
        st.markdown("## Your Strategic Plan")
        st.markdown(response)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if FPDF_AVAILABLE and st.button("Export to PDF"):
                pdf_data = export_to_pdf(business_problem, context, response)
                st.download_button(
                    "Download PDF",
                    data=pdf_data,
                    file_name="business_strategy_plan.pdf",
                    mime="application/pdf"
                )
            elif not FPDF_AVAILABLE:
                st.warning("PDF export is not available. Install FPDF package to enable this feature.")
        
        with col2:
            if st.button("Start New Strategy"):
                st.experimental_rerun()

elif page == "My Sessions":
    st.title("Previous Strategy Sessions")
    
    if not st.session_state.history:
        st.info("You haven't generated any strategies yet. Go to the 'Generate Strategy' page to create your first strategy.")
    else:
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{session['timestamp']} - {session['problem']}"):
                st.markdown(session["response"])
                
                # Export option
                if FPDF_AVAILABLE and st.button(f"Export to PDF #{i}"):
                    pdf_data = export_to_pdf("", "", session["response"])
                    st.download_button(
                        "Download PDF",
                        data=pdf_data,
                        file_name=f"strategy_plan_{session['id']}.pdf",
                        mime="application/pdf"
                    )

else:  # About page
    st.title("About PlanMind AI")
    st.markdown("""
    ## How It Works
    
    This tool leverages AI to analyze your business problem and generate comprehensive strategic approaches. 
    
    For each business problem, the AI consultant will:
    
    1. **Generate 3 different strategic approaches**
       - Each with a unique name and brief description
    
    2. **Provide detailed information for each strategy**
       - Estimated resource allocation (people, budget, tools, timeline)
       - Major steps involved in implementation
    
    3. **Identify potential risks & limitations**
       - Along with suggested mitigation plans
    
    4. **Suggest optimization tips**
       - Additional tools or AI-powered enhancements
    
    ## Technology Stack
    
    - **AI Engine**: Multiple AI services with fallback options
    - **Backend & Frontend**: Python with Streamlit
    - **Data Storage**: Supabase with local fallback
    - **Reporting**: PDF Export functionality
    
    ## Get Started
    
    Navigate to the "Generate Strategy" page to create your first business strategy plan.
    """)

    # Show an example strategy
    if st.button("See Example Strategy"):
        example_response = generate_strategy(
            "Our software company is struggling with long development cycles and frequent bugs in production.",
            "Industry: Technology\nCompany Size: Medium (51-200 employees)"
        )
        st.markdown("## Example Strategy")
        st.markdown(example_response) 