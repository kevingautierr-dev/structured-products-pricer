# Daily run: briefing, pitch and @newsmacro115 carousel

Owner: Kevin Gautier. Runs Monday to Friday, starting around 7:35 Paris time.
Goal: the carnet "Briefing et pitch" is ready by 8:00, and the Instagram
carousel goes out on @newsmacro115 at **8:30 Paris time**, with no action from
Kevin. Work silently and quickly; Kevin is usually not watching.

Everything below happens in this branch (`newsmacro`) of
`kevingautierr-dev/structured-products-pricer`. It is separate from the pricer
code on `main`: never touch `main`.

## 0. Set up (2 min)

1. Get the current time with the current-time tool. "Today" is the Paris date.
2. Clone: `git clone --depth 1 -b newsmacro https://github.com/kevingautierr-dev/structured-products-pricer /home/claude/newsmacro`
   (generous timeout). If cloning or pushing fails for lack of access, attach
   the repository with push access (add_repo, owner `kevingautierr-dev`, repo
   `structured-products-pricer`, access `push`) and retry once.
3. Read `examples/2026-11-03.json`: it is the reference for the content.json
   schema and for the tone, length and density Kevin validated. Also read the
   latest `posts/*/content.json` for continuity (yesterday's levels).

## 1. Research (15 min max)

Use web search and fetch. Find, with at least two sources whenever possible:

- **The 6 numbers** at the previous session's close (Monday: Friday's close),
  level and change: S&P 500, Euro Stoxx 50, EUR/USD, US 10-year yield (change in
  bp), Brent, VIX. Note which one is the biggest move of the session.
- **This morning:** Asia, US and European futures, oil, anything overnight.
- **Three economic headlines** of the day, each with the effect for a client or
  a structured product (autocall, Athena, Phoenix, reverse convertible, capital
  protected notes).
- **One geopolitical topic**, the **day's appointments** (central banks,
  inflation, jobs, earnings) with **Paris times** and the expected impact.

Never invent or round a number you could not source. When sources disagree,
say so in `carnet.a_verifier` and keep that number off the slides.

## 2. Write `content.json` (work dir, not the repo)

Same schema as the example. Rules from Kevin:

- `carnet`: the standard trame of 2 and 3 Nov 2026. No emoji. The pitch has 5
  steps with these exact labels: "The market this morning (15 s)", "The two key
  moves (30 s)", "Why (20 s)", "What it changes (15 s)", "What we watch today
  (10 s)". Each step: `en` (main, spoken, about 90 s in total) and `fr` (the same
  text in French). `date_label` like "Nov 4, 2026".
- `slides`: cover + 6 to 9 content pages + outro (the outro is automatic). Very
  visual, little text per page: a short title (2 to 3 words ideally), one or two
  numbers, at most one line of text. Go straight to what moved the markets; do
  not detail tech baskets or barriers on the slides. Usual flow: Ce matin → Les 6
  chiffres → Le mouvement du jour → Les actions → Pourquoi (1 or 2 pages) → Ce
  que ça change (for structured products) → À surveiller (Paris times). Use the
  block types of `kit/slides.py`: rows, table6, figure, range, bars, nodes, box
  (alert | dark | blue | good | plain), metrics, steps, agenda, note, text.
  Use the true minus sign (−) and French decimals (7,6 %).
- `post`: `hook` (1 to 2 sentences), `jour_cloture` ("lundi", "vendredi", ...),
  `rendez_vous_court` (one short paragraph), `hashtags` (5 or so, no emoji).
  The caption and first comment carry the whole written carnet word for word
  (caption.py does the assembly).

Do not change colours, fonts or layout in `kit/slides.py`: the style was
validated by Kevin (white background, electric blue, huge uppercase titles).

## 3. Build and check (by 8:00)

```
K=/home/claude/newsmacro; W=/home/claude/work; mkdir -p $W/render
D=$(date +%d-%m-%Y)   # use the Paris date
python3 $K/kit/carnet.py $W/content.json "$W/Briefing_et_pitch_carnet_quotidien_$D.docx"
python3 $K/kit/slides.py $W/content.json $W/render       # exit 2 = text too long: shorten, re-run
python3 $K/kit/caption.py $W/content.json $W/render      # exit 2 = over 2,200 chars: tighten, re-run
cp $W/content.json $W/render/
```

Look at `render/contact.png`, then open every slide whose report shows
adjustments, and fix anything clipped, wrong or ugly. Convert the carnet to PDF
(`soffice --headless --convert-to pdf`) and look at the pages. Check every
figure on the slides against content.json.

Send the carnet to Kevin as soon as it is ready (SendUserFile, status
proactive), with a one-line caption.

## 4. Put the images online and schedule the post

```
cd $K && python3 kit/publish.py $W/render <YYYY-MM-DD>
```

It pushes to `posts/<date>/` and prints the public image URLs pinned to the
commit (it checks each one answers 200 image/png).

Metricool (brand `newsmacro115`, blogId `7845212`, timezone Europe/Paris):

1. `getScheduledPosts` for today (brandId 7845212, 00:00 to 23:59, Europe/Paris).
   If there is a **draft** whose text starts with `BROUILLON TEST`, update that
   post (`updateScheduledPost` with its id and uuid) with the content below.
   Otherwise create it (`createScheduledPost`). Never create a second post for
   the same day: if a non-draft post is already scheduled today, stop and say so.
2. Publication time: today 08:30 Europe/Paris. If it is already later than
   08:25, use now + 5 minutes.
3. `info` (JSON string):

```
{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "<comment.txt>",
 "hasNotReadNotes": false, "media": ["<url 01>", "...", "<url NN>"], "mediaAltText": [],
 "providers": [{"network": "instagram"}],
 "publicationDate": {"dateTime": "<YYYY-MM-DD>T08:30:00", "timezone": "Europe/Paris"},
 "shortener": false, "smartLinkData": {"ids": []}, "text": "<caption.txt>",
 "instagramData": {"type": "POST", "collaborators": [], "carouselTags": {}, "showReelOnFeed": true}}
```

4. Check with `getScheduledPosts` that the post is there, not a draft, at the
   right time, with all images in order.

## 5. Finish

One short final message: carnet ready, carousel scheduled at 8:30 (planner
link), and anything in `a_verifier`. No recap of the steps.

If the post cannot be scheduled (push refused, Metricool error), do not retry
endlessly: send Kevin the slide images, caption.txt and comment.txt with
SendUserFile so he can post by hand, and say in one sentence what blocked.
