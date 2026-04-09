import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from fpdf import FPDF
import joblib
from datetime import datetime, timedelta


if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

def auth():

    st.title("🔐 Healthy Buddy Login / Signup")

    choice = st.radio("Select Option", ["Login", "Signup"])

    username = st.text_input("Username").strip().lower()
    password = st.text_input("Password", type="password").strip()

    # SIGNUP 

    if choice == "Signup":
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.warning("User already exists ")
            else:
                st.session_state.users[username] = password
                st.success("Account Created Now Login")

    #  LOGIN 

    if choice == "Login":
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success(f"Welcome {username} ")
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")


# SHOW LOGIN FIRST

if not st.session_state.logged_in:
    auth()
    st.stop()



# SETUP & CONFIG 

st.set_page_config(page_title="Healthy Buddy Pro", page_icon="🌐", layout="wide")

# Gemini Setup

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
ai_model = genai.GenerativeModel("gemini-pro")

# MULTI-LANGUAGE DICTIONARY 

LANG_DATA = {
    "English": {
        "title": "Clinical AI Intelligence",
        "inputs": "Patient Vitals",
        "name_label": "👤 Full Name",
        "analyze_btn": "🚀 Analyze Clinical Vitals",
        "hosp_head": "🚨 EMERGENCY CONTACTS",
        "diet_head": "🥗 Personalized Diet Chart",
        "future_head": "🔮 6-Month Risk Prediction",
        "ask_ai": "🤖 Ask Health Buddy AI",
        "ai_placeholder": "Type your health question here...",
        "ai_btn": "Ask AI",
        "rhyme": "Hello {}, how are you my friend?<br>Follow the diet, and let your illness end!<br>Health prediction is now in your hand,<br>Healthy Buddy is the best in the land!"
    },
    "Hindi": {
        "title": "क्लिनिकल AI इंटेलिजेंस",
        "inputs": "मरीज के वाइटल्स",
        "name_label": "👤 मरीज का नाम",
        "analyze_btn": "🚀 जांच शुरू करें",
        "hosp_head": "🚨 इमरजेंसी संपर्क",
        "diet_head": "🥗 व्यक्तिगत आहार चार्ट",
        "future_head": "🔮 6-महीने का स्वास्थ्य अनुमान",
        "ask_ai": "🤖 हेल्थ बड़ी AI से पूछें",
        "ai_placeholder": "अपना सवाल यहाँ लिखें...",
        "ai_btn": "पूछें",
        "rhyme": "नमस्ते {}, कैसे हो मेरे यार?<br>डाइट और चार्ट से, मिटाओ हर एक बीमार!<br>हेल्थ प्रेडिक्शन है अब आपके हाथ,<br>हेल्दी बड़ी है हमेशा आपके साथ!"
    },
    "Hinglish": {
        "title": "Clinical AI Intelligence",
        "inputs": "Patient Vitals Daalo",
        "name_label": "👤 Patient ka Naam",
        "analyze_btn": "🚀 Report Check Karo",
        "hosp_head": "🚨 EMERGENCY CONTACTS",
        "diet_head": "🥗 Diet Chart Check Karo",
        "future_head": "🔮 Agle 6 Mahine ka Risk",
        "ask_ai": "🤖 AI Doctor se Baat Karo",
        "ai_placeholder": "Kuch sawal pucho...",
        "ai_btn": "Sawal Pucho",
        "rhyme": "Hello {}, kaise ho mere yaar?<br>Diet aur chart se, mitao har ek bimar!<br>Health prediction hai ab aapke haath,<br>Healthy Buddy hai hamesha aapke saath!"
    }
}



#  DETAILED DIET DATABASE

DETAILED_DIET = {
    "Diabetes": {
        "Morning": "🕒 8:00 AM: Soaked Methi seeds + Green Tea + 2 Oats Idli",
        "Lunch": "🕒 1:30 PM: 2 Missi Roti + Large bowl of Dal + Steamed veggies",
        "Snack": "🕒 5:00 PM: Handful of roasted Chana + Roasted Makhana",
        "Dinner": "🕒 8:30 PM: Vegetable Soup + Grilled Paneer/Tofu Salad",
        "Avoid": "Sugar, White Rice, Potato, Sweet Fruits, Maida"
    },
    "High BP": {
        "Morning": "🕒 8:00 AM: DASH Diet - Oatmeal with Flax seeds + 1 Banana",
        "Lunch": "🕒 1:30 PM: Brown rice (1 cup) + Low-salt Curd + Boiled veggies",
        "Snack": "🕒 5:00 PM: 1 Apple + Coconut Water (No added salt)",
        "Dinner": "🕒 8:30 PM: Baked Fish/Moong Dal + Steamed Broccoli",
        "Avoid": "Pickles, Papad, Extra Salt, Fried Food, Canned Soups"
    },
    "General": {
        "Morning": "🕒 8:00 AM: Mixed Sprouts + 1 seasonal fruit + Milk",
        "Lunch": "🕒 1:30 PM: Balanced Thali (Dal, Roti, Sabzi, Salad)",
        "Snack": "🕒 5:00 PM: Green tea + Walnuts/Almonds",
        "Dinner": "🕒 8:30 PM: Vegetable Khichdi + Papaya bowl",
        "Avoid": "Excess Oil, Junk Food, Sugary Drinks, Late night snacks"
    }
}

