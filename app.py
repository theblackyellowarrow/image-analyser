import streamlit as st
from PIL import Image
import tempfile
import os
from anthropic import Anthropic

# Page setup
st.set_page_config(page_title="📷 AI Visual Analyser", layout="wide")
st.markdown("""
    <h1 style='text-align: center; color: white;'>📷 AI Visual Analyser</h1>
    <p style='text-align: center; color: #a29bfe;'>Forked and developed by Rahul Bhattacharya as a part of dotai + theblackyellowarrow experiments to make AI contextual</p>
""", unsafe_allow_html=True)

# Upload
uploaded_image = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])
claude_api_key = st.secrets.get("ANTHROPIC_API_KEY")

def run_claude_analysis(image_path):
    client = Anthropic(api_key=claude_api_key)
    prompt = (
        "Please analyse the uploaded image under the following five categories:\n"
        "- Formalist Analysis\n"
        "- Iconographical Analysis\n"
        "- Iconological Analysis\n"
        "- Semiotic Analysis\n"
        "- Semantic Analysis\n"
        "Then write a critical summary. Use British English. Do not summarise the task. Speak like an art historian, not a chatbot."
    )

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    # Claude 3.5 image input
    response = client.messages.create(
        model="claude-3-5-haiku-20240307",
        max_tokens=1024,
        temperature=0.5,
        system="You are a visual culture theorist generating image-based art analysis in British English.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_bytes.encode("base64")}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )
    return response.content[0].text

# Run
if uploaded_image and claude_api_key:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Analyse Your Image"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image = Image.open(uploaded_image)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(tmp_file.name, format='JPEG')

            with st.spinner("Thinking deeply about the image..."):
                try:
                    result = run_claude_analysis(tmp_file.name)
                    st.markdown("### 📝 Claude's Visual Analysis")
                    st.markdown(result)
                finally:
                    os.remove(tmp_file.name)
else:
    if not uploaded_image:
        st.info("Upload an image to begin.")
    elif not claude_api_key:
        st.error("Missing `ANTHROPIC_API_KEY` in secrets.toml. Add it to deploy.")
