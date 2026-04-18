#For both males and females. 

#The user answers 30 questions. Each answer has a certain value. 

#The sum of the answers is calculated and the value returned is weighed on a scale/spectrum to determine how masculine one is or is not. 

 
import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import urllib.parse
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import uuid
from datetime import datetime

st.set_page_config(layout="centered")

REQUIRE_EMAIL_FOR_RESULTS = True

brevo_api_key = st.secrets["brevoAPI"]
sender_email = st.secrets["sender_email"]
sender_name = st.secrets["sender_name"]

 
# Title of the app
st.title('How Masculine/Feminine Are You Quiz!')

#Display The Welcome Message 
st.image(r"images/Banner.png", use_container_width=True)

st.markdown(
    """
    <div style="display:flex; justify-content:flex-end;">
        <a href="/explore" target="_blank" style="
            display:inline-block;
            padding:10px 18px;
            border-radius:10px;
            text-decoration:none;
            font-weight:600;
            color:white;
            background:linear-gradient(90deg, #4da3ff, #ff5fbf);
        ">
            Explore
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

#Gender Determination 
 
if "gender" not in st.session_state:
    st.session_state.gender = None

if st.session_state.gender is None:
    selected_gender = st.radio(
        "Were you born male or female?",
        ["Male", "Female"],
        index=None
    )

    if st.button("Start Quiz"):
        
        if selected_gender is None:
            st.warning("Please select your biological sex to begin the quiz.")
            st.stop()
        else:
            st.session_state.gender = selected_gender
            st.rerun()

    st.stop()

gender = st.session_state.gender
if gender == "Male":
    a_value = 10
elif gender == "Female":
    a_value = 15
else:
    a_value = 0

b_value = 5
c_value = -5

total_a = 0 

total_b = 0 

total_c = 0 


st.markdown("""
<style>
.stProgress {
    position: sticky;
    top: 20px;
    z-index: 999;
    background-color: white;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

progress_placeholder = st.empty()

if gender:


#Questions 
    questions = [
#ask the first question 
    {
        "question": "When it comes to reading a map or street directory you:",
        "options": ["Have difficulty and often ask for help",
                    "Turn it round to face the direction you're going",
                    "Have no difficulty reading maps or street directories"], 

    },
#ask the second question 
    {
        "question": "You're cooking a complicated meal with the radio playing and a friend phones. Do you:", 
        "options": ["Leave the radio on and continue cooking while talking on the phone",
                    "Turn the radio off, talk and keep cooking",
                    "Say you'll call them back as soon as you've finished cooking"],
    },
#ask the third Question 
    {
        "question": "Friends are coming to visit and ask for directions to your new house. Do you:",  
        "options": ["Draw a map with clear directions and send it to them or get someone else to explain how to get there",
                    "Ask what landmarks they know then try to explain to them how to get there",
                    "Explain verbally how to get there: 'take the m3 to newcastle, turn at the junction, turn left, go to the second traffic lights...'"],  
    },
#ask the fourth Question 
    {
        "question": "When explaining an idea or concept, are you more likely to:",
        "options": ["Use a pencil, paper and body language gestures",
                    "Explain it verbally using body language and gestures",
                    "Explain it verbally, being clear and concise"],
    }, 
#ask the fifth Question 
    {
        "question": "When coming home from a great movie, you prefer to:", 
        "options": ["Picture scenes from the movie in your mind",
                    "Talk about the scenes and what was said",
                    "Quote mainly what was said in the movie"],
    },
#ask the sixth Question 
    {
        "question": "In a cinema/hall/auditorium, you usually prefer to sit:",
        "options": ["On the right side",
                    "Anywhere",
                    "On the left side"], 
    },
#ask the seventh Question 
    {
        "question": "A friend has something mechanical that won't work. You would:",
        "options": ["Sympathise, and discuss how they feel about it",
                    "Recommend someone reliable who can fix it",
                    "Figure out how it works and attempt to fix it for them"],  
    },
#ask the eighth Question 
    {
        "question": "You're in an unfamiliar place and someone asks you where north is. You:",  
        "options": ["Confess you don't know",
                    "Guess where it is, after a bit of thought",
                    "Point towards north without difficulty"], 
    },
#ask the ninth Question 
    {
        "question": "You've found a parking space but it's tight and you must reverse into it. You would:",
        "options": ["Rather try to find another space",
                    "Carefully attempt to back into it",
                    "Reverse into it without any difficulty."], 
    },
#ask the tenth Question 
    {
        "question": "You are watching tv when the telephone rings. You would:",
        "options": ["Answer the phone with the tv on",
                    "Turn the tv down and then answer",
                    "Turn the tv off, tell others to be Quiet and then answer"], 
    },
#ask the eleventh Question 
    {
        "question": "You've just heard a new song by your favourite artist. Usually you:",
        "options": ["Can sing some of the song afterwards without difficulty",
                    "Can sing some of it afterwards if it's a really simple song",
                    "Find it hard to remember how the song sounded but you might recall some of the words"],  
    },
#ask the twelfth Question 
    {
        "question": "You are best at predicting outcomes by:",
        "options": ["Using intuition",
                    "Making a decision based on both the available information and 'gut feeling'",
                    "Using facts, statistics and data"],  
    },
#ask the thirteenth Question 
    {
        "question": "You've misplaced your keys. Would you:",
        "options": ["Do something else until the answer comes to you",
                    "Do something else, but keep trying to remember where you put them",
                    "Mentally retrace your steps until you remember where you left them"],
    },
#ask the fourteenth Question 
    {
        "question": "You're in a hotel room and you hear the distant sound of a siren. you:",
        "options": ["Couldn't identify where it's coming from",
                    "Could probably point to it if you concentrate",
                    "Could point straight to where it's coming from"],
    },
#ask the fifteenth Question 
    {
        "question": "You go to a social meeting and are introduced to seven or eight new people. Next day you:",
        "options": ["Can easily picture their faces",
                    "Would remember a few of their faces",
                    "Would be more likely to remember their names"],
    },
#ask the sixteenth Question 
    {
        "question": "You want to go to the country for your holiday but your partner wants to go to a beach resort. to convince them your idea is better, you:",
        "options": ["Tell them sweetly how you feel: you love the countryside and the kids and family always have fun there",
                    "Tell them if they go to the country you'll be grateful and will be happy to go to the beach next time",
                    "Use the facts: the country resort is closer, cheaper, and well-organised for sporting and leisure activities"],
    },
#ask the seventeenth Question 
    {
        "question": "When planning your day's activities, you usually:",
        "options": ["Write a list so you can see what needs to be done",
                    "Think of the things you need to do",
                    "Picture in your mind the people you will see, places you will visit and things you'll be doing"],
    },
#ask the eighteenth Question 
    {
        "question": "A friend has a personal problem and has come to discuss it with you. you:",
        "options": ["Are sympathetic and understanding",
                    "Say that problems are never as bad as they seem and explain why",
                    "Give suggestions or rational advice on how to solve the problem"],
    },
#ask the nineteenth Question  
    {
        "question": "Two friends from different marriages are having a secret affair. How likely are you to spot it?",
        "options": ["You could spot it very early",
                    "You'd pick up on it half the time",
                    "You'd probably miss it"],
    },
#ask the twentieth Question
    {
        "question": "What is life all about, as you see it?",
        "options": ["Having friends and living in harmony with those around you",
                    "Being friendly to others while maintaining personal independence",
                    "Achieving worthwhile goals, earning others' respect and winning prestige and advancement"],
    },
#ask the twenty first Question 
    {
        "question": "Given the choice, you would prefer to work:",
        "options": ["In a team where people are compatible",
                    "Around others but maintaining your own space",
                    "By yourself"],
    },
#ask the twenty second Question 
    {
        "question": "The books you prefer to read are:",
        "options": ["Novels and fiction",
                    "Magazines and newspapers",
                    "Non-fiction, autobiographies"],
    },
#ask the twenty third Question 
    {
        "question": "When you go shopping you tend to:",
        "options": ["Often buy on impulse, particularly the specials",
                    "Have a general plan but take it as it comes",
                    "Read the labels and compare costs"],
    },
#ask the twenty fourth Question 
    {
        "question": "you prefer to go to bed, wake up and eat meals:",
        "options": ["Whenever you feel like it",
                    "On a basic schedule but you are flexible",
                    "At about the same time each day"],
    },
#ask the twenty fifth Question 
    {
        "question": "you've started a new job and met lots of new people on the staff. one of them phones you when you are at home. you would:",
        "options": ["Find it easy to recognise their voice",
                    "Recognise it about half the time",
                    "Have difficulty identifying the voice"],
    },
#ask the twenty sixth Question 
    {
        "question": "what upsets you most when arguing with someone?",
        "options": ["Their silence or lack of response",
                    "When they won't see your point of view",
                    "Their probing or challenging questions and comments"],
    },
#ask the twenty seventh Question 
    {
        "question": "in school how did you feel about spelling tests and writing essays?",
        "options": ["You found them both fairly easy",
                    "You were generally ok with one but not the other",
                    "You weren't very good at either"],
    },
#ask the twenty eighth Question
    {
        "question": "when it comes to dancing or jazz routines, you:",
        "options": ["Can 'feel' the music once you've learnt the steps",
                    "Can do some exercises or dances, but get lost with others",
                    "Have difficulty keeping time or rhythm"],
    },
#ask the twenty ninth Question
    {
        "question": "how good are you at identifying and mimicking animal sounds?",
        "options": ["Not very good",
                    "Reasonable",
                    "Very good"],
    },
#ask the thirtieth Question 
    {
        "question": "at the end of a long day, you usually prefer to:",
        "options": ["talk to friends or family about your day",
                    "listen to others talk about their day",
                    "read a paper, watch tv and not talk"],
    }
]      

def get_interpretation(score):

    if score < 0:
        title = "🔷 Highly Masculine Thinking"
        text = "Your results show a strong analytical and logical thinking with minimal emotional influence."

    elif score < 150:
        title = "🔵 Masculine Thinking"
        text = "Your results show an analytical, structured and data-driven thinking style."

    elif score <= 180:
        title = "🟢 Balanced Thinking"
        text = "Your results show a flexible mix of analytical logic and intuitive thinking."

    else:
        title = "🩷 Feminine-Wired Thinking"
        text = "Your results show a highly intuitive, creative and emotionally aware thinking style."

    extra = """
                Most men score between 0-180 and most women 150-300.
                Lower scores reflect more analytical thinking, while higher scores indicate stronger intuitive and creative thinking."""

    return title, text, extra

#Share buttons

def build_share_links(quiz_url, total_score):
    share_text = f"This quiz read me… I didn’t expect this\n😭 you need to try this"
                #"I just took this Masculine/Feminine Thinking Quiz. Take it here:"

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


def calculate_score(answers, questions, a_value, b_value, c_value):
    total_a = 0
    total_b = 0
    total_c = 0

    for index, answer in enumerate(answers):
        if answer == questions[index]["options"][2]:
            total_c += 1
        elif answer == questions[index]["options"][1]:
            total_b += 1
        else:
            total_a += 1

    total_score = (total_a * a_value) + (total_b * b_value) + (total_c * c_value)
    return total_score


CSV_PATH = "quiz_results.csv"

def load_results(csv_path=CSV_PATH):
    required_cols = [
        "AttemptID",
        "Name",
        "Email",
        "Gender",
        "Score",
        "IsAnonymous",
        "CompletedAt",
        "BrevoMessageID",
        "BrevoUUID",
        "BrevoTags",
        "BrevoSubject",
        "BrevoStatus",
        "BrevoEvent",
        "BrevoEventAt",
        "BrevoReason",
        "BrevoWebhookEmail",
        "BrevoWebhookID",
    ]

    text_cols = [
        "AttemptID",
        "Name",
        "Email",
        "Gender",
        "CompletedAt",
        "BrevoMessageID",
        "BrevoUUID",
        "BrevoTags",
        "BrevoSubject",
        "BrevoStatus",
        "BrevoEvent",
        "BrevoEventAt",
        "BrevoReason",
        "BrevoWebhookEmail",
        "BrevoWebhookID",
    ]

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=required_cols)
    else:
        df = pd.DataFrame(columns=required_cols)

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Force text columns to object/string-safe dtype
    for col in text_cols:
        df[col] = df[col].astype("object")

    # Keep Score numeric where possible
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")

    # Keep IsAnonymous flexible / boolean-like
    df["IsAnonymous"] = df["IsAnonymous"].astype("object")

    return df


def save_attempt(
    attempt_id, 
    name="", 
    email="", 
    gender="", 
    score=None,     
    brevo_message_id="",
    brevo_uuid="",
    brevo_tags="",
    brevo_subject="",
    brevo_status="",
    brevo_event="",
    brevo_event_at="",
    brevo_reason="",
    brevo_webhook_email="",
    brevo_webhook_id="",
    csv_path=CSV_PATH
):
    df = load_results(csv_path)

    clean_email = email.strip().lower()

    new_row = {
        "AttemptID": attempt_id,
        "Name": name,
        "Email": clean_email,
        "Gender": gender,
        "Score": score,
        "IsAnonymous": clean_email == "",
        "CompletedAt": datetime.now().isoformat(timespec="seconds"),

        "BrevoMessageID": brevo_message_id,
        "BrevoUUID": brevo_uuid,
        "BrevoTags": brevo_tags,
        "BrevoSubject": brevo_subject,
        "BrevoStatus": brevo_status,
        "BrevoEvent": brevo_event,
        "BrevoEventAt": brevo_event_at,
        "BrevoReason": brevo_reason,
        "BrevoWebhookEmail": brevo_webhook_email,
        "BrevoWebhookID": brevo_webhook_id,
    }

    match_index = df.index[df["AttemptID"].astype(str) == str(attempt_id)]

    if len(match_index) > 0:
        i = match_index[0]

        for key, value in new_row.items():
            if key in ["AttemptID", "Name", "Email", "Gender", "Score", "IsAnonymous", "CompletedAt"] or value not in ["", None]:
                # make sure non-score columns can accept strings
                if key != "Score":
                    df[key] = df[key].astype("object")
                df.at[i, key] = value
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(csv_path, index=False)

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

def reset_quiz(change_gender=False):
    st.session_state.current_question = 0
    st.session_state.answers = [None] * len(questions)
    st.session_state.quiz_completed = False
    st.session_state.total_score = None
    st.session_state.email_sent = False
    st.session_state.result_saved = False
    st.session_state.attempt_id = str(uuid.uuid4())

    if change_gender:
        st.session_state.gender = None

def render_results(total_score, gender):
    title, text, extra = get_interpretation(total_score)
    quiz_url = "https://your-app-url.streamlit.app"
    share_links = build_share_links(quiz_url, total_score)

    st.success("Quiz complete!")
    st.subheader(title)
    st.write(f"**Your score is:** {total_score}")
    st.write(text)
    st.write(extra)

    st.markdown("### Share the quiz with friends")
    render_share_buttons(share_links)
    
    st.markdown("### To Share on Instagram")
    st.info(
        "Instagram doesn't support direct web sharing. Tap the Instagram button above to open Instagram, "
        "then copy and paste this into your Story, bio, or DM:"
    )
    st.code(share_links["instagram_caption"])


    st.markdown("### Want to Learn More About Yourself (And everyone else)?")
    st.markdown("Get **[the science-based book](https://amzn.to/4cuanIh)** behind your results")
    st.caption("As an Amazon Associate, I earn from qualifying purchases.")



def get_verified_pool_count(gender, csv_path=CSV_PATH):
    df = load_results(csv_path)

    if df.empty:
        return 0

    df["Email"] = df["Email"].fillna("").astype(str).str.strip().str.lower()
    df["CompletedAt"] = pd.to_datetime(df["CompletedAt"], errors="coerce")

    verified = df[df["Email"] != ""].copy()

    if verified.empty:
        return 0

    latest_verified = verified.sort_values("CompletedAt").groupby("Email", as_index=False).tail(1)
    latest_verified = latest_verified[latest_verified["Gender"] == gender]

    return len(latest_verified)


def get_verified_percentile(current_score, gender, csv_path=CSV_PATH):
    df = load_results(csv_path)

    if df.empty:
        return None

    df["Email"] = df["Email"].fillna("").astype(str).str.strip().str.lower()
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["CompletedAt"] = pd.to_datetime(df["CompletedAt"], errors="coerce")

    verified = df[df["Email"] != ""].copy()
    if verified.empty:
        return None

    latest_verified = verified.sort_values("CompletedAt").groupby("Email", as_index=False).tail(1)
    latest_verified = latest_verified[
        (latest_verified["Gender"] == gender) &
        (latest_verified["Score"].notna())
    ]

    if len(latest_verified) < 5:
        return None

    lower_count = (latest_verified["Score"] < current_score).sum()
    percentile = round((lower_count / len(latest_verified)) * 100)
    return percentile

    
def build_preheader(text: str) -> str:
    return f"""
    <div style="
        display:none;
        max-height:0;
        overflow:hidden;
        opacity:0;
        color:transparent;
        mso-hide:all;
        visibility:hidden;
    ">
        {text}
    </div>
    """

# Define the send-email function
def send_email(receiver_email, name, total_score, comparison_message=None, attempt_id=None):
    
    title, text, extra = get_interpretation(total_score)

    quiz_url = "https://your-app-url.streamlit.app"
    ##share_links = build_share_links(quiz_url, total_score)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = brevo_api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    subject = "Your Masculine/Feminine Thinking Quiz Result is Here!"
    tags = ["quiz-result", "streamlit-quiz"]

    if attempt_id:
        tags.append(f"attempt-{attempt_id}")

    preheader = "👀 did You expect this? This is interesting...                                                                      "
    
    html_content=f"""
    <html>
      <body>
        <div style="display:none!important;visibility:hidden;opacity:0;color:transparent;
        max-height:0;max-width:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;">
        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
        </div>

        <h2>Hi {name},</h2>

        {preheader}

        <p>Your score is: <strong>{total_score}</strong></p>
        <h3>{title}</h3>
        <p>{text}</p>
        <p>{extra}</p>
        {f"<p><strong>{comparison_message}</strong></p>" if comparison_message else ""}
        <h3>Want to understand yourself more? Get <strong><a href="https://your-app-url.streamlit.app/explore">the book this science based quiz is from</a></strong></h3>
        <p><strong><a href="https://your-app-url.streamlit.app/share">Share the quiz with friends</a></strong></p>
        <p>Were you surprised by your results? Let me know, I'd love to hear your thoughts</p>
        <p>Regards,</p>
        <p>Lacey</p>
      </body>
    </html>
    """
    text_content = f"""
Hi {name},

Your result is ready.

{title}
{text}
{extra}

{comparison_message if comparison_message else ""}

Explore more:
https://your-app-url.streamlit.app/explore

Share:
https://your-app-url.streamlit.app/share

Regards,
Lacey
    """.strip()

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": receiver_email, "name": name}],
        sender={"email": sender_email, "name": sender_name},
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        tags=tags,
        headers={
            "X-Quiz-Attempt-ID": str(attempt_id or ""),
            "X-Entity-Ref-ID": str(attempt_id or "")
        }
    )
    
    
    try:
        response = api_instance.send_transac_email(send_smtp_email)
        message_id = getattr(response, "message_id", "") or ""
        
        return True, {
            "message_id": message_id,
            "uuid": "",  # fill later from webhook or follow-up lookup
            "tags": ",".join(tags),
            "subject": subject,
            "status": "sent_to_brevo",
            "event": "api_accepted",
            "event_at": datetime.now().isoformat(timespec="seconds"),
            "reason": "",
            "webhook_email": receiver_email.strip().lower(),
            "webhook_id": str(attempt_id or "")
        }
            

    except ApiException as e:
        return False, str(e)


