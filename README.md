# AI Professional Message Writer

A Streamlit application that uses Google's Gemini API to generate professional emails and LinkedIn messages.

## Features

- Generate job application emails
- Generate referral requests
- Generate interview follow-ups
- Generate internship requests
- Generate thank-you messages
- Generate LinkedIn messages under 300 characters
- Regenerate an alternative version
- Download generated messages as TXT
- Validate required input fields

## Tech stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- python-dotenv

## Run locally

1. Install Python.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment if desired.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the same folder as `app.py`:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

6. Start the app:

   ```bash
   python -m streamlit run app.py
   ```

7. Open the local URL shown in the terminal (usually http://localhost:8501).

## Deploy on Streamlit Community Cloud

1. Extract this ZIP.
2. Create a GitHub repository and upload the project files.
3. Do not upload `.env`, your API key, or your virtual environment.
4. Open https://share.streamlit.io/ and sign in with GitHub.
5. Select **Create app**, choose your repository and branch, and set the main file path to `app.py`.
6. Before deploying, open **Advanced settings** and add this secret:

   ```toml
   GEMINI_API_KEY = "paste_your_real_gemini_api_key_here"
   ```

7. Deploy the app and wait for the build to finish.

## Secrets and security

- Never commit `.env` or share your Gemini API key.
- For Streamlit Community Cloud, store the key in the app's **Settings → Secrets**.
- `.gitignore` excludes local secrets and virtual environments.

## Model configuration

The model name is set in `app.py` using `MODEL_NAME`. If the selected model is not available to your API key, change it to a currently supported Gemini model available in Google AI Studio.
