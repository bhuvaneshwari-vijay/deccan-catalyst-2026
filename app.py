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
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        text-align: center;
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
- STAGE 1: The user's FIRST message will always be the Job Description. Do NOT ask for it again. Simply say "Got it! I have reviewed the Job Description. Now please paste your Resume so I can compare your profile against the role requirements."
- STAGE 2: The user's SECOND message will always be their Resume. After receiving it, extract the key skills from the JD and say "Perfect! Based on the Job Description, here are the key skills I will assess: [list skills]. Let us begin the assessment!"
- STAGE 3: Assess skills one by one. Ask 2-3 real questions per skill (not self-ratings). Be conversational, encouraging, and professional.
- STAGE 4: After all skills assessed, show the Gap Analysis using this exact format — no markdown tables:

SKILL GAP ANALYSIS:
• [Skill] — [Level] ([score]/5) [emoji]

Use the word Strong for 4-5/5, Developing for 2-3/5, Gap for 1/5

- STAGE 5: Immediately in the SAME message after the gap analysis, show the full Personalised Learning Plan using this format:

PERSONALISED LEARNING PLAN:

[Skill Name] — Priority: [High/Medium/Low]
• Time to job-ready: [X weeks]
• Resource 1: [specific free resource with URL if possible]
• Resource 2: [specific free resource]
• First step TODAY: [one concrete action]

- STAGE 6: After the learning plan, say exactly this one sentence: "Please share your email address and I will send you this complete report!" — nothing else.
- STAGE 7: Once they provide their email, say exactly this: "Your personalised assessment report has been sent! Best of luck with your application!" — then stop completely. Do not say anything else.

IMPORTANT RULES:
- The first user message IS the Job Description — never ask for it again
- The second user message IS the Resume — never ask for it again
- Always show gap analysis AND learning plan in the SAME message — never split them
- Keep learning plan concise — maximum 3 resources per skill
- DO NOT use markdown tables anywhere
- DO NOT use ** or * or any markdown bold formatting at all
- Use plain bullet points (•) only
- No asterisks anywhere in your response
- Ask real assessment questions not self-rating questions
- Be encouraging and warm throughout
- Use the candidate's name if they mention it
- Score each skill: Strong (4-5/5), Developing (2-3/5), Gap (1/5)
- Focus on adjacent skills the candidate can realistically learn
- Write everything in clean plain text suitable for email"""

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
    st.session_state.email_sent = False

# ── Auto-greeting (static — no API call) ─────────────────────────────────────
if not st.session_state.greeted:
    greeting = "👋 Hi there! Welcome to **SkillSense AI**!\n\nI'm your personal career coach — I'll assess your skills against a Job Description and build you a personalised learning plan.\n\n**Ready to get started? Paste the Job Description below!** 🚀"
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.greeted = True

# ── Status indicator ──────────────────────────────────────────────────────────
stage_labels = {
    "start": "📋 Paste your Job Description below to begin",
    "jd_received": "📄 Great! Now paste your Resume",
    "resume_received": "🔍 Assessing your skills...",
    "assessing": "💬 Assessment in Progress",
    "complete": "✅ Assessment Complete — check your email!",
    "done": "📧 Report Sent Successfully!"
}
current_label = stage_labels.get(st.session_state.stage, "💬 In Progress")
st.markdown(f'<div class="status-box">{current_label}</div>', unsafe_allow_html=True)

# ── Show completion screen if done ───────────────────────────────────────────
if st.session_state.stage == "done":
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Your Assessment is Complete!</h3>
        <p>Your personalised learning plan has been sent to your email.</p>
        <p>Check your inbox — it should arrive within a few seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            st.session_state.messages = []
            st.session_state.greeted = False
            st.session_state.stage = "start"
            st.session_state.email_sent = False
            st.rerun()
    with col2:
        if st.button("💬 Continue Chatting", use_container_width=True):
            st.session_state.stage = "complete"
            st.rerun()
    st.stop()

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

    # Update stage based on message count
    user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    if len(user_messages) == 1:
        st.session_state.stage = "jd_received"
    elif len(user_messages) == 2:
        st.session_state.stage = "resume_received"
    elif len(user_messages) > 2 and st.session_state.stage not in ["complete", "done"]:
        st.session_state.stage = "assessing"

    # Send email via n8n webhook if user provided email
    if st.session_state.stage in ["complete", "assessing"] and "@" in prompt and "." in prompt and not st.session_state.email_sent:
        learning_plan_raw = next(
            (m["content"] for m in reversed(st.session_state.messages)
             if "SKILL GAP ANALYSIS" in m.get("content", "")), ""
        )
        learning_plan = learning_plan_raw.split("Please share your email")[0].strip()
        learning_plan = learning_plan.split("Would you like me to send")[0].strip()
        try:
            requests.post(
                "https://bhuvana-vijay.app.n8n.cloud/webhook/skillsense",
                json={
                    "email": prompt,
                    "report": learning_plan,
                    "name": "SkillSense AI Assessment Report"
                },
                timeout=5
            )
            st.session_state.email_sent = True
        except Exception:
            pass

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

    # Check if assessment complete
    if "please share your email" in reply.lower():
        st.session_state.stage = "complete"

    # Move to done stage after email confirmed sent
    if st.session_state.email_sent and "best of luck" in reply.lower():
        st.session_state.stage = "done"

    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📌 How it works")
    st.markdown("""
1. **Paste your Job Description**
2. **Paste your Resume**
3. **Answer assessment questions**
4. **Get your Gap Analysis**
5. **Receive your Learning Plan by email**
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
        st.session_state.email_sent = False
        st.rerun()
    st.divider()
    st.caption("Built for Deccan AI Catalyst Hackathon 2026")
    st.caption("By Bhuvaneshwari Vijay Raghavan")