#Session Keys
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

if "total_score" not in st.session_state:
    st.session_state.total_score = None

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

if "result_saved" not in st.session_state:
    st.session_state.result_saved = False

if "attempt_id" not in st.session_state:
    st.session_state.attempt_id = str(uuid.uuid4())

# Collect answers
if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)

if None in st.session_state.answers:

    q_index = st.session_state.current_question
    q = questions[q_index]

    if q_index == 0:
        st.write("Answer the questions below to discover where you fall on the masculine-feminine spectrum.")

    st.subheader(f"Question {q_index+1} of {len(questions)}")

    previous_answer = st.session_state.answers[q_index]

    answer = st.radio(
        q["question"],
        q["options"],
        index=None if previous_answer is None else q["options"].index(previous_answer),
        key=f"q_{q_index}"
    )
    #Save Current Selection
    if answer is not None:
    #and answer != previous_answer:
        st.session_state.answers[q_index] = answer
    
    #Auto-advance only when answering a previously unanswered question
    if previous_answer is None and answer is not None:
        if q_index < len(questions) - 1:
            st.session_state.current_question += 1
        st.rerun()

    #Progress Bar
    progress = sum(a is not None for a in st.session_state.answers) / len(questions)
    st.progress(progress)

    #Navigation Buttons
    col1, col2 = st.columns(2)

    with col1:
        if q_index > 0:
            if st.button("Back"):
                st.session_state.current_question -= 1
                st.rerun()

    with col2:
        if previous_answer is not None and q_index < len(questions) - 1:
            if st.button("Continue"):
                st.session_state.current_question += 1
                st.rerun()

