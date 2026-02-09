# Contributing to BesideYou 🌿

BesideYou was built in Australia for people navigating cancer. But cancer doesn't respect borders, and neither should support.

If you want to bring BesideYou to your country, your language, or your cancer community — this project was designed for you to do exactly that.

## How you can help

### "I want to add my country's resources"

The easiest and most impactful contribution. Open `data.js` and:

1. Update the `CRISIS` object with your country's emergency number and helplines
2. Replace the `RESOURCES` array with local support services
3. Submit a pull request, or fork and deploy your own version

**What we need for each resource:**
- `name` — the organisation's name
- `desc` — what they do, in plain language (one sentence)
- `cat` — category: `emotional`, `practical`, `financial`, `medical`, or `carer`
- `who` — who it's for: `patients`, `carers`, or `patients,carers`
- `url` — their website
- `phone` — phone number (optional)

### "I want to translate BesideYou"

Translation is more than changing words. The tone of BesideYou is its soul — gentle, realistic, never patronising.

**Guidelines:**
- "You are still here. That matters." — Translate the feeling, not just the words.
- Avoid clinical language where the original uses plain language.
- Keep sentences short. People reading this may be exhausted, frightened, or grieving.
- "No pressure" and "skip anything you like" are not throwaway phrases — they are therapeutic. Preserve them.
- Test your translation by reading it aloud as if you were speaking to a friend who just received a diagnosis.

All translatable text is in `index.html` (UI text) and `data.js` (content). The CSS and `app.js` should not need changes.

### "I want to create a cancer-specific version"

Fork the repo and customise:
- Add glossary terms specific to that cancer type
- Adjust the symptom suggestions in the check-in and tracker
- Add cancer-specific resources
- Adjust the welcome text and vignette

Example: A version for breast cancer might add terms like "Lumpectomy", "HER2", "Tamoxifen" and link to Breast Cancer Network Australia.

### "I want to improve the core app"

Wonderful. Here's the architecture:

- `index.html` — All screens and modals. Single page app, no routing.
- `style.css` — All styles. CSS variables for theming. Dark/light mode.
- `data.js` — All content. Glossary terms, resources, crisis numbers.
- `app.js` — All logic. State management, rendering, encryption.

**Principles:**
- No frameworks. No build tools. No npm. Someone should be able to clone and open `index.html`.
- No server dependencies. Everything runs client-side.
- Gentle progressive disclosure. Don't add features that overwhelm.
- Every new feature should work offline and respect the "no data leaves the device" promise.

### "I'm not a developer but I want to help"

You are equally valuable. You can:
- **Review glossary terms** for accuracy and plain-language quality
- **Suggest resources** for your country or region
- **Test the app** on different devices and report issues
- **Share BesideYou** with cancer support organisations, hospitals, or support groups
- **Write or review translations** for accuracy and tone
- **Suggest improvements** to the UX from a patient or carer perspective

If you've been through cancer — as a patient, carer, or supporter — your perspective is the most important contribution of all.

## Code of conduct

This project serves people in one of the most vulnerable moments of their lives. All contributions should reflect that.

- Be kind. Always.
- Respect the tone. This is not a startup — it's a companion.
- Protect privacy. Never add analytics, tracking, or server calls.
- Test your changes. Make sure nothing breaks on mobile.
- Keep it simple. The person using this might be exhausted, scared, or in pain.

## Submitting changes

1. Fork the repo
2. Create a branch (`feature/nz-resources` or `fix/glossary-typo`)
3. Make your changes
4. Test in a browser (just open `index.html`)
5. Submit a pull request with a clear description

For resource additions, include a link to the organisation's website so we can verify.

For translations, include a note about your relationship to the language (native speaker, professional translator, etc.).

## Questions?

Open an issue. There are no stupid questions — especially not about cancer.

---

*The best cancer support tool for your community is the one your community builds.*