# ENTERPRISE UI STYLING 

st.markdown("""
    <style>
    .stApp { background: #020617; color: #f1f5f9; }
    .glass-card { 
        padding: 25px; border-radius: 20px; background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 20px;
    }
    .diet-card {
        background: linear-gradient(135deg, #064e3b, #065f46);
        padding: 20px; border-radius: 15px; border-left: 10px solid #10b981;
    }
    .avoid-box {
        background: rgba(220, 38, 38, 0.2); padding: 15px;
        border-radius: 10px; border: 1px solid #ef4444; margin-top: 10px;
    }
    h1, h2, h3 { color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)


# SIDEBAR & STATE DB 


MASTER_HOSPITALS = {
    "Andaman & Nicobar": "GB Pant Hospital, ANIIMS, Pillar Hospital",
    "Andhra Pradesh": "Apollo (Vizag), KIMS (Nellore), Care, Manipal, Star, Sunshine",
    "Arunachal Pradesh": "TRIHMS, Bakin Pertin, RK Mission, Heema, Niba, Gyati",
    "Assam": "GMC Guwahati, Nemcare, Apollo, Hayat, GNRC, Marwari Hospital",
    "Bihar": "AIIMS Patna, IGIMS, Paras HMRI, Ruban, Mediversal, Ford Hospital",
    "Chandigarh": "PGIMER, GMSH-16, Fortis, Max Mohali",
    "Chhattisgarh": "AIIMS Raipur, Ramkrishna Care, Apollo, Vyas, Shree Narayana, Balco",
    "Dadra and Nagar Haveli": "Shri Vinoba Bhave Civil Hospital",
    "Daman and Diu": "Government Hospital Daman",
    "Delhi (UT)": "AIIMS, Safdarjung, Max Saket, Fortis, Medanta, Ganga Ram",
    "Goa": "GMC Bambolim, Manipal, Victor, Healthway, Vision, Vintage",
    "Gujarat": "Civil Ahmedabad, Zydus, Sterling, Apollo, Shalby, HCG Cancer",
    "Haryana": "Medanta GGM, Fortis, Artemis, Paras, Metro, Park Hospital",
    "Himachal Pradesh": "IGMC Shimla, Tanda Medical, Fortis Kangra, Indus, MMU, Civil",
    "Jammu and Kashmir": "SKIMS, SMHS, GMC Jammu, ASCOMS",
    "Jharkhand": "RIMS Ranchi, TMH Jamshedpur, Medica, Orchid, Brahmananda, Hill View",
    "Karnataka": "Manipal, Narayana Health, Fortis, Aster CMI, Apollo, St. John's",
    "Kerala": "Aster Medcity, Amrita, KIMS, Rajagiri, Baby Memorial, Medical Trust",
    "Ladakh": "SNM Hospital Leh, District Hospital Kargil",
    "Lakshadweep": "Rajiv Gandhi Hospital, Agatti",
    "Madhya Pradesh": "AIIMS Bhopal, Choithram, Bombay Hosp, Bansal, Chirayu, Apollo",
    "Maharashtra": "Lilavati, Sahyadri, Kokilaben, Breach Candy, SevenHills, Nanavati",
    "Manipur": "RIMS, Shija, JNIMS, Raj Medicity, Sky Hospital, City Hosp",
    "Meghalaya": "NEIGRIHMS, Nazareth, Civil Hosp, Woodland, Bethany, Supercare",
    "Mizoram": "Civil Aizawl, Trinity, New Life, Synod, Ebenezer, Greenwood",
    "Nagaland": "Naga Hosp, CIHSR, Eden, Zion, Oking, Bethel",
    "Odisha": "AIIMS BBSR, SUM, KIMS, AMRI, Care, Ashwini",
    "Puducherry": "JIPMER, PIMS, Indira Gandhi Medical College",
    "Punjab": "PGIMER, Fortis Mohali, DMC, CMC Ludhiana, Max, Ivy Hospital",
    "Rajasthan": "SMS Hosp, EHCC, Fortis, Mahatma Gandhi, Narayana, CK Birla",
    "Sikkim": "STNM Gangtok, CRH Manipal, Sangram, Namchi, Geyzing, Singtam",
    "Tamil Nadu": "Apollo, CMC Vellore, MIOT, MGM, Kauvery, SIMS",
    "Telangana": "Yashoda, NIMS, Apollo, Continental, KIMS, Care",
    "Tripura": "AGMC, ILS, TMC Hapania, IGM, Agartala City, Tripura Med",
    "Uttar Pradesh": "Medanta LKO, SGPGI, KGMU, Regency, Apollo, Jaypee",
    "Uttarakhand": "AIIMS Rishikesh, Max Doon, Jolly Grant, Synergy, Kailash, GDMC",
    "West Bengal": "SSKM, Apollo, AMRI, Fortis, Tata Medical, Peerless"
}


with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3304/3304567.png", width=100)
    sel_lang = st.selectbox("🌐 Choose Language", ["English", "Hindi", "Hinglish"])
    sel_state = st.selectbox("📍 Select State", sorted(MASTER_HOSPITALS.keys()))
    st.divider()
    st.info("Health Tip: Drink at least 3L of water daily.")

L = LANG_DATA[sel_lang] 


#  MAIN INTERFACE

st.markdown(f"<h1 style='text-align:center;'>🩺 {L['title']}</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"<div class='glass-card'><h3>📝 {L['inputs']}</h3>", unsafe_allow_html=True)
    p_name = st.text_input(L['name_label'], placeholder="Enter Name")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Age", 1, 100, 25)
    weight = c2.number_input("Weight (kg)", 10, 200, 70)
    glucose = c3.number_input("Glucose (mg/dL)", 40, 500, 110)
    
    s1, s2, s3 = st.columns(3)
    systolic = s1.slider("Systolic BP", 80, 200, 120)
    hba1c = s2.slider("HbA1c %", 4.0, 15.0, 5.5)
    hr = s3.slider("Heart Rate", 40, 180, 72)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='background:linear-gradient(to right, #b91c1c, #991b1b); padding:20px; border-radius:15px; text-align:center;'>
            <h3>{L['hosp_head']}</h3>
            <h1 style='margin:0;'>📞 108 / 102</h1>
        </div>
        <div class='glass-card' style='margin-top:15px;'>
            <b>🏥 Top Hospitals ({sel_state}):</b><br>{MASTER_HOSPITALS[sel_state]}
        </div>
    """, unsafe_allow_html=True)

