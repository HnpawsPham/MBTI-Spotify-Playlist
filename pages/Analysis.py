import streamlit as st
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from joblib import load as joblib_load
from utilities import *

def run():
    st.markdown(f'<h1 style="text-align: center;">Prediction from audio features</h1>', unsafe_allow_html=True)

    # LOAD MODEL AND SCALER
    @st.cache_resource
    def load_mbti_utilities():
        ie_model = load_model("models/ie_model.keras")
        ns_model = load_model("models/ns_model.keras")
        tf_model = load_model("models/tf_model.keras")
        jp_model = load_model("models/jp_model.keras")
        scaler = joblib_load("models/mbti_scaler.pkl")
        return ie_model, ns_model, tf_model, jp_model, scaler


    # GET FILE FROM INPUT
    def load_all():
        file = st.file_uploader("📂 Upload file `.json`", type="json")
        if not file:
            return
        
        # read .json info
        try:
            data = json.load(file)
        except Exception as e:
            st.error("Không thể đọc file JSON.")
            return
        
        predict_mbti(data)


    # PREDICT PLAYLIST MBTI
    def get_mbti(ie, ns, tf, jp):
        return f"{'E' if ie else 'I'}{'S' if ns else 'N'}{'F' if tf else 'T'}{'P' if jp else 'J'}"

    def predict_mbti(data):
        if missing := [k for k in playlist_features if k not in data]:
            st.error(f"Thiếu trường: {', '.join(missing)}")
            return

        x = np.array([[data[k] for k in playlist_features]])

        # get models
        try:
            ie_model, ns_model, tf_model, jp_model, scaler = load_mbti_utilities()
            x_scaled = scaler.transform(x)
        except Exception as e:
            st.error("Không thể load model hoặc scaler MBTI")
            st.exception(e)
            return

        # get pred
        ie = int(ie_model.predict(x_scaled)[0][0] > 0.5)
        ns = int(ns_model.predict(x_scaled)[0][0] > 0.5)
        tf = int(tf_model.predict(x_scaled)[0][0] > 0.5)
        jp = int(jp_model.predict(x_scaled)[0][0] > 0.5)

        
        res = get_mbti(ie, ns, tf, jp)

        st.success(f"Dự đoán: **{res}**")
        st.write(f"- I/E: {'E' if ie else 'I'}")
        st.write(f"- N/S: {'S' if ns else 'N'}")
        st.write(f"- T/F: {'F' if tf else 'T'}")
        st.write(f"- J/P: {'P' if jp else 'J'}")

        st.session_state.mbti = res

    load_all()