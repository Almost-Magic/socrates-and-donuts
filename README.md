# Socrates and Donuts

Socrates and Donuts is a local-first reflection app for difficult moments. It gives a user a quiet place to pause, write, answer careful questions, and decide what to do next without pretending to be a therapist or authority.

## What this is

This is a reflection and self-organisation tool. It is not therapy, medical advice, diagnosis, treatment, crisis care, emergency support, spiritual authority, or a replacement for a qualified teacher or professional.

The app should feel useful from the first screen: what it is, who it helps, what the user can do now, what it cannot do, and where to go when human support is needed.

## Who it helps

- someone who is about to send a reactive message;
- someone trying to think clearly during conflict, grief, or pressure;
- a Vipassana practitioner who wants a restrained local practice companion;
- contributors working on safe open-source companion tools.

## What you can do now

- ask the mirror for questions;
- lock a reactive message in the vault;
- write a letter you will not send;
- map how an emotion feels in the body;
- capture a thought quickly;
- rewrite a message in a calmer tone;
- review local notes and settings.

## Safety boundaries

- If someone may be in immediate danger, contact emergency services now.
- If you may harm yourself or someone else, reach a real person and crisis support now.
- Use qualified professionals for mental health, medical, legal, financial, or safety decisions.
- Use qualified teachers for meditation technique questions.
- Do not paste secrets, credentials, private third-party information, legal documents, or medical records into optional AI features.

## Run locally

```bash
npm install
npm run dev
```

Then open the local URL shown by Vite.

## Checks

```bash
npm test
npm run build
npm run test:e2e
```

## Public demo

Public GitHub Pages evidence was checked unauthenticated on 2026-07-04:

- `https://almost-magic.github.io/socrates-and-donuts/`

This confirms a reachable page, not release readiness. Review current app behaviour, licence, repo shape, safety wording, and browser QA before public promotion.

## Release blockers

- `BLOCKED_RELEASE_LICENSE_MISSING`: no release licence is present at repo root.
- `BLOCKED_RELEASE_REPO_HYGIENE`: the repo contains broad AMTL/Elaine workspace material alongside the Socrates app.
- `BLOCKED_MERGE_RENAME_DECISION`: confirm whether this remains Socrates and Donuts, merges into Dhamma Mirror, or becomes a separate named tool.

## Good first issues

- decide and document the Socrates/Dhamma relationship;
- add a release licence after owner approval;
- remove unrelated workspace/archive material from a clean product repo;
- add tests for the vault, crisis banner, and local storage;
- add desktop/mobile screenshots to the README.
