import streamlit as st
from openai import OpenAI
import requests

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
- STAGE 5: After all skills assessed, show the Gap Analysis using this exact format — no markdown tables:

SKILL GAP ANALYSIS:
• [Skill] — [Level] ([score]/5) [emoji]

Use ✅ for Strong (4-5/5), ⚠️ for Developing (2-3/5), ❌ for Gap (1/5)

- STAGE 6: Immediately in the SAME message after the gap analysis, show the full Personalised Learning Plan using this format:

PERSONALISED LEARNING PLAN:

[Skill Name] — Priority: [High/Medium/Low]
• Time to job-ready: [X weeks]
• Resource 1: [specific free resource with URL if possible]
• Resource 2: [specific free resource]
• First step TODAY: [one concrete action]

- STAGE 7: After the learning plan, ask for their email to send the report

IMPORTANT RULES:
- Always show gap analysis AND learning plan in the SAME message — never split them
- Keep learning plan concise — maximum 3 resources per skill
- DO NOT use markdown tables anywhere
- Ask real assessment questions like "walk me through how you would write a window function" not "rate yourself 1-5"
- Be encouraging and warm throughout
- Use the candidate's name if they mention it
- Score each skill: Strong (4-5/5), Developing (2-3/5), Gap (1/5)
- Focus on adjacent skills the candidate can realistically learn"""

# ── OpenRouter client ─────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

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

    # Build messages for API
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call OpenRouter API
    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="openrouter/auto",
                    max_tokens=3000,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + api_messages
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"
                st.warning(reply)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Check if complete
    if any(phrase in reply.lower() for phrase in ["learning plan", "personalised learning", "email"]):
        st.session_state.stage = "complete"

    # Send email via Zapier if user just provided their email
    if st.session_state.stage == "complete" and "@" in prompt:
        learning_plan = next(
            (m["content"] for m in reversed(st.session_state.messages)
             if "SKILL GAP ANALYSIS" in m.get("content", "")), ""
        )
        try:
            requests.post(
                "https://hooks.zapier.com/hooks/catch/25722379/uvbe3lb/",
                json={
                    "email": prompt,
                    "report": learning_plan,
                    "name": "SkillSense AI Assessment Report"
                }
            )
        except:
            pass

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
