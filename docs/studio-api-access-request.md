# ElevenLabs Studio API — access request (draft)

**Send to:** ElevenLabs sales/support — `sales@elevenlabs.io` (or via
<https://elevenlabs.io/contact-sales>, or the in-app support chat).

**Fill in before sending:** the email address / workspace name of your
ElevenLabs account (the one holding the API key).

---

**Subject:** Request to whitelist my account for the Studio API (`invalid_subscription`)

Hello ElevenLabs team,

I'd like to request access to the **Studio API** for my account.

- **Account:** `<your ElevenLabs account email / workspace name>`
- **Current plan:** Creator
- **What I'm trying to do:** create Studio projects programmatically via
  `POST /v1/studio/projects` — importing long-form German scripts (audio dramas,
  audiobooks, and a documentary-feature podcast) as chapterised Studio projects,
  then assigning voices per speaker and converting. I already use the public
  Text-to-Speech, Sound Effects and Music APIs successfully; only Studio is gated.

When I call the Studio endpoints I get **HTTP 403** with:

> `"code": "invalid_subscription"` —
> "Access to the Studio API requires your account to be explicitly whitelisted to
> use it. Please contact our sales team."

For reference, two request IDs from those denied calls:

- `04b76f48c60369f7644b2ed63b79164b`
- `52c92830be9eccd3f00163c9c76e936c`

Could you let me know:

1. What's required to enable Studio API access on my account (whitelisting, a
   specific plan/tier, or an enterprise agreement)?
2. Any usage terms or limits I should be aware of once enabled.

Happy to provide any further details. Thank you!

Best regards,
`<your name>`
