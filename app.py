import streamlit as st
from google import genai
from google.genai import types

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkillSense AI – Skill Assessment Agent",
    page_icon="🎯",
    layout="centered"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    h1 { color: #1a1a2e; font-size: 2rem; }
    .subtitle { color: #555; font-size: 1rem; margin-top: -10px; margin-bottom: 20px; }
    .status-box {
        background: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: #3730a3;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 SkillSense AI")
st.markdown('<p class="subtitle">AI-Powered Skill Assessment & Personalised Learning Plan Agent</p>', unsafe_allow_html=True)
st.divider()

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are SkillSense AI, an expert career coach and skill assessment agent.

Your job is to:
1. Accept a Job Description (JD) and a candidate's Resume from the user
2. Extract the key required skills from the JD
3. Conversationally assess the candidate's REAL proficiency on each skill — ask 2-3 targeted questions per skill, not just "rate yourself"
4. Identify skill gaps based on their answers
5. Generate a detailed, personalised learning plan with curated free resources and realistic time estimates

CONVERSATION FLOW — follow this strictly:
- STAGE 1: Greet the user warmly and ask them to paste the Job Description
- STAGE 2: After JD received, ask them to paste their Resume
- STAGE 3: Confirm the skills you have extracted from the JD. List them clearly. Tell the user you will now assess each one.
- STAGE 4: Assess skills one by one. Ask 2-3 real questions per skill (not self-ratings). Be conversational, encouraging, and professional.
- STAGE 5: After all skills assessed, show the Gap Analysis in a clear table format
- STAGE 6: Generate the Personalised Learning Plan with specific free resources, time estimates per skill, and priority order
- STAGE 7: Ask for their email to send the report

ASSESSMENT RULES:
- Ask real questions like "Can you walk me through how you would write a VLOOKUP?" not "Rate yourself 1-5"
- Be encouraging and conversational — this is a coaching session, not an exam
- Score each skill internally: Strong (4-5/5), Developing (2-3/5), Gap (1/5)
- Focus on adjacent skills — what can this person REALISTICALLY learn given what they already know?

LEARNING PLAN FORMAT:
For each gap skill, provide:
- Priority level (High/Medium/Low)
- Estimated time to reach job-ready level
- 2-3 specific free resources (YouTube channels, Coursera free courses, documentation, etc.)
- A practical first step they can take TODAY

OUTPUT STYLE:
- Use emojis sparingly but effectively
- Use markdown tables for gap analysis
- Be warm, encouraging, and specific
- Always use the candidate's name if they mention it
- Keep responses focused — do not overwhelm with text"""

# ── Gemini client ─────────────────────────────────────────────────────────────
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stage = "start"
    st.session_state.greeted = False

# ── Auto-greeting (static — no API call) ─────────────────────────────────────
if not st.session_state.greeted:
    greeting = "👋 Welcome to **SkillSense AI**! I'm here to assess your skills and build you a personalised learning plan.\n\nTo get started, please **paste the Job Description** you're targeting below."
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.greeted = True

# ── Status indicator ──────────────────────────────────────────────────────────
stage_labels = {
    "start": "📋 Waiting for Job Description",
    "jd_received": "📄 Waiting for Resume",
    "resume_received": "🔍 Extracting Skills...",
    "assessing": "💬 Assessment in Progress",
    "complete": "✅ Assessment Complete"
}
current_label = stage_labels.get(st.session_state.stage, "💬 In Progress")
st.markdown(f'<div class="status-box">{current_label}</div>', unsafe_allow_html=True)

# ── Display chat history ──────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🎯" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your response here..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Update stage
    if st.session_state.stage == "start" and len(prompt) > 100:
        st.session_state.stage = "jd_received"
    elif st.session_state.stage == "jd_received" and len(prompt) > 100:
        st.session_state.stage = "resume_received"
    elif st.session_state.stage in ["resume_received", "assessing"]:
        st.session_state.stage = "assessing"

    # Build conversation history for Gemini
    history = []
    for m in st.session_state.messages[:-1]:  # exclude latest user message
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [{"text": m["content"]}]})

    # Call Gemini API
    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash-lite",
                    contents=history + [{"role": "user", "parts": [{"text": prompt}]}],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=2048,
                        temperature=0.7,
                    )
                )
                reply = response.text
                st.markdown(reply)
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"
                st.warning(reply)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Check if complete
    if any(phrase in reply.lower() for phrase in ["learning plan", "personalised plan", "your email"]):
        st.session_state.stage = "complete"

    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📌 How it works")
    st.markdown("""
1. **Paste your Job Description**
2. **Paste your Resume**
3. **Answer assessment questions**
4. **Get your Gap Analysis**
5. **Receive your Learning Plan**
    """)
    st.divider()
    st.markdown("### 💡 Tips")
    st.markdown("""
- Be honest in your answers — the more accurate, the better your learning plan
- Answer in detail — don't just say yes/no
- Mention specific tools and projects you have worked on
    """)
    st.divider()
    if st.button("🔄 Start Over"):
        st.session_state.messages = []
        st.session_state.greeted = False
        st.session_state.stage = "start"
        st.rerun()
    st.divider()
    st.caption("Built for Deccan AI Catalyst Hackathon 2026")
    st.caption("By Bhuvaneshwari Vijay Raghavan")