else:

    if not st.session_state.quiz_completed:
        total_score = calculate_score(
            st.session_state.answers,
            questions,
            a_value,
            b_value,
            c_value
        )
        st.session_state.total_score = total_score
        st.session_state.quiz_completed = True

        # Save result immediately even if no email is given
        if not st.session_state.result_saved:
            save_attempt(
                attempt_id=st.session_state.attempt_id,
                name="",
                email="",
                gender=gender,
                score=total_score
            )
            st.session_state.result_saved = True

    total_score = st.session_state.total_score

    # Show result immediately on the same page

    verified_pool_count = get_verified_pool_count(gender)

    # TEMP MODE: force email before showing results
    if REQUIRE_EMAIL_FOR_RESULTS and not st.session_state.email_sent:
        st.success("Quiz complete!")
        st.subheader("Enter your email to unlock your results")

        st.write("Your full result will be sent to your email")

        with st.form("required_email_form"):
            name = st.text_input("First name")
            email = st.text_input("Email")
            submit = st.form_submit_button("Email me my result")

            if submit:
                if not name and not email:
                    st.error("Please type your name and email.")
                elif not name:
                    st.error("Please type your name.")
                elif not email:
                    st.error("Please type your email.")
                else:
                    comparison_message = None

                    # Keep your comparison logic alive in the background
                    if verified_pool_count >= 5:
                        percentile = get_verified_percentile(total_score, gender)
                        if percentile is not None:
                            if gender == "Female":
                                comparison_message = f"Your score is higher than {percentile}% of verified women who took this quiz."
                            else:
                                comparison_message = f"Your score is higher than {percentile}% of verified men who took this quiz."

                    success, result = send_email(
                        email,
                        name,
                        total_score,
                        comparison_message,
                        attempt_id=st.session_state.attempt_id
                    )

                    if success:
                        st.session_state.email_sent = True

                        save_attempt(
                            attempt_id=st.session_state.attempt_id,
                            name=name,
                            email=email,
                            gender=gender,
                            score=total_score,
                            brevo_message_id=result.get("message_id", ""),
                            brevo_uuid=result.get("uuid", ""),
                            brevo_tags=result.get("tags", ""),
                            brevo_subject=result.get("subject", ""),
                            brevo_status=result.get("status", ""),
                            brevo_event=result.get("event", ""),
                            brevo_event_at=result.get("event_at", ""),
                            brevo_reason=result.get("reason", ""),
                            brevo_webhook_email=result.get("webhook_email", ""),
                            brevo_webhook_id=result.get("webhook_id", "")
                        )

                        st.rerun()
                    else:
                        st.error(f"Email failed: {result}")

    else:
        # OLD / NORMAL MODE
        if not REQUIRE_EMAIL_FOR_RESULTS:
            render_results(total_score, gender)

            st.markdown("---")

            if verified_pool_count >= 5:
                st.markdown("### Enter your email to see how you compare with others")
                submit_label = "Show my comparison"
            else:
                st.markdown("### Enter your email for posterity")
                submit_label = "Send me my result"

            if st.session_state.email_sent:
                st.success("Your results have already been sent to your email.")
            else:
                with st.form("optional_email_form"):
                    name = st.text_input("First name")
                    email = st.text_input("Email")
                    submit = st.form_submit_button(submit_label)

                    if submit:
                        if not name and not email:
                            st.error("Please type your name and email.")
                        elif not name:
                            st.error("Please type your name.")
                        elif not email:
                            st.error("Please type your email.")
                        else:
                            comparison_message = None

                            if verified_pool_count >= 5:
                                percentile = get_verified_percentile(total_score, gender)
                                if percentile is not None:
                                    if gender == "Female":
                                        comparison_message = f"Your score is higher than {percentile}% of verified women who took this quiz."
                                    else:
                                        comparison_message = f"Your score is higher than {percentile}% of verified men who took this quiz."

                            success, result = send_email(
                                email,
                                name,
                                total_score,
                                comparison_message,
                                attempt_id=st.session_state.attempt_id
                            )

                            if success:
                                st.session_state.email_sent = True

                                save_attempt(
                                    attempt_id=st.session_state.attempt_id,
                                    name=name,
                                    email=email,
                                    gender=gender,
                                    score=total_score,
                                    brevo_message_id=result.get("message_id", ""),
                                    brevo_uuid=result.get("uuid", ""),
                                    brevo_tags=result.get("tags", ""),
                                    brevo_subject=result.get("subject", ""),
                                    brevo_status=result.get("status", ""),
                                    brevo_event=result.get("event", ""),
                                    brevo_event_at=result.get("event_at", ""),
                                    brevo_reason=result.get("reason", ""),
                                    brevo_webhook_email=result.get("webhook_email", ""),
                                    brevo_webhook_id=result.get("webhook_id", "")
                                )

                                if comparison_message:
                                    st.success("Your result and comparison have been sent to your email.")
                                else:
                                    st.success("Your result has been sent to your email! Check spam/promotions if you don't see it.")

                                    st.markdown("---")
                                if st.button("Retake Quiz"):
                                    reset_quiz()
                                    st.rerun()

                            else:
                                st.error(f"Email failed: {result}")

        else:
            # Email was sent successfully in required-email mode, now show the result
            st.success("Your result has been sent to your email! Check spam/promotions if you don't see it.")
            st.markdown("---")
            if st.button("Retake Quiz"):
                reset_quiz()
                st.rerun()

                    
