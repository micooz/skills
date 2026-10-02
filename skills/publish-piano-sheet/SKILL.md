---
name: publish-piano-sheet
description: Produce a publishable piano score and matching 1080p60 falling-notes video from a user-provided audio recording, including metadata research, cover art, PDF/MusicXML/MIDI exports, review-gated YouTube publication, and mymusic5 sheet-music listing. Use for piano transcription, sheet-music delivery, falling-notes video, or end-to-end publication requests.
---

# Publish Piano Sheet

## Computer Use

For browser-driven work, use Computer Use through `cua_repl`. For DOM-heavy sites such as YouTube Studio, prefer Playwright/DOM inspection; use AX for application controls, native dialogs, and fallback, and screenshots for visual verification. Use full CDP only when DOM access is insufficient and the approval policy allows it. Prefer a connector, API, or CLI when it can perform the same action safely. Do not launch Chrome with remote debugging or bypass `cua_repl` with standalone CDP/Playwright; otherwise use an approved fallback or stop. Confirm uploads, public edits, publishing, and deletion at action time.

## Outcome

Produce and publish one song at a time from an original audio file:

1. Create a track workspace in the current working directory.
2. Research the recording and write the evidence to `research.md`.
3. Generate a clean piano score with Songscription.
4. Send the Songscription score URL to the user for review before download.
5. Download a one-page, QR-free PDF, a MusicXML file, and a MIDI file from Songscription.
6. Use the direct MusicXML download as-is and use the bundled `music21` converter only when the download fails.
7. Save the NoteFall `.nfz` project and render a 1080p60 video using the approved visual settings.
8. Upload and publish the approved video to YouTube, then record its public URL.
9. Publish the PDF and MusicXML to mymusic5.
10. Backfill the public sheet URL into the YouTube description.
11. Open the final App Link in the task browser and report both public URLs.

The workflow is only complete after both the YouTube video and mymusic5 sheet are publicly available and their URLs have been verified.

## Authorization Boundaries

- Never publish a YouTube video or mymusic5 listing until the user has reviewed and explicitly approved the exact metadata.
- Credit consumption and other metered or paid resources used by this workflow are pre-authorized. Do not ask the user to approve each consumption. Check the displayed cost and current balance when available, then proceed.
- If a provider reports an error, insufficient balance, payment failure, or quota block, stop that step and notify the user with the platform message. Do not retry blindly or silently switch to a paid alternative.
- The Songscription copyright declaration is pre-authorized. Tick it without asking again.
- Do not delete prior projects, downloads, or published content without explicit approval.

## Task Workspace

Create one directory per song in the current working directory where the Skill is executed:

```text
<Track> - <Source>/
```

Unless the user explicitly asks for another location, treat the Skill's execution directory as the project root. Do not hard-code a user-specific absolute path.

Use one canonical stem for deliverables:

```text
research.md
<Track> - <Source>.mp3
<Track> - <Source>.pdf
<Track> - <Source>.mid
<Track> - <Source>.musicxml
<Track> - <Source>.nfz
<Track> - <Source> - Cover.jpg
<Track> - <Source>-1080p60-high.mp4
```

Do not create an ASCII upload alias; Songscription derives the project name from the uploaded filename.

## Workflow

### 1. Research and metadata

> Use subagent to do research if available.

Inspect the provided audio before editing or uploading:

```bash
ffprobe -v error -show_entries format=duration,bit_rate:format_tags -show_entries stream=codec_name,sample_rate,channels -of json <audio>
```

Verify the music title, source, composer, and any remixer or arranger from more than one source when possible. Do not infer a composer from a same-named soundtrack or free BGM.

Prefer the composer's official profile or original source-library listing over reposts, gamerips, or unrelated tracks with the same title.

When an external platform offers existing song records, select one only when the platform record strictly matches the title and the verifiable source/composer metadata. A matching title by itself is not enough. If the platform has no strict match, use its manual song entry rather than choosing an approximate result.

Maintain a metadata record with the track title, alternate-language title if any, source, composer, soundtrack/catalog reference, original release context, and the user's arrangement credit. Resolve the exact credit names from authoritative sources and reuse them consistently across the score, video, and marketplace. Keep project-specific facts outside this reusable Skill.

Write the original research materials and citations to `research.md` before starting Songscription. Include:

- the user-provided title, source, audio information, and any supplied references
- source URLs, provider names, publication dates, and access dates
- short quotations or faithful summaries of the evidence used for credits, release context, instrumentation, mood, and catalog placement
- verified locale-specific titles or source names when they will be used, including the citation for each; explicitly record when no reliable localized name is available
- candidate matches considered and why they were accepted or rejected
- the final metadata decisions and any unresolved uncertainty

### 2. Cover image

Find a source-related image that is as close to 16:9 as possible. Prefer official game/store/developer artwork over thumbnails. Verify the downloaded dimensions before continuing.

