##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

import requests

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)
from modules.style import style_sidebar
style_sidebar()

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")

st.title('Best Life')

st.write('\n\n')
st.write('### Welcome to Best Life! Which user would you like to log in as?')

def get_usernames(role_name):
     role_id_res = requests.get(f"http://web-api:4000/users/users/role/{role_name}")
     if role_id_res.status_code != 200:
        logger.error(f"Failed to get role_id for {role_name}")
        return []
     
     role_id = role_id_res.json()
     if not role_id:
         logger.error(f"No role_id found for {role_name}")
         return []
     
     users_res = requests.get(f"http://web-api:4000/users/users/role/{role_id}")
     if users_res.status_code != 200:
         logger.error(f"Failed to get users for role_id {role_id}")
         return []
     
     return users_res.json()

def get_userID(user_name):
    user_id_res = requests.get(f"http://web-api:4000/users/users/getID/{user_name}")
    if user_id_res.status_code != 200:
        logger.error(f"Failed to get user_id for {user_name}")
        return None
     
    user_id = user_id_res.json()
    
    if "user_id" not in user_id:
        logger.error(f"No user_id found for {user_name}")
        return None
    
    return user_id["user_id"]
    

student_users = get_usernames("student")
policymaker_users = get_usernames("policymaker")
activist_users = get_usernames("activist")

st.write("#### Act as Grace, an Incoming University Student")
row1_col1, row1_col2 = st.columns([3, 1])
with row1_col1:
    grace_user = st.selectbox(
        label='',
        options=["Select username"] + student_users,
        label_visibility='collapsed',
        key='grace'
    )
with row1_col2:
    if st.button('Login', use_container_width=True, key='login_grace'):
        if grace_user == "Select username":
            st.session_state['grace_warning'] = True
        else:
            st.session_state['grace_warning'] = False
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'student'
            st.session_state['first_name'] = 'Grace'
            st.session_state['username'] = grace_user
            st.session_state['user_id'] = get_userID(grace_user)
            logger.info("Logging in as University Student Persona")
            st.switch_page('pages/00_University_Student_Home.py')
    warning_grace = st.empty()
    if st.session_state.get('grace_warning'):
        warning_grace.markdown(
            "<div style='color:#d33;font-size:0.9rem;'>Please select a student username.</div>",
            unsafe_allow_html=True
        )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

st.write("#### Act as James, a Policymaker")
row2_col1, row2_col2 = st.columns([3, 1])
with row2_col1:
    james_user = st.selectbox(
        label='',
        options=["Select username"] + policymaker_users,
        label_visibility='collapsed',
        key='james'
    )
with row2_col2:
    if st.button('Login', use_container_width=True, key='login_james'):
        if james_user == "Select username":
            st.session_state['james_warning'] = True
        else:
            st.session_state['james_warning'] = False
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'policymaker'
            st.session_state['first_name'] = 'James'
            st.session_state['username'] = james_user
            st.session_state['user_id'] = get_userID(james_user)
            logger.info("Logging in as Policymaker Persona")
            st.switch_page('pages/10_Policymaker_Home.py')
    warning_james = st.empty()
    if st.session_state.get('james_warning'):
        warning_james.markdown(
            "<div style='color:#d33;font-size:0.9rem;'>Please select a policymaker username.</div>",
            unsafe_allow_html=True
        )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

st.write("#### Act as Faye, an Activist")
row3_col1, row3_col2 = st.columns([3, 1])
with row3_col1:
    faye_user = st.selectbox(
        label='',
        options=["Select username"] + activist_users,
        label_visibility='collapsed',
        key='faye'
    )
with row3_col2:
    if st.button('Login', use_container_width=True, key='login_faye'):
        if faye_user == "Select username":
            st.session_state['faye_warning'] = True
        else:
            st.session_state['faye_warning'] = False
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'activist'
            st.session_state['first_name'] = 'Faye'
            st.session_state['username'] = faye_user
            st.session_state['user_id'] = get_userID(faye_user)
            logger.info("Logging in as Activist Persona")
            st.switch_page('pages/20_Activist_Home.py')
    warning_faye = st.empty()
    if st.session_state.get('faye_warning'):
        warning_faye.markdown(
            "<div style='color:#d33;font-size:0.9rem;'>Please select an activist username.</div>",
            unsafe_allow_html=True
        )