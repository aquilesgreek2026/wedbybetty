# Wed by Betty — Social Media Content Agent Plan

**Goal:** Bring wedding clients to Betty (bilingual officiant: ceremony + marriage license handling + court filing, Oceanside / North County / San Diego County) by publishing consistent, high-quality social posts, with a human (Betty or Camilo) approving every post before it goes live.

**Status:** Draft plan v2, 2026-11-20. Nothing built yet. v2 changes the runtime to **Aquiles** (the always-on OpenClaw agent on the Mac mini) instead of a standalone Claude pipeline; see section 2.

---

## 1. Requirements (from the brief)

| # | Requirement | How the plan meets it |
|---|---|---|
| 1 | Daily or weekly posts for Instagram and other platforms | Agent drafts a full week of posts once a week (3–4 posts/week to start) |
| 2 | Topic: weddings, Betty's ceremony + license handling | Content pillars (section 4) all tied to her services and locations |
| 3 | Every post has a picture | Image library (Betty's/Camilo's photos first, free-license stock second) |
| 4 | Betty or Camilo approves **each** post before publishing | Hard gate: nothing is scheduled or published without an explicit approval (section 6) |
| 5 | Posted at the days/times people see them most | Posting schedule with starting best-times, tuned from Insights data (section 7) |
| 6 | Caption in Spanish first, then English | Fixed caption template, enforced by the agent and checked automatically (section 5) |
| 7 | Purpose: win business | Every post has a goal and a call to action (CTA) pointing to the website, WhatsApp/phone, or DM |

---

## 2. Recommended approach (decision summary)

Build this as an **agent with a human approval step**, not a fully autonomous poster, and **run it on Aquiles** (OpenClaw on the Mac mini).

### Who runs it: Aquiles, with Claude Code as the builder

| Concern | Aquiles (OpenClaw, Mac mini) | Claude Code (this repo) |
|---|---|---|
| Always on, can run on a schedule | **Yes** (gateway + cron/heartbeat) | No, only runs when a session is open |
| Telegram approval chat with buttons | **Already set up** (Betty and Vanessa may join chats) | No |
| Running cost | **Flat**: ChatGPT plan (GPT-5.4) plus Gemini/Ollama; no new per-token bill | Separate Anthropic API spend |
| Already watches the wedbybetty site | **Yes** (heartbeat checks Netlify form submissions and alerts Camilo) | No |
| Draft-only precedent | **Yes** (`biz-growth` writes "DRAFT - NOT SENT"; a human sends) | n/a |
| Best at | Running the weekly loop and talking to Betty | Writing the spec, templates, prompts, tests; fixing the system |