def update_attempt_from_webhook(
    attempt_id="",
    message_id="",
    event="",
    status="",
    event_at="",
    reason="",
    webhook_email="",
    webhook_id="",
    brevo_uuid="",
    csv_path=CSV_PATH
):
    df = load_results(csv_path)

    row_index = None

    if attempt_id:
        matches = df.index[df["AttemptID"].astype(str) == str(attempt_id)]
        if len(matches) > 0:
            row_index = matches[0]

    if row_index is None and message_id:
        matches = df.index[df["BrevoMessageID"].astype(str) == str(message_id)]
        if len(matches) > 0:
            row_index = matches[0]

    if row_index is None:
        return False

    if event:
        df.at[row_index, "BrevoEvent"] = event
    if status:
        df.at[row_index, "BrevoStatus"] = status
    if event_at:
        df.at[row_index, "BrevoEventAt"] = event_at
    if reason:
        df.at[row_index, "BrevoReason"] = reason
    if webhook_email:
        df.at[row_index, "BrevoWebhookEmail"] = webhook_email
    if webhook_id:
        df.at[row_index, "BrevoWebhookID"] = webhook_id
    if brevo_uuid:
        df.at[row_index, "BrevoUUID"] = brevo_uuid

    df.to_csv(csv_path, index=False)
    return True

               
#Marketing The Book
st.markdown("Get **[the science-based book](https://amzn.to/4cuanIh)** behind this quiz")
