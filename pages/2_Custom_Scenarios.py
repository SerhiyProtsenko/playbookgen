import os

import pandas as pd
import streamlit as st
from langchain.callbacks.manager import collect_runs
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
#from langsmith import Client
from mitreattack.stix20 import MitreAttackData

# Add environment variables for LangSmith
#os.environ["LANGCHAIN_TRACING_V2"]="true"
#os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
#os.environ["LANGCHAIN_PROJECT"] = "AttackGen"
#os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]

# Initialize the LangSmith client
#client = Client()

logo = 'https://static.scalarr.io/edgelabs-site-static/images/edgelabs.ico'
st.image(logo)

st.title('AI Edgelabs Demo, PlaybookGen')


# Check if 'openai_api_key' exists in the session state
if "openai_api_key" not in st.session_state:
    st.error("""
             API key not found!
             
             Please go to the `Welcome` page and enter your API key to continue.
             """)
    st.stop()
else:
    openai_api_key = st.session_state["openai_api_key"]

if "custom_scenario_generated" not in st.session_state:
    st.session_state["custom_scenario_generated"] = False

industry = st.session_state["industry"]
company_size = st.session_state["company_size"]

#st.set_page_config(
#    page_title="Generate Custom Scenario"
#)

# Load and cache the MITRE ATT&CK data
@st.cache_resource
def load_attack_data():
    attack_data = MitreAttackData("./data/enterprise-attack.json")
    return attack_data

attack_data = load_attack_data()

# Get all techniques
@st.cache_resource
def load_techniques():
    try:
        techniques = attack_data.get_techniques()
        techniques_list = []
        for technique in techniques:
            for reference in technique.external_references:
                if "external_id" in reference:
                    techniques_list.append({
                        'id': technique.id,
                        'Technique Name': technique.name,
                        'External ID': reference['external_id'],
                        'Display Name': f"{technique.name} ({reference['external_id']})"
                    })
        techniques_df = pd.DataFrame(techniques_list)
        
        return techniques_df
    except Exception as e:
        print(f"Error in load_techniques: {e}")
        return pd.DataFrame() # Return an empty DataFrame

techniques_df = load_techniques()

def generate_scenario(openai_api_key, messages):
    try:
        with st.status('Generating Playbook...', expanded=True):
            st.write("Initialising AI model.")
            llm = ChatOpenAI(openai_api_key=openai_api_key, streaming=False)
            st.write("Model initialised. Generating Playbook, please wait.")

            with collect_runs() as cb:
                response = llm.generate(messages=[messages])
                run_id1 = cb.traced_runs[0].id  # Get run_id from the callback

            st.write("Playbook generated successfully.")
            st.session_state['run_id'] = run_id1  # Store the run ID in the session state
        return response
    except Exception as e:
        st.error("An error occurred while generating the Playbook: " + str(e))
        return None

st.markdown("Generate Custom Playbook", unsafe_allow_html=True)

st.markdown("""
            ### Select ATT&CK Techniques

            Use the multi-select box below to select the ATT&CK techniques that you would like to include in a custom Playbook.
            """)

selected_techniques = []
if not techniques_df.empty:
    selected_techniques = st.multiselect("Select ATT&CK techniques for the Playbook",
                                         sorted(techniques_df['Display Name'].unique()), placeholder="Select Techniques", label_visibility="hidden")
    st.info("📝 Techniques are searchable by either their name or technique ID (e.g. `T1556` or `Phishing`).")
    
try:
    if len(selected_techniques) > 0:
        selected_techniques_string = ', '.join(selected_techniques)

        # Create System Message Template
        system_template = "You are a cybersecurity expert. Your task is to produce a comprehensive playbook include the incident response on the information provided."
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        # Create Human Message Template
        human_template = ("""
**Background information:**
The company operates in the '{industry}' industry and is of size '{company_size}'. 

**Threat actor information:**
The threat actor is known to use the following ATT&CK techniques:
{selected_techniques_string}

**Your task:**
Create an playbook include the incident response based on the information provided. The goal of the playbook is to provide the details incident response capabilities against a threat actor group that uses the identified ATT&CK techniques. 

Your response should be well structured and formatted using Markdown. Write in British English.
""")
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # Construct the ChatPromptTemplate
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        # Format the prompt
        messages = chat_prompt.format_prompt(selected_techniques_string=selected_techniques_string, 
                                            industry=industry, 
                                            company_size=company_size).to_messages()
        st.markdown("")
        st.markdown("""
            ### Generate a Playbook

            Click the button below to generate a Playbook based on the selected technique(s).

            It normally takes between 30-50 seconds to generate a Playbook. ⏱️
            """)
        if st.button('Generate Playbook'):
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
            elif not industry:
                st.info("Please select your company's industry to continue.")
            elif not company_size:
                st.info("Please select your company's size to continue.")
            else:
                # Generate a scenario
                response = generate_scenario(openai_api_key, messages)
                st.markdown("---")
                if response is not None:
                    st.session_state['custom_scenario_generated'] = True
                    custom_scenario_text = response.generations[0][0].text
                    st.session_state['custom_scenario_text'] = custom_scenario_text  # Store the generated scenario in the session state
                    st.markdown(custom_scenario_text)
                    st.download_button(label="Download Playbook", data=custom_scenario_text, file_name="custom_scenario.md", mime="text/markdown")
        else:
            # If a scenario has been generated previously, display it
            if 'custom_scenario_text' in st.session_state and st.session_state['custom_scenario_generated']:
                st.markdown("---")
                st.markdown(st.session_state['custom_scenario_text'])
                st.download_button(label="Download Playbook", data=st.session_state['custom_scenario_text'], file_name="custom_scenario.md", mime="text/markdown")
        
        
                
                
except Exception as e:
    st.error("An error occurred: " + str(e))
    

