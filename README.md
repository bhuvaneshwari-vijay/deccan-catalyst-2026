# 🎯 SkillSense AI - Deccan AI Catalyst Hackathon 2026

> **An AI agent that reads a Job Description and a candidate's Resume, conversationally assesses real skill proficiency, identifies gaps and delivers a personalised learning plan - straight to your inbox.**

---

## 📌 Problem Statement

A resume tells you what someone *claims* to know — not how well they actually know it. Recruiters and candidates both lose time on mismatched applications. SkillSense AI bridges this gap by acting as an intelligent career coach that goes beyond self-ratings to assess real proficiency through conversation.

**Business Impact:**
- Without agent: Candidates apply blindly, recruiters screen manually, skill gaps discovered too late
- With agent: Real proficiency assessed in minutes, personalised upskilling plan delivered instantly, better job-fit from day one

---

## 🧠 Solution Overview

SkillSense AI is a conversational skill assessment agent. Here is how it works:

1. Candidate pastes a Job Description
2. Candidate pastes their Resume
3. Agent extracts required skills from the JD dynamically
4. Agent assesses each skill through real targeted questions - not self-ratings
5. Agent generates a Gap Analysis and Personalised Learning Plan
6. Full report is delivered to the candidate's email automatically

**Agent Workflow:**
```
Job Description + Resume → Skill Extraction → Conversational Assessment → Gap Analysis → Learning Plan → Email Delivery
```

---

## 🏗️ Architecture

### Tech Stack

| Layer | Tool | Why chosen |
|---|---|---|
| Frontend + Chat UI | Streamlit | Fast deployment, built-in chat components, free hosting |
| AI Brain | OpenRouter (auto model selection) | Free tier, reliable, smart model routing |
| Email Delivery | n8n + Gmail | No-code automation, webhook-triggered, free tier |
| Deployment | Streamlit Community Cloud | Zero-config deployment, live URL instantly |
| Code Hosting | GitHub | Public repo, version control |

### Architecture Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  OpenRouter API  │────▶│  AI Response    │
│  (Chat Interface│     │  (Auto Model     │     │  (Gap Analysis  │
│   + Session     │     │   Selection)     │     │   + Learning    │
│   Management)   │     │                  │     │   Plan)         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                 │
         │ User provides email                             │
         ▼                                                 ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Webhook POST   │────▶│   n8n Workflow   │────▶│  Gmail Delivery │
│  (email +       │     │  (Automation     │     │  (Personalised  │
│   report)       │     │   Engine)        │     │   Report)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## ⚙️ Scoring & Assessment Logic

### How Skills are Extracted
The AI reads the Job Description and identifies all required technical and soft skills. This is dynamic - every JD produces a different skill list. No hardcoded skills.

### How Proficiency is Assessed
For each skill, the agent asks 2-3 real-world questions such as:
- "Walk me through a complex SQL query you have written — what business problem did it solve?"
- "How would you handle missing values in a dataset before building a model?"

These are evaluated by the AI against the candidate's answers and scored internally:

| Score | Level | Meaning |
|---|---|---|
| 4-5/5 | Strong ✅ | Job-ready, no action needed |
| 2-3/5 | Developing ⚠️ | Needs some upskilling |
| 1/5 | Gap ❌ | Priority area for learning |

### How the Learning Plan is Generated
For each gap or developing skill, the agent generates:
- Priority level (High / Medium / Low) based on how critical the skill is to the JD
- Realistic time estimate to reach job-ready level
- 2-3 specific free resources (Coursera, YouTube, documentation, etc.)
- One concrete action the candidate can take today

---

## 🚀 How to Run

### Prerequisites
- Streamlit Community Cloud account (free)
- OpenRouter account + API key (free)
- n8n Cloud account (free)
- Gmail account

### Setup Steps

**Step 1 — Clone the repo**
```
git clone https://github.com/bhuvaneshwari-vijay/deccan-catalyst-2026
```

**Step 2 — Deploy on Streamlit Cloud**
- Go to share.streamlit.io
- Connect your GitHub repo
- Set main file as app.py
- Add secrets: OPENROUTER_API_KEY = "your-key"

**Step 3 — Set up n8n webhook**
- Create n8n workflow with Webhook trigger + Gmail action
- Use production webhook URL in app.py
- Map email and report fields from webhook body

**Step 4 — Run**
- Visit your Streamlit app URL
- Paste a Job Description to begin

### Test It
Visit 👉 https://skillsense-catalyst-ai.streamlit.app

Sample inputs provided in the /sample-data folder.

---

## 📊 Demo

🎥 **Demo Video:** [Loom link — coming soon]

### Sample Input

**Job Description:** Data Analyst role at YipitData requiring SQL, Python, data accuracy, communication and problem-solving skills.

**Resume:** Data analytics professional with IIT Roorkee certification, Power BI, SQL, Python, SSRS experience and GenAI project work.

### Sample Output

```
SKILL GAP ANALYSIS:
• SQL — Strong (5/5) ✅
• Python — Strong (4/5) ✅
• Data Analysis & Accuracy — Strong (5/5) ✅
• Communication — Strong (5/5) ✅
• Investing & Reporting — Developing (3/5) ⚠️

PERSONALISED LEARNING PLAN:

Investing & Reporting — Priority: Medium
• Time to job-ready: 1-2 weeks
• Resource 1: Investopedia — How Institutional Investors Make Decisions
• Resource 2: Coursera — Financial Analysis and Decision Making (free audit)
• First step TODAY: Read one article on YipitData's blog about how they analyze companies
```

---

## 📈 Results & Impact

| Metric | Manual Process | SkillSense AI |
|---|---|---|
| Time to assess skills | 45-60 mins (interview) | 10-15 mins (conversational) |
| Personalised learning plan | Days (career counsellor) | Instant |
| Cost | ₹2000-5000 per session | Free |
| Scalability | 1 candidate at a time | Unlimited concurrent users |

---

## 🔧 Production Considerations

- **Error Handling:** API errors surface as user-friendly warning messages, not crashes
- **Scalability:** Stateless Streamlit architecture — each session is independent, scales horizontally
- **Security:** API keys stored in Streamlit secrets, never exposed in code
- **Cost:** Entire stack runs on free tiers — OpenRouter free model routing, n8n free tier, Streamlit free hosting
- **Rate Limits:** OpenRouter auto-routing selects available free models, reducing rate limit errors

---

## 🗂️ Repo Structure

```
deccan-catalyst-2026/
│
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── README.md               ← You are here
└── sample-data/
    ├── sample-jd.txt       ← Sample Job Description input
    └── sample-resume.txt   ← Sample Resume input
```

---

## 👩‍💻 About the Builder

**Bhuvaneshwari Vijay Raghavan**
BI Analyst | Data Analytics | GenAI Automation

- 🔗 [LinkedIn](https://www.linkedin.com/in/bhuvaneshwari-vijay-data-analyst)
- 💻 [GitHub](https://github.com/bhuvaneshwari-vijay)
- 🎓 Executive PG in Data Analytics — IIT Roorkee

*Built solo over 30 hours for Deccan AI Catalyst Hackathon, April 2026.*

---

## 📄 License

This project was built for the Deccan AI Catalyst Hackathon 2026. All rights reserved.
