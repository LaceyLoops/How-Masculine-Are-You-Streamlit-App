import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(layout="centered", page_title="Share the Quiz")

APP_URL = "https://your-app-url.streamlit.app"

def build_share_links(quiz_url):
    share_text = "This quiz read me… I didn’t expect this 😭 you need to try this"

    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(quiz_url)

    whatsapp_url = f"https://wa.me/?text={encoded_text}%20{encoded_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_text}"
    x_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
    reddit_url = f"https://www.reddit.com/submit?url={encoded_url}&title={encoded_text}"

    instagram_caption = (
        "This quiz read me… I didn’t expect this\n"
        f"😭 you need to try this {quiz_url}"
    )

    instagram_url = "https://www.instagram.com/"

    return {
        "whatsapp": whatsapp_url,
        "facebook": facebook_url,
        "x": x_url,
        "reddit": reddit_url,
        "instagram_url": instagram_url,
        "instagram_caption": instagram_caption,
    }

def render_share_buttons(share_links):
    buttons_html = f"""
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;margin-bottom:10px;">

            <a href="{share_links['whatsapp']}" target="_blank"
               style="background:#25D366;color:white;padding:10px 16px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
               WhatsApp
            </a>

            <a href="{share_links['x']}" target="_blank"
               style="background:#000000;color:white;padding:10px 16px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
               X
            </a>

            <a href="{share_links['facebook']}" target="_blank"
               style="background:#1877F2;color:white;padding:10px 16px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
               Facebook
            </a>

            <a href="{share_links['instagram_url']}" target="_blank"
               style="background:linear-gradient(45deg,#F58529,#FEDA77,#DD2A7B,#8134AF,#515BD4);
                      color:white;padding:10px 16px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
               Instagram
            </a>

            <a href="{share_links['reddit']}" target="_blank"
               style="background:#FF4500;color:white;padding:10px 16px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:inline-block;">
               Reddit
            </a>

        </div>
    """
    components.html(buttons_html, height=70)

quiz_url = "https://your-app-url.streamlit.app"
share_links = build_share_links(APP_URL)

st.title("Share the Quiz")
st.write("Share the quiz with friends or explore more below.")

st.markdown("### Share the quiz")
render_share_buttons(share_links)

st.markdown("### Share on Instagram")
st.info(
    "Instagram doesn't support direct web sharing. Tap the Instagram button above to open Instagram, "
    "then copy and paste this into your Story, bio, or DM:"
)
st.code(share_links["instagram_caption"])

st.markdown("### To Learn More About Yourself (And Others)")
st.markdown("**Get [The book](https://amzn.to/4cuanIh)** this science based quiz is from.")
st.caption("As an Amazon Associate, I earn from qualifying purchases.")

st.markdown(f"[Take the quiz again]({APP_URL})")
#st.page_link("app.py", label="Retake the quiz")