For a game soundtrack, a suitable image usually shows recognizable characters or key art and leaves space for the falling notes. Save it directly into the song directory with the canonical `Cover.jpg` name.

### 3. Songscription transcription

Open `https://www.songscription.ai/new` and upload the original audio filename.

Use these steps:

1. Keep the whole track unless the user specifies a clip.
2. Select the correct instrument. Solo piano recordings use `Piano`. The cards may be exposed as one accessibility list box; use keyboard navigation when necessary.
3. Use `Direct Transcription` when the source already contains the target piano performance.
4. Tick the copyright declaration according to the authorization boundary above.
5. Before `Start Transcription`, read the displayed credit cost and check the account balance.
6. After generation, review and correct notes before downloading.

In the score information panel, set:

- Title: `<Track>`.
- Subtitle: `<Source>`.
- Composer: prefix with `Composer: ` when shown on the score.
- Arranger: prefix with `Arranger: ` when shown on the score.
- Review any other exposed fields, such as `Lyricist`, `Dedication`, or `Copyright`, and fill them only when the researched metadata supports them.

Before downloading, send the Songscription score URL to the user for review.

### 4. Download PDF, MusicXML, and MIDI

In Songscription's `Download` panel:

- Download `PDF` for the marketplace and customer.
  - Turn the PDF QR code off.
  - Adjust `Staff size` as the main pagination control, checking the preview to improve page distribution and eliminate short final-page systems.
- Download `MusicXML` for the marketplace.
- Download `MIDI` for the NoteFall video pipeline.
- Save the PDF, MusicXML, and MIDI directly in the song directory and keep the canonical stem.
- The panel may also expose `RAW MIDI` and `MP3`, which are not required here.

### 5. MusicXML fallback

When the direct MusicXML download cannot be obtained, generate the canonical MusicXML from the downloaded MIDI with the bundled fallback script:

```bash
uv run --no-project --with music21 \
  python scripts/midi_to_musicxml.py \
  '<Track> - <Source>.mid' \
  '<Track> - <Source>.musicxml' \
  --title '<Track>' \
  --composer '<Composer>' \
  --arranger '<Arranger>'
```

The script writes title, composer, and arranger metadata, then reparses the result to confirm it is readable. Do not use MIDI conversion as the normal path.

### 6. NoteFall video

1. Open `https://notefall.app/`.
2. Use `File -> Open` and load the canonical MIDI file.
3. Ask user if use original audio, use `File -> Open Audio` load the original audio then disable MIDI audio by click left audio icon of MIDI Track. Do not turn off whole stage audio.

> Don't click on the canvas; doing so will accidentally add notes.

Set these values:

- `Camera -> Pivot Y`: `0.35`
- `Layout -> Keyboard Y`: `-3.00`
- `Scene -> Background Image`: the canonical cover image
- `Scene -> Opacity`: `0.30`
- `Notes -> Texture`: `Liquid`
- `Notes -> Width`: `0.80`
- `Notes -> Opacity`: `0.80`
- `Notes -> Track 1`: a bright color sampled from the cover
- `Notes -> Track 2`: a second, distinguishable color sampled from the cover

> Precise slider values are entered by right-clicking the slider and choosing `Enter Value...`. Keyboard arrow automation can coalesce and is not reliable for exact values.

4. Use `File -> Save` and save the NoteFall project as `<Track> - <Source>.nfz` in the same track directory. Confirm the file exists before continuing.

5. Before exporting, send the user the current NoteFall URL and ask them to confirm the previewed visual effect. Do not export until the user explicitly approves. If they request changes, apply them, save the project again, and repeat this confirmation.

6. Use `File -> Export` with:

- `Video + audio (MP4)`
- `1080p`
- `60fps`
- `High`

Save the MP4 directly in the song directory. Verify it with `ffprobe` before upload.

Confirm 1920x1080, 60fps, stereo audio, and a browser-playable H.264/AAC combination.

After exporting, send the exported video path to the user for a final review before uploading.

### 7. YouTube draft

Upload to the user's YouTube channel and prepare the video without publishing until approved.

Title format:

```text
<Source> - <Track> | Piano Cover
```

Description structure:

```text
📝 Sheet Music: <app link, added after publication>

🎹 Welcome to <Channel Name>!

<Researched description of the original piece.>

🎼 About This Cover:
• 🎧 Original Song: <Source> <Track reference>
• 🎼 Composer: <Composer>
• 🎹 Arranged & Performed by: <Arranger>

#<Source> #<SourceRevision> #<Original title> #<English title> #<Composer> #PianoCover #GameMusic #VGM #Piano
```

Write the descriptive paragraph from the collected, verified research rather than copying the example's prose or simply substituting track names. Use concrete facts such as the original release/source, composer notes, soundtrack placement, or documented mood and instrumentation. Keep uncertain claims out of the public description.

Preparation checklist:

