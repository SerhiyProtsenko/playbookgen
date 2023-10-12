import streamlit as st

st.set_page_config(
    page_title="AI Edgelabs Demo, PlaybookGen"
)

logo = 'https://static.scalarr.io/edgelabs-site-static/images/edgelabs.ico'
st.image(logo)


st.title('AI Edgelabs Demo, PlaybookGen')

with st.sidebar:
    #st.sidebar.markdown(unsafe_allow_html=True)     
    openai_api_key = st.text_input("Enter your API Key:", type="password", help="You can find your API key at https://platform.openai.com/account/api-keys")
    st.session_state["openai_api_key"] = openai_api_key

    # Add the drop-down selectors for Industry and Company Size
    industry = st.selectbox(
    "Select your company's industry:",
    sorted(['Aerospace / Defense', 'Agriculture / Food Services', 
            'Automotive', 'Construction', 'Education', 
            'Energy / Utilities', 'Finance / Banking', 
            'Government / Public Sector', 'Healthcare', 
            'Hospitality / Tourism', 'Insurance', 
            'Legal Services', 'Manufacturing', 
            'Media / Entertainment', 'Non-profit', 
            'Real Estate', 'Retail / E-commerce', 
            'Technology / IT', 'Telecommunication', 
            'Transportation / Logistics'])
    , placeholder="Select Industry")
    st.session_state["industry"] = industry

    company_size = st.selectbox("Select your company's size:", ['Small (1-50 employees)', 'Medium (51-200 employees)', 'Large (201-1,000 employees)', 'Enterprise (1,001-10,000 employees)', 'Large Enterprise (10,000+ employees)'], placeholder="Select Company Size")
    st.session_state["company_size"] = company_size

    st.sidebar.markdown("---")

    #st.sidebar.markdown( unsafe_allow_html=True)        
    
    


#st.markdown( unsafe_allow_html=True)
st.markdown("Use MITRE ATT&CK and Large Language Models to generate playbook scenarios for incident response", unsafe_allow_html=True)
st.markdown("---")


st.markdown("""          
            ### Welcome to AI Edgelabs Demo, PlaybookGen!
            
            The MITRE ATT&CK framework is a powerful tool for understanding the tactics, techniques, and procedures (TTPs) used by threat actors; however, it can be difficult to translate this information into realistic playbook.

            PlaybookGen solves this problem by using large language models to quickly generate documents based on a selection of a threat actor group's known techniques.

            ### Getting Started

            1. Enter your  API key and select your company's industry and size from the sidebar. 
            2. Go to the `Threat Group Scenarios` page to generate a scenario based on a threat actor group's known techniques, or go to the `Custom Scenarios` page to generate a scenario based on your own selection of ATT&CK techniques.
            """)