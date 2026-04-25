# SkillSense AI — One-Page Write-Up
**Deccan AI Catalyst Hackathon 2026 | Bhuvaneshwari Vijay Raghavan**

---

## The Problem

A resume tells you what someone claims to know - not how well they actually know it. Candidates apply to roles with mismatched skills, recruiters spend hours screening and skill gaps are discovered too late in the process. There is no scalable, personalised way for candidates to understand exactly where they stand against a specific Job Description - and what to do about it.

## My Approach

I built SkillSense AI as a conversational skill assessment agent. Rather than asking candidates to self-rate their skills (which is unreliable), the agent extracts required skills dynamically from any Job Description, then probes real proficiency through targeted follow-up questions - the way a skilled interviewer would.

The key insight driving my design: the quality of an assessment depends on the quality of the questions, not the format. So I invested heavily in prompt engineering to make the agent ask genuinely diagnostic questions rather than surface-level ones.

The agent follows a structured 7-stage flow: receive JD → receive Resume → extract skills → assess each skill conversationally → generate gap analysis → generate learning plan → deliver report by email. Each stage is tracked in session state so the user always knows where they are.

## Architecture

The stack is entirely free-tier and deployable by anyone:

- Streamlit handles the chat UI and session management. It was chosen for its native chat components, zero-config deployment and free hosting via Streamlit Community Cloud.
- OpenRouter provides AI inference with automatic free model routing. Rather than locking into one model, OpenRouter selects the best available free model per request — making the app resilient to individual model rate limits.
- n8n handles email automation via a webhook-triggered workflow connected to Gmail. When the user provides their email, the app posts the report to the n8n webhook, which formats and delivers it within seconds.
- GitHub hosts the public codebase, connected directly to Streamlit for continuous deployment.

## Key Design Decisions

**Conversational assessment over forms:** Self-rating forms are fast but unreliable. Conversational assessment takes longer but produces accurate, trustworthy results. The trade-off is session length - a full assessment takes 10-15 minutes. For a career tool, that is acceptable.

**Dynamic skill extraction:** Skills are extracted from the JD by the AI at runtime - nothing is hardcoded. This means SkillSense works for any role, any industry, any seniority level without modification.

**OpenRouter auto-routing:** Using a fixed model risks hitting rate limits during judge evaluation. Auto-routing eliminates this risk by falling back to alternative free models automatically.

**Email delivery via webhook:** Rather than building a backend email service, I used n8n as a no-code automation layer. This keeps the architecture simple, auditable and extensible — the webhook can be connected to Slack, Notion or any other tool with no code changes.

## Trade-offs and Limitations

- Free model quality varies — OpenRouter's auto-routing sometimes selects less capable models, which can affect response quality. A paid model would produce more consistent results.
- Session state is not persisted — if the user closes the browser mid-assessment, progress is lost. A database layer would solve this.
- Email formatting is plain text — HTML email would look more polished but adds complexity.
- The agent currently supports text input only — resume PDF upload would improve usability.

## What I Would Build Next

- Resume PDF upload and parsing
- Employer-facing dashboard to review candidate assessments
- Progress tracking — retake the assessment after upskilling to measure improvement
- Integration with LinkedIn to auto-populate resume data

---

*SkillSense AI — turning job descriptions into personalised career roadmaps.*
