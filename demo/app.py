import streamlit as st
from utils import predict



st.title('Infer Politcal Stance and Topic')


input = st.text_area(label="Text", placeholder="Input Your Text", max_chars=3800, height="content")

if st.button(label="Submit"):
    with st.spinner("Infering..", show_time=True):
        major, minor, stance, raw_stance = predict(input)

    st.subheader("Prediction Results")
    st.markdown(f"**Major Category:** {major}")
    st.markdown(f"**Minor Category:** {minor}")
    st.markdown(f"**Stance Score:** `{raw_stance:.3f}`")

    st.info(stance)
    






