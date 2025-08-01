import streamlit as st
import pandas as pd
import os
import json
from langchain_core.messages import HumanMessage, AIMessage
from backend.core.backend import PythonChatbot, InputData
import pickle
import time

# Monochromatic Color Palette
PRIMARY = "#25282b"   # Main dark background
SECONDARY = "#f8f8f8" # Off-white for contrast
TEXT_DARK = "#FFFFFF" # White text everywhere
BACKGROUND = PRIMARY   # Main background
CARD = "#2d3035"      # Slightly lighter than PRIMARY for cards/sections
ACCENT = "#35373b"    # For subtle accents, buttons, etc.
BORDER = "#3a3d42"    # For borders and dividers

# Custom CSS for monochromatic theme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND} !important;
        color: {TEXT_DARK} !important;
    }}
    /* Header full-width, dark background */
    .main-header {{
        background: {PRIMARY};
        width: 100vw;
        margin: 0 calc(-50vw + 50%);
        padding: 1rem 0.5rem 0.5rem 0.5rem;
        border-radius: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        box-shadow: 0 4px 24px rgba(37,40,43,0.24);
    }}
    .main-header .logo, .main-header .nav a, .main-header .nav .signup {{
        color: {TEXT_DARK} !important;
    }}
    .main-header .nav .signup {{
        background: {ACCENT};
        border-radius: 8px;
        font-weight: 700;
        padding: 0.4rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }}
    .main-header .nav .signup:hover {{
        background: {SECONDARY};
        color: {PRIMARY} !important;
    }}
    /* Hero section full width, slightly lighter dark */
    .hero-section {{
        width: 100vw;
        margin: 0 calc(-50vw + 50%);
        padding: 3rem 0 2.5rem 0;
        border-radius: 0;
        background: {CARD};
        color: {TEXT_DARK};
        text-align: center;
        box-shadow: 0 4px 24px rgba(37,40,43,0.08);
        border: none;
        max-width: 100vw;
    }}
    .hero-section h1, .hero-section p {{
        color: {TEXT_DARK};
    }}
    /* All cards, tables, preview, chat, etc. use CARD color */
    .stDataFrame, .stTable, .stMetric, .stFileUploader, .stJson, .stMarkdown[data-testid="stMarkdownContainer"]:has(h3), .stMarkdown[data-testid="stMarkdownContainer"]:has(h2), .stMarkdown[data-testid="stMarkdownContainer"]:has(h1), .themed-card, .whats-happening-card, .element-container, .block-container {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border-radius: 8px;
        border: 1px solid {BORDER};
        box-shadow: none !important;
    }}
    /* Remove white backgrounds and shadows from all containers, cards, and boxes */
    .stMarkdown, .stText, .stExpander, .stButton, .stSelectbox, .stTextInput, .stSlider, .stRadio, .stCheckbox, .stNumberInput, .stDateInput, .stTimeInput, .stColorPicker, .stForm {{
        background: {CARD} !important;
        box-shadow: none !important;
        border: none !important;
        color: {TEXT_DARK} !important;
    }}
    .block-container {{
        background: {BACKGROUND} !important;
    }}
    /* Sidebar styling */
    .stApp [data-testid="stSidebar"] > div:first-child {{
        background-color: {ACCENT};
        border-right: 1px solid {BORDER};
        color: {TEXT_DARK};
    }}
    /* Button styling */
    .stButton > button {{
        background: {ACCENT};
        color: {TEXT_DARK};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: {SECONDARY};
        color: {PRIMARY};
    }}
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {CARD};
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(37,40,43,0.08);
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {SECONDARY};
        border-radius: 6px;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ACCENT} !important;
        color: {TEXT_DARK} !important;
    }}
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div > select {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {{
        border-color: {SECONDARY};
        box-shadow: 0 0 0 2px rgba(248,248,248,0.2);
    }}
    /* Chat message styling */
    .stChatMessage, .stChatInput > div > div > input {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stChatMessage[data-testid="chat-message-user"] {{
        background-color: {ACCENT};
        color: {TEXT_DARK};
    }}
    .stChatMessage[data-testid="chat-message-assistant"] {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border-left: 4px solid {SECONDARY};
    }}
    /* Expander styling */
    .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {CARD};
        color: {TEXT_DARK};
        border-radius: 8px;
        border: 1px solid {BORDER};
    }}
    /* Code block styling */
    .stCode {{
        background-color: {ACCENT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        color: {TEXT_DARK};
    }}
    /* Plotly chart container */
    .js-plotly-plot {{
        background-color: {CARD};
        border-radius: 8px;
        border: 1px solid {BORDER};
    }}
    .whats-happening-card {{
        width: 195vw !important;
        max-width: 195vw !important;
        min-width: 0 !important;
        margin-left: calc(-50vw + 50%) !important;
        margin-right: calc(-50vw + 50%) !important;
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border-radius: 8px;
        border: none !important;
        box-shadow: none !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .debug-title {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    .stTabs {{
        background-color: {CARD} !important;
        color: {TEXT_DARK} !important;
        border-radius: 8px;
        border: 1px solid {BORDER};
        box-shadow: none !important;
    }}
    .stDataFrame {{
        width: 46vw !important;
        max-width: 46vw !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }}
    .themed-card, .whats-happening-card {{
        align-items: stretch !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Detect logged-in user
user_logged_in = st.session_state.get('user')
if user_logged_in:
    username = user_logged_in if isinstance(user_logged_in, str) else user_logged_in[1] if isinstance(user_logged_in, tuple) else user_logged_in.get('username', None)
else:
    username = None

# Set up user-specific upload and data dictionary paths
if username:
    user_upload_dir = os.path.join('uploads', username)
    os.makedirs(user_upload_dir, exist_ok=True)
    user_data_dict_path = os.path.join(user_upload_dir, 'data_dictionary.json')
    if os.path.exists(user_data_dict_path):
        with open(user_data_dict_path, 'r') as f:
            data_dictionary = json.load(f)
    else:
        data_dictionary = {}
else:
    # Fallback for not logged in: use session state
    if 'user_files' not in st.session_state:
        st.session_state['user_files'] = []
    user_upload_dir = 'uploads'
    user_data_dict_path = 'data_dictionary.json'
    if os.path.exists(user_data_dict_path):
        with open(user_data_dict_path, 'r') as f:
            data_dictionary = json.load(f)
    else:
        data_dictionary = {}

st.title("📊 Insights Dashboard")

# Use columns for Data Management (left) and Chat Interface (right)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="themed-card">', unsafe_allow_html=True)
    st.header("📁 Data Management")
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Upload CSV files", 
        type="csv", 
        accept_multiple_files=True,
        help="Select one or more CSV files to analyze"
    )

    if uploaded_files:
        # Save uploaded files and track in session or user folder
        for file in uploaded_files:
            file_path = os.path.join(user_upload_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            if not username:
                if file.name not in st.session_state['user_files']:
                    st.session_state['user_files'].append(file.name)
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")

    # Only show files uploaded by this user (or in session if not logged in)
    if username:
        available_files = [f for f in os.listdir(user_upload_dir) if f.endswith('.csv')]
    else:
        # For guests, always include 'sample.csv' if it exists
        guest_files = [f for f in st.session_state['user_files'] if f.endswith('.csv')]
        if os.path.exists(os.path.join('uploads', 'sample.csv')):
            if 'sample.csv' not in guest_files:
                guest_files.insert(0, 'sample.csv')
        available_files = guest_files

    if available_files:
        # File selection
        selected_files = st.multiselect(
            "📋 Select files to analyze",
            available_files,
            key="selected_files",
            help="Choose which files you want to work with"
        )
        
        # Dictionary to store new descriptions
        new_descriptions = {}
        
        if selected_files:
            st.subheader(f"📄 File Preview ({len(selected_files)} selected)")
            
            # Create tabs for each selected file
            file_tabs = st.tabs(selected_files)
            
            # Display dataframe previews and data dictionary info in tabs
            for tab, filename in zip(file_tabs, selected_files):
                with tab:
                    try:
                        df = pd.read_csv(os.path.join(user_upload_dir, filename))
                        
                        # Show basic info
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.metric("📊 Rows", f"{len(df):,}")
                        with col_info2:
                            st.metric("📋 Columns", len(df.columns))
                        with col_info3:
                            st.metric("💾 Size", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                        
                        st.write(f"**Preview of {filename}:**")
                        st.dataframe(df.head(), use_container_width=True)
                        
                        # Display/edit data dictionary information
                        st.subheader("📝 Dataset Information")
                        if filename in data_dictionary:
                            info = data_dictionary[filename]
                            current_description = info.get('description', '')
                        else:
                            current_description = ''
                            
                        new_descriptions[filename] = st.text_area(
                            "Dataset Description",
                            value=current_description,
                            key=f"description_{filename}",
                            help="Provide a description of this dataset",
                            height=100
                        )
                        
                        if filename in data_dictionary:
                            info = data_dictionary[filename]
                            if 'coverage' in info:
                                st.write(f"**🌐 Coverage:** {info['coverage']}")
                            if 'features' in info:
                                st.write("**🔧 Features:**")
                                for feature in info['features']:
                                    st.write(f"• {feature}")
                            if 'usage' in info:
                                st.write("**💡 Usage:**")
                                if isinstance(info['usage'], list):
                                    for use in info['usage']:
                                        st.write(f"• {use}")
                                else:
                                    st.write(f"• {info['usage']}")
                            if 'linkage' in info:
                                st.write(f"**🔗 Linkage:** {info['linkage']}")
                                
                    except Exception as e:
                        st.error(f"❌ Error loading {filename}: {str(e)}")
            
            # Save button for descriptions
            if st.button("💾 Save Descriptions", type="primary"):
                for filename, description in new_descriptions.items():
                    if description:  # Only update if description is not empty
                        if filename not in data_dictionary:
                            data_dictionary[filename] = {}
                        data_dictionary[filename]['description'] = description
                
                # Save updated data dictionary
                with open(user_data_dict_path, 'w') as f:
                    json.dump(data_dictionary, f, indent=4)
                st.success("✅ Descriptions saved successfully!")
    else:
        st.info("📤 No CSV files available. Please upload some files first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="themed-card">', unsafe_allow_html=True)
    st.header("💬 Chat Interface")
    
    # Add chat loading state and pending message
    if 'chat_loading' not in st.session_state:
        st.session_state['chat_loading'] = False
    if 'pending_user_message' not in st.session_state:
        st.session_state['pending_user_message'] = None

    def on_submit_user_query():
        # Step 1: Set loading and store message, do not process AI yet
        st.session_state['chat_loading'] = True
        st.session_state['pending_user_message'] = st.session_state['user_input']
        # Return immediately to allow UI to update

    # Step 2: On rerun, if loading and pending message, process AI
    if st.session_state.get('chat_loading', False) and st.session_state.get('pending_user_message'):
        # Show animation for 2 seconds for testing
        time.sleep(2)
        user_query = st.session_state['pending_user_message']
        input_data_list = [
            InputData(
                variable_name=f"{file.split('.')[0]}", 
                data_path=os.path.abspath(os.path.join(user_upload_dir, file)), 
                data_description=data_dictionary.get(file, {}).get('description', '')
            ) 
            for file in selected_files
        ]
        st.session_state.visualisation_chatbot.user_sent_message(user_query, input_data=input_data_list)
        st.session_state['chat_loading'] = False
        st.session_state['pending_user_message'] = None
        st.rerun()

    if 'selected_files' in st.session_state and st.session_state['selected_files']:
        if 'visualisation_chatbot' not in st.session_state:
            st.session_state.visualisation_chatbot = PythonChatbot()
        chat_container = st.container(height=500)
        with chat_container:
            # Show loading animation if AI is processing
            if st.session_state.get('chat_loading', False):
                st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;">', unsafe_allow_html=True)
                st.image("images/brain_thinking.gif", width=120)
                st.markdown('<div style="font-size:1.3rem;font-weight:600;color:#fff;text-align:center;">Thinking...</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Display chat history with associated images
                for msg_index, msg in enumerate(st.session_state.visualisation_chatbot.chat_history):
                    if isinstance(msg, HumanMessage):
                        with st.chat_message("user"):
                            st.markdown(msg.content)
                    elif isinstance(msg, AIMessage):
                        with st.chat_message("assistant"):
                            st.markdown(msg.content)
                            # Display associated plots if they exist
                            if msg_index in st.session_state.visualisation_chatbot.output_image_paths:
                                image_paths = st.session_state.visualisation_chatbot.output_image_paths[msg_index]
                                for image_path in image_paths:
                                    try:
                                        with open(os.path.join("images/plotly_figures/pickle", image_path), "rb") as f:
                                            fig = pickle.load(f)
                                        st.plotly_chart(fig, use_container_width=True, key=f"plotly_chart_{msg_index}_{image_path}")
                                    except Exception as e:
                                        st.error(f"Error loading plot: {str(e)}")
        # Chat input
        st.chat_input(
            placeholder="💭 Ask me anything about your data...",
            on_submit=on_submit_user_query,
            key='user_input'
        )
    else:
        st.info("📋 Please select files to analyze in the Data Management section first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# What's Happening section
whats_happening_tab, = st.tabs(["🐞 Debug"])
with whats_happening_tab:
    st.markdown('<div class="whats-happening-card">', unsafe_allow_html=True)
    st.markdown('<div class="debug-title">🐞 Debug</div>', unsafe_allow_html=True)
    
    if 'visualisation_chatbot' in st.session_state and hasattr(st.session_state.visualisation_chatbot, 'intermediate_outputs'):
        if st.session_state.visualisation_chatbot.intermediate_outputs:
            for i, output in enumerate(st.session_state.visualisation_chatbot.intermediate_outputs):
                with st.expander(f"🔄 Step {i+1}", expanded=False):
                    if isinstance(output, dict):
                        if 'thought' in output:
                            st.markdown("### 💭 Thought Process")
                            st.markdown(output['thought'])
                        if 'code' in output:
                            st.markdown("### 💻 Code")
                            st.code(output['code'], language="python")
                        if 'output' in output:
                            st.markdown("### 📤 Output")
                            st.text(output['output'])
                    else:
                        st.markdown("### 📤 Output")
                        st.text(str(output))
        else:
            st.info("🤖 No debug information available yet. Start a conversation to see intermediate outputs.")
    else:
        st.info("🤖 No debug information available yet. Start a conversation to see intermediate outputs.")
    
    st.markdown('</div>', unsafe_allow_html=True)