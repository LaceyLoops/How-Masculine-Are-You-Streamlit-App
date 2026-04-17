import streamlit as st

st.markdown("""
<style>
/* Make sure the class actually overrides Streamlit defaults */
a.link-hover {
    text-decoration: none !important;
    color: #1a73e8 !important;
    font-weight: 600;
    cursor: pointer;
}

/* Hover behavior */
a.link-hover:hover {
    text-decoration: underline !important;
    color: #0b5ed7 !important;
}
</style>

### This explains your result

<div style="font-size:18px; margin-top:10px; margin-bottom:10px;">
    👉 <a href="https://amzn.to/4cuanIh" target="_blank" class="link-hover">
        Get the science-based book behind your results
    </a>
</div>

<div style="font-size:14px; color:#666;">
    This quiz is based on the book.
</div>

<div style="font-size:12px; color:#999; margin-top:8px;">
    As an Amazon Associate, I earn from qualifying purchases.
</div>
""", unsafe_allow_html=True)