# ANALYTICS & FUTURE PREDICTION 

if st.button(L['analyze_btn']):
    # Risk Logic
    risk_score = (glucose/300 * 40) + (systolic/180 * 40) + (hba1c/12 * 20)
    risk_percent = round(risk_score * 100, 1)
    
    if glucose > 170 or hba1c > 6.5: category = "Diabetes"
    elif systolic > 140: category = "High BP"
    else: category = "General"

    # Display Gauge and Future Chart
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("📊 Risk Probability")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=risk_percent, 
                        gauge={'bar':{'color':"red" if risk_percent > 60 else "green"}}))
        st.plotly_chart(fig, use_container_width=True)
    
    with r2:
        st.subheader(f"📈 {L['future_head']}")
        months = ["Current", "Month 1", "Month 2", "Month 3", "Month 4", "Month 5"]

        # Simplified prediction logic for trend visualization

        trend = [risk_percent, risk_percent-2, risk_percent-5, risk_percent-8, risk_percent-12, risk_percent-15]
        fig_trend = px.line(x=months, y=trend, markers=True, template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)


    #  DETAILED DIET CHART (BIGGER DISPLAY)

    st.divider()
    st.markdown(f"## {L['diet_head']} ({category})")
    diet = DETAILED_DIET[category]
    
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"""<div class='diet-card'>
            <h3>📅 Daily Schedule</h3>
            <p>{diet['Morning']}</p>
            <p>{diet['Lunch']}</p>
            <p>{diet['Snack']}</p>
            <p>{diet['Dinner']}</p>
        </div>""", unsafe_allow_html=True)
    
    with d2:
        st.markdown(f"""<div class='avoid-box'>
            <h3 style='color:#ef4444;'>🚫 STRICTLY AVOID</h3>
            <p>{diet['Avoid']}</p>
        </div>""", unsafe_allow_html=True)


# CHATBOT 

st.divider()
st.subheader(f"💬 {L['ask_ai']}")
user_q = st.text_input(L['ai_placeholder'])

if st.button(L['ai_btn']):
    if user_q:
        prompt = f"Answer the following health query in {sel_lang} language briefly: {user_q}"
        resp = ai_model.generate_content(prompt)
        st.info(resp.text)

# Floating Rhyme Chatbot 

display_name = p_name if p_name else ("Buddy" if sel_lang=="English" else "दोस्त")

st.markdown(f"""
    <div style="position:fixed; bottom:20px; right:20px; width:300px; background:#0f172a; border:2px solid #3b82f6; border-radius:20px; padding:15px; z-index:1000;">
        <b style="color:#60a5fa;">🤖 Health Buddy AI</b><br><br>
        <span style="font-size:14px; color:white;">
            {L['rhyme'].format(display_name)}
        </span>
    </div>
""", unsafe_allow_html=True)
