# Project-owners training script

**You follow this document while you train.** Do not ad-lib metrics. If a yellow banner says DEMO MODE or DEMO/SYNTHETIC, read it out loud.

| | |
|---|---|
| Live site | [https://pc.zebprojecthub.com/](https://pc.zebprojecthub.com/) |
| Browser | Microsoft Edge (guest / InPrivate if you have leftover logins) |
| Length | **25–30 minutes** core · **40 minutes** with Q&A |
| Starting state | Database was reset. Only the administrator exists. Dashboards start empty. |

Screenshots of screens (older counts) live in [USER_MANUAL.md](USER_MANUAL.md). **Ignore those numbers today.** Owners should see zeros until you create a participant in this session.

---

## 1. Before they arrive (5 minutes)

1. Open InPrivate Edge and load [https://pc.zebprojecthub.com/](https://pc.zebprojecthub.com/). Confirm the landing page.
2. Keep this document on a second screen or printed.
3. Write down one throwaway participant you will create live:

| Field | Suggested value | Notes |
|---|---|---|
| First name | Owner | Or an owner’s first name |
| Last name | Demo | |
| Email | `owner.demo@zebprojecthub.com` | Must be unused |
| Password | `OwnerDemo123!` | 8+ characters, letter + number |

4. Administrator (do **not** create this in the session — it already exists):

| | |
|---|---|
| Email | `admin@temperamentlab.local` |
| Password | `AdminDemo123!` |
| Lands on | `/admin` |

5. Decide whether you will **train DEMO models** in this session.  
   - **Skip** if the owners only need the product story (register → assessment → result).  
   - **Do it** if they want to see Decision Tree / Naive Bayes / KNN. Those fits are labelled DEMO/SYNTHETIC. Say that before you click.

---

## 2. Sentences you must use

Say these at least once. They are the defence of the project.

1. **Scoring is not classification.** Likert answers become category scores (features). The class label comes from a stored model, or from a labelled DEMO fallback if no model is ACTIVE.
2. **“Your assessment indicates…”** — never “you are” or “this is a diagnosis.”
3. **Empty cards are honest.** The dashboard does not invent a mix before a completed, classified assessment exists.
4. **Yellow banners are not optional.** DEMO MODE / DEMO/SYNTHETIC numbers are not research findings.
5. **Roles are enforced on the server.** A participant who types `/admin` is sent back to `/app`. Administrators cannot be created from the public register form.

---

## 3. Session map

| Clock | Block | Goal |
|---|---|---|
| 0:00 | Open + problem | Why a platform, not a paper questionnaire |
| 0:03 | Public site | Landing, How it works, four types |
| 0:08 | Register a USER | Owners see a real account created |
| 0:11 | Empty workspace | Honesty of empty state |
| 0:13 | Assessment | Consent + 32 Likert items |
| 0:20 | Result | DEMO MODE if no ACTIVE model (current live state) |
| 0:23 | Admin console | Empty-then-filled overview, questions, isolation |
| 0:28 | Optional ML | Dataset → Train DEMO → Evaluate → *do not treat 100% as research* |
| 0:35 | Q&A | Use the answers in section 8 |

If time is short, **cut the optional ML block**. The product story is complete after the admin overview.

---

## 4. Script — follow in order

For each step: **Do** is what you click. **Say** is what you tell them. **See** is the pass condition.

### 4.1 Open the site (0:00)

**Do:** Address bar → `https://pc.zebprojecthub.com/`

**Say:**  
“This is Temperament Lab, the public name of Personality Classification Using Data Mining. It standardises a Likert questionnaire, turns answers into numerical features, and classifies into four educational types: Choleric, Melancholic, Phlegmatic, Sanguine. It is not a clinical diagnosis.”

**See:** Hero “Discover your personality through data”, buttons **Take assessment** and **How it works**.

---

### 4.2 How it works (0:03)

**Do:** Header **How It Works**, or the button on the hero.

**Say:**  
“Three steps. One: answer a versioned questionnaire stored in the database, not hardcoded in React. Two: answers become category scores — that is feature engineering, not the personality label. Three: a trained classifier maps the feature vector to a type. If no model is active, the system still classifies with a labelled DEMO fallback so the pipeline is visible. We will see that banner later.”

**See:** Steps 01 / 02 / 03 on the page.

---

### 4.3 Four types (0:05)

**Do:** **Personality Types**.

**Say:**  
“The same four labels are used on the public site and by the classifier. Copy comes from MySQL. An assessment indicates a pattern; it does not diagnose a person.”

**See:** Choleric, Melancholic, Phlegmatic, Sanguine cards.

Optional 30 seconds: **About** — “what it does not do” and “metrics come from a held-out split, never typed in.”

---

### 4.4 Register a participant (0:08)

**Do:** **Get Started** (or `/register`). Fill the table from section 1. Click **Create account**.

**Say:**  
“Anyone can create a USER account here. New accounts always receive USER. Administrators are created separately. Gender and age group are optional — we do not need date of birth.”

**See:** Redirect to `/app`, heading **Welcome back, {First name}**, role **USER** in the header.

If email is taken, change the local part (`owner.demo2@…`) and continue. Do not log in as the old deleted demo user — that account is gone.

---

### 4.5 Empty workspace (0:11)

**Do:** Stay on **Dashboard**.

**Say:**  
“Cards are empty because this person has not finished an assessment. Assessments completed is 0, latest type is None yet, mix says no classification yet. Nothing here is a placeholder percentage.”

**See:**

| Card | Expected now |
|---|---|
| Assessments completed | 0 |
| Latest personality type | None yet |
| Mix | No classification yet |

---

### 4.6 Consent (0:13)

**Do:** Sidebar **Take assessment**.

**Say:**  
“The instrument is version 1, 32 Likert items. Scores become ML features; they are not the final class. Consent is required and stored on the assessment. Start stays disabled until the box is ticked.”

**See:** Checkbox; **Start assessment** disabled, then enabled after tick.

**Do:** Tick consent → **Start assessment**.

---

### 4.7 Questionnaire (0:14)

**Do:** Answer all 32 items (1 Strongly Disagree … 5 Strongly Agree). For a fast demo, use **Neutral / Agree** and click **Next**. You can **Save progress** once to show answers persist.

**Say:**  
“Each answer is stored per question. Weighted scores stay on the server. The participant view does not show weight or reverse scoring, so you cannot game the key from the UI.”

**See:** “Question *n* of 32”, progress bar. **Submit assessment** stays disabled until every item has an answer.

**Do:** On the last item, **Submit assessment**. Wait for classification (a few seconds).

If the network is slow, say so and wait. Do not refresh twice.

---

### 4.8 Immediate result (0:20)

**See (current live system, no ACTIVE model):**

- Headline: **Your assessment indicates {Type}.**
- Yellow: **DEMO MODE. No ACTIVE model is registered. A labelled rule-based fallback was used.**
- Mix source similar to `demo_item_totals`
- Language: educational, not a diagnosis

**Say:**  
“This is the honest state of a fresh system. There is no ACTIVE sklearn model yet, so classification used a labelled fallback. The mix is stored from that fallback. We do not invent percentages on the results page.”

**Do:** **View full result**. Point at Print / Download summary. Point at strengths and development copy from the personality catalogue.

---

### 4.9 History and profile (0:22)

**Do:** **History** — one completed row, DEMO badge if DEMO MODE.  
**Do:** **Profile** — name and optional demographics; “Your role cannot be changed here.”

**Say:**  
“History is this user’s attempts only. Mix percentages stay on the results page, not in the table.”

---

### 4.10 Switch to administrator (0:23)

**Do:** **Sign out** → **Login** → admin email and password.

**Say:**  
“Same login form. The server checks the role. Administrators land on the research console.”

**See:** Header **Ada Admin · ADMIN**, sidebar Overview … Audit log.

---

### 4.11 Overview after the live assessment (0:24)

**Say:**  
“These totals are counts of MySQL rows. This page does not run a new prediction.”

**See (after one successful participant in this session):**

| Card | Expected |
|---|---|
| Registered users | 2 (1 participant · 1 admin) |
| Assessments completed | 1 |
| Stored classifications | 1, and “1 in DEMO MODE” if the fallback ran |
| Active model | **None** |
| Stored type counts | 1 bar on whatever type was indicated |

If you skipped the assessment, users = 1 and the other cards stay 0. That is still a valid demo of honesty — then go back and register.

**Do:** **Users** — only names, emails, roles. “Passwords are never returned.”  
**Do:** **Assessments** — status and stored type. “Likert answers are not shown to administrators here.”  
**Do:** **Questions** — 32 items, pagination. “After an answer exists, scoring fields lock. We deactivate instead of deleting so old assessments stay reproducible.”

Optional: type `/admin` is already where you are. Tell them a USER who opens `/admin` is bounced to `/app`.

---

### 4.12 Optional — show the ML loop (0:28)

Only if owners asked “where is the data mining?”

**Do:** **Dataset** → **Validate DEMO CSV**.

**Say:**  
“This only checks the bundled file and builds features. It does not train and it does not invent accuracy. The file is DEMO/SYNTHETIC.”

**Do:** **Training** → **Train DEMO models**. Wait until the table lists Decision Tree, Naive Bayes, KNN.

**Say:**  
“Three classical algorithms on the same training fold. KNN uses a scaler inside a pipeline. If train-fold scores look like 100%, that is because the synthetic labels were constructed. We will not put those numbers in a research report.”

**Do:** **Models** → **Evaluate DEMO held-out set**.

**Say:**  
“Held-out metrics come from sklearn. Registry stays empty until we activate. New participant classifications stay in DEMO MODE until one artefact is ACTIVE.”

**Do not** click **Activate selected** unless you immediately say:  
“Even after activate, a model trained on DEMO/SYNTHETIC data must not be reported as a research model. The UI will still warn.”

If you activate, you can sign out, log in as the participant, take a **new** assessment, and show `mix_source` / DEMO reason change. Budget extra time.

---

### 4.13 Close (0:35)

**Say:**  
“You have seen the public story, a real USER account, a full questionnaire, a stored result with cautious language, and an admin console that counts what is in the database. Next steps for a real study would be ethically collected labelled data, then train and activate a non-synthetic model.”

**Do:** Sign out. Leave the browser on the landing page.

---

## 5. If something breaks

| What you see | What you do |
|---|---|
| SSL / site won’t load | Try the URL again; wait 10 seconds. Do not switch to the old IP:9100 unless you have already explained Cloudflare. |
| “Invalid email or password” on admin | Caps lock; use `admin@temperamentlab.local` / `AdminDemo123!`. |
| Register rejected | Email already used, or password missing a letter/number. Change email. |
| Submit stays grey | An item is unanswered. Use Previous until the progress count is 32 of 32. |
| Result is DEMO MODE | That is correct today (no ACTIVE model). Treat it as a teaching point, not a failure. |
| Admin overview still 0 after submit | Hard refresh. Confirm you submitted **and** waited for “Your assessment indicates”. |
| You are still in the USER app as admin | Header **User app** vs **Admin** — use **Admin** / Overview. |
| Yellow 100% scores after DEMO train | Read the banner. Do not call it model quality. |

---

## 6. What owners can try themselves (hands-on)

If they want to click:

1. One owner registers their own USER (their email).
2. They complete the 32 items (or watch you).
3. They open **Results** and **History**.
4. You stay on admin (second InPrivate window) and show their row appear under **Users** / **Assessments** without showing their Likert answers.

Two windows: Window A = participant, Window B = `admin@temperamentlab.local`. Do not mix tokens in one profile.

---

## 7. What not to promise

- Clinical or hiring use
- That DEMO/SYNTHETIC accuracy is a project finding
- Mix percentages that are not on the screen
- That administrators can read a participant’s Likert answers from the Assessments table (they cannot)
- That `/register` can create an ADMIN

---

## 8. Likely questions — short answers

**Why four old temperament types?**  
Educational, well-known labels for a four-class supervised problem. Not a modern clinical taxonomy.

**Is this machine learning or a scorecard?**  
Both exist, and they are separated. Category totals are features. The class is a persisted sklearn model when one is ACTIVE. Without that, DEMO MODE is labelled.

**Which algorithm is best?**  
Only after held-out evaluation on **non-synthetic** labelled data. DEMO CSV comparison is for showing the pipeline.

**Where is the data?**  
MySQL/MariaDB on the application stack. Passwords are bcrypt hashes. JWT does not store the role as the source of truth — the API reloads the user from the database.

**Can we add our own questions?**  
Yes, as ADMIN on **Questions**, on the active version. Scoring fields lock after the first answer.

**Can we use our own labelled CSV?**  
Yes: Dataset **Upload CSV** → Training **Train uploaded CSV** → Models evaluate → activate. The CSV must match the instrument’s feature columns.

**Is it live for students now?**  
The URL is live. Accounts created here are real. Treat DEMO MODE results as educational only.

---

## 9. Checklist to print

- [ ] InPrivate Edge on https://pc.zebprojecthub.com/
- [ ] Participant details written down
- [ ] Admin password to hand (not on the projector)
- [ ] Landing → How it works → Types
- [ ] Register USER → empty dashboard
- [ ] Consent → 32 items → submit
- [ ] Point at DEMO MODE banner
- [ ] Results + history
- [ ] Sign out → admin overview (counts match what you just did)
- [ ] Users / Assessments / Questions
- [ ] Optional Dataset + Train DEMO + Evaluate (say SYNTHETIC)
- [ ] Sign out, landing page, Q&A

---

## Related

- [USER_MANUAL.md](USER_MANUAL.md) — full screens, UML, access tables (screenshot counts are from before the reset)
- [ARCHITECTURE.md](../ARCHITECTURE.md) — design for examiners
