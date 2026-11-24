import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --------------------------------------------------
# 1. BASIC CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Professional Message Writer",
    page_icon="✉️",
    layout="centered",
)

MODEL_NAME = "gemini-3.5-flash-lite"

MESSAGE_TYPES = [
    "Job application",
    "Referral request",
    "Interview follow-up",
    "Internship request",
    "Thank-you after interview",
]


# --------------------------------------------------
# 2. CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 850px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.5rem 1.6rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 18px;
        margin-bottom: 1.4rem;
    }

    .hero h1 {
        margin: 0 0 .35rem 0;
        font-size: 2rem;
    }

    .muted {
        color: #777;
        font-size: .95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>✉️ AI Professional Message Writer</h1>
        <div class="muted">
            Create clear, confident and professional emails
            or LinkedIn messages in seconds.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 4. GET GEMINI API KEY
# --------------------------------------------------

def get_api_key():
    """Read the API key from Streamlit secrets or .env."""

    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""

    return secret_key or os.getenv("GEMINI_API_KEY", "")


# --------------------------------------------------
# 5. BUILD PROMPT
# --------------------------------------------------

def build_prompt(
    message_type,
    recipient,
    key_points,
    platform,
    regenerate=False,
    previous_message="",
    retry_note="",
):

    if platform == "Email":
        output_rules = """
Return a complete professional email.

Use this format:

Subject: A concise and relevant subject line

Email body

Write approximately 100–140 words.

Include:
- A suitable greeting.
- A clear opening sentence.
- All important points supplied by the user.
- A polite closing sentence.
- A professional sign-off with [Your Name].

Never stop halfway through a sentence.
Do not invent qualifications, experience, dates,
company details or facts.
"""
    else:
        output_rules = """
Return only one LinkedIn message.

It MUST contain fewer than 300 characters,
including spaces.

Do not include:
- A subject line.
- An explanation.
- Quotation marks.
- Unnecessary headings.

Keep the message professional and natural.
Do not invent facts.
"""

    variation_instruction = ""

    if regenerate:
        variation_instruction = f"""
IMPORTANT: Generate a genuinely NEW alternative.

Use different sentence structures and wording.
Keep the same meaning and important details.
Do not copy the previous message.

PREVIOUS MESSAGE:
{previous_message}

Make this alternative noticeably different.
"""

    return f"""
You are an expert professional career communication assistant.

Create a polished message using the following information.

Message type: {message_type}

Recipient: {recipient}

Important points:
{key_points}

{variation_instruction}

{retry_note}

{output_rules}
"""


# --------------------------------------------------
# 6. GENERATE MESSAGE USING GEMINI
# --------------------------------------------------

def generate_message(
    message_type,
    recipient,
    key_points,
    platform,
    regenerate=False,
    previous_message="",
):

    api_key = get_api_key()

    if not api_key:
        st.error(
            "Gemini API key not found. Add GEMINI_API_KEY "
            "to Streamlit secrets or your local .env file."
        )
        return None

    client = genai.Client(api_key=api_key)
    retry_note = ""

    for attempt in range(3):
        prompt = build_prompt(
            message_type,
            recipient,
            key_points,
            platform,
            regenerate,
            previous_message,
            retry_note,
        )

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    max_output_tokens=1200,
                ),
            )

            result = (response.text or "").strip()

            if not result:
                retry_note = "The previous response was empty. Try again."
                continue

            if platform == "LinkedIn":
                result = result.strip().strip('"').strip()

                if len(result) >= 300:
                    retry_note = (
                        "Your previous response was too long. "
                        "Write a shorter message under 300 characters."
                    )
                    continue

            if platform == "Email":
                word_count = len(result.split())

                valid_closing = any(
                    word in result.lower()
                    for word in ["regards", "sincerely", "thank you", "best"]
                )

                if word_count < 80 or not valid_closing:
                    retry_note = (
                        "The previous email was incomplete. "
                        "Write a complete professional email."
                    )
                    continue

            if regenerate and previous_message:
                if result.casefold() == previous_message.strip().casefold():
                    retry_note = (
                        "Your previous attempt repeated the old message. "
                        "Create a substantially different alternative."
                    )
                    continue

            return result

        except Exception as error:
            error_text = str(error).upper()

            temporary_error = (
                "503" in error_text
                or "429" in error_text
                or "UNAVAILABLE" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )

            if temporary_error and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue

            st.error(
                "Gemini could not generate the message. "
                f"Technical detail: {error}"
            )
            return None

    if regenerate:
        st.warning(
            "Gemini could not produce a sufficiently different version "
            "after three attempts. Your previous message has been kept."
        )
    else:
        st.warning(
            "Could not generate a valid message after three attempts. "
            "Please try again."
        )

    return None