**Decision:** Aquiles is the **operator** (weekly generation, Telegram approvals, scheduling, metrics). Claude Code is the **builder** (writes `social/` files, templates, and the agent instructions once, in this repo, and revises them when Betty's feedback shows a gap). This avoids a second always-on system and a second bill, and approvals land where the family already chats.

Caveats to settle first:
- **Config freeze:** Aquiles' memory says "no system updates or config changes unless explicitly requested," and cron is currently disabled. Camilo must explicitly approve adding the agent and a weekly schedule.
- **Spanish quality:** GPT-5.4 is fine for this, but Betty reviews the first 2–3 batches. Her corrections go into `brand-voice.md`.
- **Publishing:** use an official API or scheduler (Meta Business Suite, Buffer, or Instagram Graph API). Do **not** have Aquiles drive Instagram through a logged-in browser; automation like that risks the account being flagged.
- **Cost bookkeeping:** log this under a `wedbybetty` project in Aquiles' `biz/costs.js` ledger so the flat-plan cost is tracked.

### Three implementation options

| Option | What it is | Effort | Cost | Pros | Cons |
|---|---|---|---|---|---|
| **A. Semi-manual MVP (start here)** | Aquiles generates a weekly batch into the repo's `social/` folder and sends it to Telegram. You review there, then schedule in **Meta Business Suite** (free, Instagram + Facebook native scheduling) or **Buffer** | Low (1–2 days) | $0–$6/mo | Works immediately, zero API approval hurdles, you see everything | Scheduling the approved posts is a manual copy/paste step |
| **B. Automated with approval inbox** | Same generator, with Aquiles' Telegram chat as the review inbox. Approve → the agent posts via the **Instagram Graph API** (or Buffer API) at the scheduled time | Medium (1–2 weeks) | ~$0–6/mo (optional Buffer; model usage is on the flat plan) | One-tap approval from a phone, no copy/paste | Needs a Meta developer app + Business account setup; more moving parts |
| **C. Full autonomous** | Agent publishes without review | — | — | — | **Rejected.** Violates the approval requirement and risks wrong license/legal info or off-brand Spanish going public |

**Recommendation:** Start with **A (run by Aquiles) for the first 3–4 weeks** to prove the content works and learn what Betty likes, then upgrade to **B** once the post style is settled. The generator and calendar format are identical, so nothing is thrown away.

---

## 3. Architecture

```
                 ┌──────────────────────────────────────────┐
  Weekly trigger │ 1. PLAN      pick topics from pillars +   │
 (Sunday AM PT)  │              seasonal calendar + what     │
        ─────────▶              performed well last week     │
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 2. WRITE     Spanish caption, then English│
                 │              hashtags, CTA, alt text      │
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 3. IMAGE     match photo from library /   │
                 │              stock; crop to 4:5 / 9:16    │
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 4. CHECK     automatic QA (language order,│
                 │              length, facts, banned claims)│
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 5. APPROVE   Betty / Camilo: ✅ ✏️ ❌       │  ◀── HUMAN GATE
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 6. SCHEDULE  Meta Business Suite / Buffer │
                 │              / Graph API at best time     │
                 └───────────────┬──────────────────────────┘
                                 ▼
                 ┌──────────────────────────────────────────┐
                 │ 7. LEARN     weekly metrics → next plan   │
                 └──────────────────────────────────────────┘
```

### Suggested repo layout

```
docs/
  social-media-agent-plan.md        ← this file
social/
  brand-voice.md                    ← Betty's tone, do/don't, sample captions
  facts.md                          ← approved facts (pricing, service area, license rules)
  hashtags.md                       ← EN + ES sets by theme
  calendar/
    2026-W48.json                   ← one file per week: posts, status, time, image
  images/
    library/                        ← originals (Betty's/Camilo's photos) + index.json (tags, consent, credit)
    stock/                          ← downloaded free-license images + license note per file
  out/
    2026-W48/post-1.png + post-1.md ← ready-to-publish assets for review
  metrics/
    2026-W48.csv                    ← weekly results
```

Each post in the calendar JSON carries a **status**: `draft → needs_review → approved → scheduled → published` (or `rejected`). Only `approved` posts may ever be scheduled. This status field is the safety gate.

---

## 4. Content strategy

### Platforms (matches existing strategy in `weddings.md`)

1. **Instagram** (feed posts + Reels + Stories) — primary
2. **Facebook Page** — cross-post automatically from Instagram (free, near-zero extra work; also needed for Meta ads later)
3. **TikTok** — short video only; add in Phase 3 when there is video to use
4. **Google Business Profile posts** — weekly, 1 short post; high local-SEO value
5. Skip X/Twitter, LinkedIn, Pinterest (low return, per `weddings.md`)

### Content pillars (rotate through these)

| Pillar | Share | Examples | Business purpose |
|---|---|---|---|
| **License & legal made easy** | 25% | "3 steps to your California marriage license", "Confidential vs. public license", "Who can be your witness?" | Trust + answers the exact questions couples search |
| **Ceremony & experience** | 25% | What a ceremony looks like, bilingual vows, "what to expect", readings | Shows the product |
| **Locations** | 20% | Oceanside Pier, harbor, beaches, parks, backyards (photos already on the site) | Local SEO + inspiration |
| **Social proof** | 15% | Real reviews (with permission), real couples' photos (with consent) | Conversion |
| **Betty / behind the scenes** | 10% | Betty introducing herself in Spanish and English, prep, tools of the trade | Personal connection |
| **Offers & CTA** | 5% | Open dates, "Book your free 15-min call", small elopement packages | Direct leads |

### Seasonality
Wedding season peaks March–October in San Diego, but **engagement-season planning** peaks Nov–Feb (post-holiday proposals). Content from now to February should skew toward "just got engaged? here's how simple it is" and license/legal explainers. Add holiday hooks (Valentine's Day, 11/11, 12/12, 2/22, other "special date" weddings).

### Post formats
- **Single image** (4:5, 1080×1350) — default
- **Carousel** (3–7 slides) — best for step-by-step license explainers; Claude writes slide text, template renders them
- **Reel** (9:16, 15–30s) — only when real video exists; agent supplies script + caption, Betty/Camilo shoot
- **Story** — optional reminders (e.g., "Open dates this month")

### Cadence
- **Start:** 3 feed posts/week + 1 Google Business post (about 4 approvals per week, ~10 minutes of review)
- **Grow:** 4–5/week once there is a library of photos and the review routine is comfortable
- Consistency beats volume; skipping a week is better than posting something weak.

---

## 5. Post format and language rules

### Caption template (Spanish first, English second — always)

```
[HOOK in Spanish – 1 line, appears before "...more"]

[Spanish body – 2–4 short lines]
👉 [Spanish CTA]

—————
🇺🇸 [English hook]

[English body – mirror of the Spanish, not a word-for-word robot translation]
👉 [English CTA]

[Location tag] • [8–12 hashtags: ES set first, then EN set]
```

### Language rules for the agent
- Spanish is **written first, natively** (neutral, warm Latin American/US-Spanish; "tú" form unless Betty prefers "usted"), then English is adapted — not machine-translated.
- Keep the Spanish hook strong: only roughly the first 125 characters show before "...more".
- Always write alt text (accessibility + SEO), in Spanish and English.
- Instagram caption limit is 2,200 characters; target under 1,000 for readability.
- **Betty reviews Spanish tone** on the first 2–3 batches; her corrections go into `brand-voice.md` so the agent improves.

### CTAs (rotate)
- "Escríbenos por WhatsApp / DM" · "Reserva tu llamada gratis" · "Link en la bio" · "Guarda este post para cuando estés listo/a"
- Always points to wedbybetty.com, the phone number (760) 492-3054, or DM.

### Hard guardrails (agent must never)
1. Invent legal, price, or license facts. All license/legal statements must come from `social/facts.md` (verified against the San Diego County Clerk's official website by Betty/Camilo). The agent flags anything not in that file instead of guessing.
2. Fabricate testimonials, couples, reviews, or "recent weddings".
3. Use a photo of identifiable people without their written consent.
4. Use AI-generated images to depict real ceremonies or real couples (graphics/templates are fine).
5. Use copyrighted music, images, or text.
6. Make guarantees ("100% legal anywhere", "we handle everything" without detail) that Betty can't stand behind.

---

## 6. The approval step (human gate)

**Rule: no post is scheduled or published until its status is `approved` by Betty or Camilo.**

### Phase A (manual MVP)
- Agent produces a weekly **review sheet** (Google Doc or Sheet, or a markdown file) with, for each post: image preview, Spanish + English caption, proposed day/time, goal, and a status cell.
- Betty/Camilo mark Approved / Change / Reject and add notes.
- Approved posts are loaded into Meta Business Suite (or Buffer) scheduler.

### Phase B (one-tap approval)
- Agent sends each draft to a **private Telegram chat** (or email / WhatsApp) with the image and caption, plus buttons **✅ Approve · ✏️ Edit (reply with changes) · ❌ Reject · ⏰ Change time**.
- "Edit" sends the feedback back to Claude, which revises and resends.
- On ✅, the agent schedules the post. Unreviewed posts after their time slot expires are **skipped, never auto-published**.
- Approver identities are limited to two accounts (Betty, Camilo).
- Reminder if a batch is still pending 24 h before the first slot.

### Review SLA
- Batch delivered **Sunday**, reviewed by **Monday night**, so the Tuesday–Sunday slots are covered.

---

## 7. When to post (starting schedule — Pacific Time)

General social-media research and typical local-service patterns suggest weekday late morning to early afternoon, and evenings, work best for Instagram, with Sunday evenings strong for wedding planning browsing (couples plan on their downtime). **Treat these as starting hypotheses, not facts** — your audience (engaged couples, many Spanish-speaking, plus their families) may differ, and the first 4–6 weeks of Instagram Insights ("Most active times") will replace them.

| Slot | Day / time (PT) | Content type | Why |
|---|---|---|---|
| 1 | **Tuesday 12:00 PM** | License/legal tip or carousel | Lunch-break scrolling; educational content |
| 2 | **Thursday 7:30 PM** | Ceremony or location photo | Evening wind-down; inspiration browsing |
| 3 | **Sunday 6:00 PM** | Social proof / Betty intro / CTA | Peak "planning the wedding" evening |
| 4 (optional) | **Saturday 10:00 AM** | Location or Reel | Weekend browsing + wedding-day buzz |
| GBP | **Wednesday 10:00 AM** | Short local post | Fresh Google profile activity |

### Tuning loop
1. Weeks 1–4: use the schedule above and **vary** slots a little to collect data.
2. After 4 weeks: compare reach, saves, shares, profile visits, and link clicks per slot/format.
3. Then shift to top-performing slots; re-check quarterly and around wedding season.
4. Switch the agent to use **Instagram Insights "Most active times"** for the account once available (the Business account must have enough followers/activity).

### Success metrics (what "bringing business" means)
Likes are vanity. Track, in order of importance:
1. **Inquiries** (DMs, WhatsApp, calls, website form) that mention social media
2. Profile visits and link-in-bio clicks
3. Saves and shares
4. Follower growth (local, Spanish-speaking engaged couples)
5. Reach and impressions

Add "How did you hear about Wed by Betty?" to the inquiry form so bookings can be tied back to social.

---

## 8. Images

Priority order:

1. **Betty's/Camilo's own photos** (ceremonies, locations, Betty herself). Best performing, 100% authentic. Put them in `social/images/library/` and tag them (location, type, people-consent yes/no) in `index.json`. The site already has Oceanside pier/harbor photos in `assets/`.
2. **Photographer partners** — ask local wedding photographers for shareable photos with credit; builds relationships and referrals.
3. **Free-license stock** (Unsplash, Pexels, Pixabay): the agent prefers real San Diego/Oceanside beach and ceremony imagery, never presents stock couples as Betty's clients, and records the source/license in a sidecar note. Avoid images with clearly identifiable models in ways that imply a testimonial.
4. **Branded text graphics/carousels** made from templates (consistent colors/fonts from the website) — ideal for license explainers where no photo is needed. Canva (free) or an HTML-to-PNG render.

Image rules: crop to 4:5 or 9:16, no watermarks/third-party logos, minimum 1080px wide, keep a consistent warm "coastal editorial" look (matches the current site redesign).

**Ask for from Betty:** 20–30 photos to start (ceremonies, her portrait, locations, signing the license), plus a quick "who agreed to be shown" list.

---

## 9. Tech choices

| Concern | Recommendation | Notes |
|---|---|---|
| Content generation | **Aquiles** (OpenClaw, GPT-5.4 on the existing ChatGPT plan); `ask.js`-style agent with its own instructions file | Flat plan, no new per-token bill; Claude Code writes/maintains the instructions |
| Orchestration | Aquiles weekly cron on the Mac mini (needs Camilo's explicit OK to enable); repo `social/` folder is the source of truth, pushed to GitHub | Versioned, backed up with the existing daily backup |
| Scheduling/publishing | Phase A: **Meta Business Suite** (free) or **Buffer** free tier. Phase B: **Instagram Graph API** (content publishing) or Buffer API | Graph API requires an Instagram Business/Creator account linked to a Facebook Page and a Meta developer app |
| Approval | Telegram chat with Aquiles (Betty and Camilo added); Phase A can be plain text replies, Phase B adds buttons | Already in use, free, works on phone |
| Image handling | Sharp (Node) or Pillow (Python) for crop/resize; Unsplash/Pexels APIs for stock | |
| Secrets | API keys in GitHub Secrets / environment variables, **never committed** | Meta tokens expire (long-lived ~60 days) — add a refresh reminder |
| Metrics | Instagram Insights export / Graph API insights → `social/metrics/` CSV | |

**Estimated cost:** about $0–$6/month extra (optional Buffer); model usage rides on the existing flat ChatGPT plan. Meta Business Suite scheduling is free.

---

## 10. Rollout plan

### Phase 0 — Prerequisites (Betty/Camilo, ~1–2 hours)
- [ ] Create/confirm **@wedbybetty** Instagram **Business** account and link it to a Facebook Page (also needed for ads and the API)
- [ ] Create Google Business Profile (already the #1 priority in `SEO-CHECKLIST.md`)
- [ ] Decide approvers (Betty + Camilo); add Betty to the Telegram chat with Aquiles
- [ ] Camilo explicitly approves adding a social agent and weekly cron on Aquiles (config freeze)
- [ ] Provide 20–30 photos and a short bio, preferred tone (tú vs usted), phone/WhatsApp, services and prices she is comfortable sharing
- [ ] Verify license facts against the San Diego County Clerk website and write them into `social/facts.md`
- [ ] Add "How did you hear about us?" to the website contact form

### Phase 1 — Foundation (Week 1)
- [ ] Write `brand-voice.md`, `facts.md`, `hashtags.md`
- [ ] Build the weekly calendar JSON format and a markdown review sheet
- [ ] Create 3–4 reusable branded templates (single image, carousel slide, quote card)
- [ ] Tag and index the first photos

### Phase 2 — Manual MVP (Weeks 2–5)  ← Option A
- [ ] Generate batch every Sunday; Betty/Camilo approve Monday
- [ ] Schedule approved posts in Meta Business Suite (IG + FB at once)
- [ ] Collect all of Betty's edits into `brand-voice.md`
- [ ] Review metrics after week 4; adjust times and pillars

### Phase 3 — Automate approval and publishing (Weeks 6–9)  ← Option B
- [ ] Telegram (or email) approval bot with buttons
- [ ] Meta developer app + Graph API publishing (or Buffer API)
- [ ] GitHub Actions weekly cron for generation; scheduled publish job
- [ ] Weekly metrics pull + auto-written "what worked" summary

### Phase 4 — Expand (Month 3+)
- [ ] Reels/TikTok (script + caption from agent; Betty films 5–10 clips in one session)
- [ ] Google Business weekly posts automated through the same approval flow
- [ ] Use best-performing posts as Instagram/Facebook ad creatives (Phase 2–3 budget in `weddings.md`)
- [ ] Seasonal campaigns (engagement season, spring/summer rush, special dates)

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong license/legal info is published | Facts only from `facts.md`; agent flags unknowns; human approval on every post |
| Awkward or incorrect Spanish | Spanish is written natively first; Betty reviews initially; feedback loop into voice guide |
| Photo rights/consent problems | Library index records consent/source; stock license note per image; no AI "fake clients" |
| Content feels generic | Prioritize Betty's own photos/voice; use real stories (with permission); avoid stock-couple overload |
| Meta API/token friction | Start with Business Suite (no API); add API only after content is proven |
| Account banned/flagged for automation | Official APIs only (Graph API/Buffer); no scraping, bots, follow/unfollow automation, or fake engagement |
| Approvals pile up and posting stalls | Small batches (3–4/week), reminders, "skip not auto-publish" rule, one backup approver |
| Posts get no response | Weekly metrics review; change pillars/times; measure inquiries not likes |

---

## 12. Weekly operating routine (steady state)

| When | Who | What |
|---|---|---|
| Sunday AM | Agent | Reads last week's metrics, drafts next week's 3–4 posts + images |
| Sunday–Monday | Betty / Camilo | Approve, edit, or reject each draft (~10 min) |
| Mon night | Agent | Schedules approved posts at their slots |
| Tue–Sun | Betty | Reply to comments/DMs promptly (replies drive conversions; the agent can draft reply suggestions for approval, never auto-send) |
| Following Sunday | Agent | Metrics summary + recommendations |

---

## 13. Open questions for Betty/Camilo

1. Instagram handle and status of the Business account — does **@wedbybetty** exist yet?
2. Is Betty comfortable approving in Telegram (recommended, Aquiles already uses it)?
3. How many posts per week can you realistically review: 3, 4, or 5?
4. How many photos/videos can you provide now, and are couples' photos cleared for social use?
5. Tone in Spanish: informal "tú" or formal "usted"? Any phrases Betty always uses?
6. Which prices/packages (if any) may be shown publicly?
7. Is Betty comfortable appearing on camera (Reels/TikTok)?
8. Does a "Wed by Betty" Facebook Page and Google Business Profile exist yet?
9. Any budget for Buffer ($6/mo) or later ads?

---

## 14. Next step

On approval of this plan, start **Phase 1** (Claude Code builds, Aquiles later runs): create the `social/` folder with `brand-voice.md`, `facts.md`, `hashtags.md`, the weekly calendar format, and generate a **sample week of four posts** (Spanish first, English second, with images from the existing `assets/` photos) so Betty and Camilo can react to something concrete before any automation is built.