- Choose the thumbnail from a video frame, not a separate still image.
- Prefer a frame that clearly shows falling notes and the piano keyboard.
- Select the source playlist, creating it only when absent.
- Mark the video as not made for kids unless the content actually qualifies.
- Review Content ID claims. A claim may still allow publication and global reach, but it can affect monetization.
- Stop before setting the video to public and show the user the final title, description, thumbnail, playlist, visibility, and any claims.
- In YouTube Studio's description editor, write the complete description and save it.

After the user approves publication, complete the public action, verify the video is public, and record the canonical public URL such as `https://youtu.be/<video_id>`.

### 8. mymusic5 publication

1. Open `https://studio.mymusic5.com/content`.
2. Upload the PDF and MusicXML.
3. In `Song Information`, use the strict-match rule above. If no existing record matches both title and source/composer, use the manual-add action (English UI: `Can't find your song? Add manually`), enter the song title and verified composer, and leave the original-creator checkbox unchecked unless it is actually true.
4. Complete the score-information step. Ask the user about any unclear field rather than guessing.
5. In `Sales Information`, add a title and product description for every language option exposed by the page. Include English and all optional locales, such as Korean, Japanese, Traditional Chinese, and Simplified Chinese when available. Do not leave an optional locale empty.
6. Use a localized track or source name in a locale only when `research.md` cites a reliable source for that name. Do not translate, transliterate, or infer names. If no verified localization exists, reuse the canonical verified name unchanged in every locale. Use the musician/source field for the source rather than the composer, and keep proper names and credits consistent with the researched metadata.
7. Use the public YouTube description as the source of truth for every locale's product description. Keep the same content and information, including the descriptive paragraphs and credit details, while translating or adapting the wording as needed for natural language and marketplace formatting. The `Music Sheet` line is the only content to omit because the sheet URL does not exist yet. Do not create locale-specific content, omit other sections, or paste the English description unchanged into non-English locales.
8. Enter the public YouTube performance URL, confirm the price and all remaining publication metadata with the user, then publish.
9. Record the public sheet URL and `sheet_id`.
10. Prefix the app link with `https://mymusic5.com/applink?sheet_id=<sheet_id>`.
11. Add this as the first line of the YouTube description: `📝 Music Sheet: <app link>`.
12. Open the App Link in a new tab in the current task Chrome window and leave it visible for the user.
13. Report both the public YouTube URL and `https://www.mymusic5.com/<username>/<sheet_id>`, plus the current review status if the marketplace still shows it as under review or in review.

## Failure and Recovery Cases

- Pitfall: Accessibility IDs, focus, or system native file-picker selection can become stale or expose the wrong element. Recovery: re-read state, cancel intervening dialogs, use visual recognition when accessibility remains wrong, and verify the selected filename plus enabled Open/Save before continuing.
- Pitfall: Address-bar navigation can appear successful without actually navigating. Recovery: focus the address bar, press Return, and verify the real URL, title, and page content.
- Pitfall: NoteFall's `Open Audio...` and `Save Song as MIDI...` can be confused during recovery. Recovery: cancel accidental saves, preserve stray files, and verify the canonical MIDI and audio lane before proceeding.
- Pitfall: Provider can derive an approximate or incorrect project/song name. Recovery: create the correctly named project or manual record instead of using an upload alias or approximate match.
- Pitfall: Provider controls can be hidden by unstable layout or overlays. Recovery: wait, use the visibly rendered control, dismiss overlays, or reopen the direct edit/upload URL.
- Pitfall: Songscription's Playwright `filechooser` can time out while the native picker is actually open and therefore absent from browser screenshots. Recovery: bind to Chrome with `cua.getApp("Google Chrome")`, use `Cmd+Shift+G`, set the full Unicode path with `setValue` (not `typeText`, which can drop Japanese characters), select the file, and press Return.
- Pitfall: Songscription's direct MusicXML download can fail in an individual session. Recovery: use the bundled MIDI-to-MusicXML script only when the download cannot be obtained instead of making conversion the default path.
- Pitfall: A marketplace rich-text description editor may collapse blank lines or keep only the first line. Recovery: after insertions, re-read field indices; set the full field once with `setValue` and `\n\n` between sections, then verify the visible blank paragraphs in a screenshot. If that fails, paste one section at a time with two `Return` presses between sections; avoid long `paste` runs and do not use `typeText` for long multilingual copy.
- Pitfall: YouTube's custom elements and dynamic frontend can leave AX state incomplete or stale. Recovery: inspect and operate the YouTube page through the extension's Playwright/DOM access, using CDP when DOM actions are insufficient; keep AX or coordinates for native dialogs.
- Pitfall: YouTube's description editor can retain only the first line, append duplicate text, or accept a DOM-only value. Recovery: append and delete one space, save, confirm `Save` and `Undo changes` are disabled, then reload or inspect the public watch page.
- Pitfall: NoteFall repeat, audio-lane, or `.nfz` state can reset during recovery. Recovery: verify all three alongside the rendered media before publishing.