# --------------------------------------------------
# 7. MESSAGE INPUT FORM
# --------------------------------------------------

with st.form("message_form"):
    st.subheader("1. Enter your message details")

    message_type = st.selectbox(
        "Message type",
        MESSAGE_TYPES,
    )

    recipient = st.text_input(
        "Who is the message for?",
        placeholder="Example: HR Manager at ABC Technologies",
    )

    key_points = st.text_area(
        "What should the message include?",
        placeholder=(
            "Enter 2–3 important points.\n"
            "Example: I am a computer science student; "
            "I know Python and SQL; I am interested in a data analyst role."
        ),
        height=130,
        max_chars=1200,
    )

    platform = st.radio(
        "Choose platform",
        ["Email", "LinkedIn"],
        horizontal=True,
    )

    submitted = st.form_submit_button(
        "✨ Generate message",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# 8. HANDLE FORM SUBMISSION
# --------------------------------------------------

if submitted:
    if not recipient.strip():
        st.warning("Please enter who the message is for.")

    elif not key_points.strip():
        st.warning("Please enter 2–3 key points for the message.")

    else:
        st.session_state["last_message_type"] = message_type
        st.session_state["last_recipient"] = recipient.strip()
        st.session_state["last_key_points"] = key_points.strip()
        st.session_state["last_platform"] = platform

        st.session_state.pop("generated_message", None)
        st.session_state.pop("generated_platform", None)

        with st.spinner("Gemini is writing your professional message..."):
            generated = generate_message(
                message_type,
                recipient.strip(),
                key_points.strip(),
                platform,
            )

        if generated:
            st.session_state["generated_message"] = generated
            st.session_state["generated_platform"] = platform
            st.session_state["output_version"] = (
                st.session_state.get("output_version", 0) + 1
            )


# --------------------------------------------------
# 9. DISPLAY GENERATED MESSAGE
# --------------------------------------------------

if "generated_message" in st.session_state:
    st.divider()
    st.subheader("2. Your generated message")

    output = st.session_state["generated_message"]
    output_platform = st.session_state["generated_platform"]

    if output_platform == "LinkedIn":
        st.caption(f"Character count: {len(output)} / 299")

        if len(output) < 300:
            st.success("Within the assignment's 300-character limit.")
        else:
            st.warning("This version is over the 300-character limit.")

    st.text_area(
        "Generated content",
        value=output,
        height=230 if output_platform == "Email" else 150,
        key=f"output_box_{st.session_state.get('output_version', 0)}",
    )

    st.download_button(
        "⬇️ Download message as TXT",
        data=output,
        file_name="professional_message.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # --------------------------------------------------
    # 10. REGENERATE ANOTHER VERSION
    # --------------------------------------------------

    if st.button(
        "🔄 Regenerate another version",
        use_container_width=True,
    ):
        previous_message = st.session_state["generated_message"]

        with st.spinner("Generating a fresh version..."):
            generated = generate_message(
                st.session_state["last_message_type"],
                st.session_state["last_recipient"],
                st.session_state["last_key_points"],
                st.session_state["last_platform"],
                regenerate=True,
                previous_message=previous_message,
            )

        if generated:
            st.session_state["generated_message"] = generated
            st.session_state["generated_platform"] = (
                st.session_state["last_platform"]
            )
            st.session_state["output_version"] = (
                st.session_state.get("output_version", 0) + 1
            )
            st.rerun()


# --------------------------------------------------
# 11. FOOTER
# --------------------------------------------------

st.divider()
st.caption("Built with Python • Streamlit • Google Gemini API")
