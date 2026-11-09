---
name: writing-style
description: "Write and revise Chinese or English personal essays, blog posts, product notes, technical retrospectives, launch copy, and short social posts in this user's personal writing style: a plain, first-person, concrete voice that avoids generic AI cadence, essay transitions, forced symmetry, abstract summaries, and launch-deck phrasing. Use when the user wants writing that sounds like their own published work. Not for formal specs, API docs, legal copy, UI microcopy, or neutral third-party content."
metadata:
  short-description: My personal writing style
---

# Writing Style

Write like someone who used the thing, not like a launch deck. Start from a concrete situation, say what happened, then show the work. Strong opinions are fine; polish is not the goal.

## Scope

Use this for personal essays, blog posts, product notes, technical retrospectives, launch copy, and short social posts. Do not use it for formal specs, API docs, legal text, UI microcopy, or writing that should sound neutral.

## Voice

- Open with a real situation, problem, or claim. A time marker, a direct question, or a blunt statement is normal. Avoid opening with a thesis about the nature of software unless the piece is explicitly an essay.
- Prefer short paragraphs, one idea each. A paragraph can be one sentence.
- Use first person. "我" is the default. "我们" can include the reader or a team, but do not use it to avoid taking a position.
- Address the reader directly. "你" and rhetorical questions are part of the voice; use them to pivot, not as filler.
- Contrast is a core move: state the common view, then turn it with "但", "不过", or "其实". Do not make every paragraph a turn.
- Keep the wording plain. A little colloquialism helps: "老在", "搞个", "索性", "把玩", "（笑）". Do not sand every quirk off.
- Strong judgments are allowed: "我觉得", "我不想", "这玩意儿". Do not hedge every sentence.
- Use concrete numbers, dates, places, and personal details when they are available. They carry more voice than adjectives.
- Metaphors are allowed when they are concrete and a little earthy. Cut literary metaphors that only decorate.
- Do not force a moral or a metaphor at the end. If there is a closing line, it should be a real thought, not a summary of the article.
- Technical precision matters more than smoothness. If a claim is uncertain, say so or cut it.

## Observed habits

These come from 92 published posts, not from a style manual. Treat them as defaults, not quotas.

- Most posts are 1,000–3,000 characters; technical deep dives can run 5,000–7,000. Paragraphs mostly sit at 30–45 characters; titles at about 16. Do not pad a short idea.
- Headings are one or two levels (`#`, `##`). Bold marks a load-bearing claim, not decoration. Lists are format-specific, not a default.
- "我" dominates, "你" is used for direct address, and questions appear about twice per article.
- "但是", "不过", and "其实" are common turn words. "换句话说" and "说白了" are essentially absent; avoid them.

## Article shapes

- **Product / open-source note:** concrete personal problem → what you built → how to use it → what it looks like now → limits → links. Keep it short. Do not add a feature matrix unless the product needs one.
- **Technical / retrospective:** headings are allowed. Paragraphs still stay short. Use bullets or tables only when they carry dense information.
- **Opinion / essay:** one point per paragraph. You can end on a personal image or an unresolved question; do not manufacture uplift.
- **List / Q&A:** use numbered points when the content is genuinely parallel. Do not turn every article into a listicle.
- **Video companion:** write it as spoken narration. Images can carry the steps; the text should sound like someone talking, not reading a manual.
- **Short post:** one concrete detail, one turn, one question. Do not compress a full essay into a thread.

## AI-tell pass

Remove these before delivering:

- repeated "不是……而是……" constructions
- filler uses of "换句话说" and "这让我想到"
- filler uses of "当然", "或许", "某种程度上"; keep them only when they carry a real qualification
- triadic lists that exist only for rhythm
- a polished aphorism at the end of every section
- abstract nouns where a verb or a concrete object would do
- over-neat headings and bullets that make a post read like documentation
- English launch-deck phrases such as "The original problem was mundane", "Technical bits", "Current limitations", "The obvious comparison is"
- excessive em dashes, colons, and quotation marks

## Workflow

1. Identify the concrete scene or claim. If the user gave none, ask for one short example. Do not invent personal history.
2. Choose the shape: product note, technical piece, opinion, list/Q&A, video companion, or short post.
3. Draft with short paragraphs. Keep facts that can be verified; cut anything that only sounds good.
4. Run the AI-tell pass. Read the first two paragraphs aloud; if they sound like a press release, rewrite them.
5. Check the ending. For a personal essay, delete the last paragraph if it only summarizes. For a technical piece, a short summary is allowed.
6. Preserve the author's actual quirks and opinions; do not replace them with "better" ones.

## References

- For line-level before/after edits, read [references/ai-tells.md](references/ai-tells.md).
- For article structure and length, read [references/article-shapes.md](references/article-shapes.md).
- For voice patterns and corpus observations, read [references/voice-patterns.md](references/voice-patterns.md).
