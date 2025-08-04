import streamlit as st
from utils import predict



st.title('Infer Politcal Stance and Topic')

st.markdown("This app analyzes a given text to predict its political topic, subtopic, and inferred political stance on the left–right spectrum.")


input = st.text_area(label="Input Text", placeholder="Input Your Text", max_chars=3800, height="content")

if st.button(label="Submit"):
    with st.spinner("Infering..", show_time=True):
        major, minor, stance, raw_stance = predict(input)

    st.subheader("Prediction Results")
    st.markdown(f"**Major Category:** {major}")
    st.markdown(f"**Minor Category:** {minor}")
    st.markdown(f"**Stance Score:** `{raw_stance:.3f}`")

    st.info(stance)

    st.markdown("*Note: The model currently performs more accurately on liberal-leaning texts. Improving balance is part of ongoing work with more conservative data.*")
    







