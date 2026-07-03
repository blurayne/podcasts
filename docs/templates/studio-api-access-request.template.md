# Template — ElevenLabs Studio API access request

Reusable template for requesting Studio API whitelisting. Replace every
`{{PLACEHOLDER}}`, delete this header block, and send.

**Send to:** ElevenLabs sales/support — `sales@elevenlabs.io`, via
<https://elevenlabs.io/contact-sales>, or the in-app support chat.

Placeholders:
- `{{ACCOUNT}}` — ElevenLabs account email / workspace name holding the API key
- `{{PLAN}}` — current subscription tier (e.g. Creator)
- `{{USE_CASE}}` — one sentence on what you're building via `POST /v1/studio/projects`
- `{{REQUEST_IDS}}` — request_id value(s) from your 403 responses (optional but speeds lookup)
- `{{NAME}}` — your name

---

**Subject:** Request to whitelist my account for the Studio API (`invalid_subscription`)

Hello ElevenLabs team,

I'd like to request access to the **Studio API** for my account.

- **Account:** {{ACCOUNT}}
- **Current plan:** {{PLAN}}
- **What I'm trying to do:** {{USE_CASE}} — creating Studio projects
  programmatically via `POST /v1/studio/projects` (importing long-form scripts as
  chapterised projects, assigning voices per speaker, then converting). I already
  use the public Text-to-Speech, Sound Effects and Music APIs successfully; only
  Studio is gated.

When I call the Studio endpoints I get **HTTP 403** with:

> `"code": "invalid_subscription"` —
> "Access to the Studio API requires your account to be explicitly whitelisted to
> use it. Please contact our sales team."

Request ID(s) from the denied calls, for reference: {{REQUEST_IDS}}

Could you let me know:

1. What's required to enable Studio API access on my account (whitelisting, a
   specific plan/tier, or an enterprise agreement)?
2. Any usage terms or limits I should be aware of once enabled.

Happy to provide any further details. Thank you!

Best regards,
{{NAME}}

---

### Example (this project's filled values)

- `{{ACCOUNT}}` → *your ElevenLabs account email / workspace*
- `{{PLAN}}` → Creator
- `{{USE_CASE}}` → producing German audio dramas, audiobooks and a documentary-feature podcast
- `{{REQUEST_IDS}}` → `04b76f48c60369f7644b2ed63b79164b`, `52c92830be9eccd3f00163c9c76e936c`
- `{{NAME}}` → *your name*
