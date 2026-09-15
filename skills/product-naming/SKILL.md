---
name: product-naming
description: Product naming and domain research workflow for proposing creative English/Chinese product names, explaining naming metaphors, and checking matching domain availability and price signals. Use when the user asks to name or rename a product/project/company/tool and wants domain checks such as .com, .design, .art, registration status, premium/price caveats, or a concise shortlist rather than broad brainstorming.
---

# Product Naming

## Workflow

1. Ground the product in one sentence before naming.
   - Read the closest product docs, package metadata, landing copy, README, or user-provided description.
   - If local docs are placeholder text, say so and infer only from real code/package surfaces.
   - Capture the product's core action, audience, and strongest metaphor.

2. Generate names in focused lanes.
   - Prefer single-word names or single-word-feeling coined names when the user asks for names that do not feel like combinations.
   - Use direct category words only when they remain brandable. Avoid overusing obvious category words unless the user explicitly wants them.
   - Keep each lane small: real words, metaphor words, coined words, and native-language names. Do not spray dozens of weak variants before checking availability.

3. Explain the naming logic.
   - For each serious candidate, give the Chinese name direction and the implied product story.
   - Favor names whose metaphor can stretch with the product beyond the current feature set.
   - Reject candidates that are hard to pronounce, too generic to defend, misleading for the product, or mainly clever because of spelling.

4. Check domains before final ranking.
   - Read `references/domain-query.md` when domain availability or pricing is requested.
   - Check the exact word across the requested TLDs, usually `.com`, `.design`, and `.art`.
   - Treat RDAP `404`/not-found as "likely available", and a domain object as registered.
   - If a domain query fails because of sandbox networking, request the needed network approval instead of guessing.

5. Keep price claims honest.
   - Use Tencent Cloud `CheckDomain` only when valid credentials/signing are available or the user provides a working query path. Its `Price`, `RealPrice`, `Premium`, and renewal fields are the precise source for Tencent Cloud purchase decisions.
   - If Tencent Cloud cannot be called, label public registrar pricing as a non-premium reference, include the source/date, and do not present it as the exact checkout price.
   - Mention that premium names can be much more expensive than TLD baseline pricing.

6. Report a ranked shortlist.
   - Put the best candidates first, not every generated name.
   - Include: English name, Chinese direction, rationale, `.com/.design/.art` status, and price caveat.
   - Separate "recommended" from "also viable" when many domains are unavailable.
   - End with a practical recommendation such as "best if you accept `.design`" or "needs another coined-name pass if `.com` is mandatory."

## Output Shape

Use a compact table for the shortlist:

| Name | 中文方向 | Why it fits | Domains |
|---|---|---|---|
| Candidate | 中文方向 | Short metaphor tied to the product's core action. | `candidate.com` registered; `candidate.design` likely available; `candidate.art` likely available |

Then add a short note for pricing:

- `Exact Tencent Cloud price`: only if `CheckDomain` returned `Price`/`RealPrice`.
- `Reference registrar price`: only if copied from a public pricing page, with source and caveat.
- `Unknown`: if no reliable pricing source was queried.

## Guardrails

- Do not invent availability, registrars, registration dates, or prices.
- Do not equate RDAP availability with final checkout availability; call it "likely available" unless a registrar purchase API confirms it.
- Do not bury unavailable `.com` results. If `.com` is taken, say so plainly.
- Do not do trademark clearance unless the user asks; if the name will be used commercially, recommend a trademark search as separate legal diligence.
