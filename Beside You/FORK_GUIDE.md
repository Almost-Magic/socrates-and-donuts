# Fork Guide: Create BesideYou for Your Community

This guide walks you through creating a version of BesideYou for your country, language, or cancer community. No backend knowledge needed. You'll have a live site in under an hour.

## What you'll need

- A GitHub account (free)
- A text editor (even GitHub's built-in editor works)
- Your country's crisis numbers and cancer support resources

## Step 1: Fork the repo

1. Go to [github.com/almost-magic/beside-you](https://github.com/almost-magic/beside-you)
2. Click **Fork** (top right)
3. You now have your own copy

## Step 2: Edit `data.js`

This is where all the content lives. Open it and change:

### Crisis numbers

```javascript
const CRISIS = {
  emergency: { number: "111", label: "Call 111 Now" },  // NZ example
  lines: [
    { name: "1737", number: "1737", tel: "1737", 
      desc: "Free call or text for mental health support. Available 24/7." },
    { name: "Cancer Society", number: "0800 226 237", tel: "0800226237",
      desc: "Free support from cancer nurses." }
  ]
};
```

### Resources

Replace the `RESOURCES` array with your local services. Follow the format:

```javascript
{ name: "Cancer Society of NZ", desc: "Free support for anyone affected by cancer.",
  cat: "emotional", who: "patients,carers", url: "https://www.cancer.org.nz",
  phone: "0800 226 237" }
```

Categories: `emotional`, `practical`, `financial`, `medical`, `carer`

### Glossary

The medical glossary is universal — most terms don't need changing. You might want to:
- Add terms specific to your healthcare system
- Adjust any Australia-specific references in definitions

## Step 3: Edit `index.html`

Change these sections:
- The emergency number in the **crisis screen** (search for `tel:000` and replace)
- The crisis support box in the **resources screen**
- Any references to "Australian" in resource descriptions
- The footer attribution (if you want to credit your organisation)

If translating to another language, translate all visible text in `index.html`. The `app.js` logic does not need translation.

## Step 4: Deploy

1. Go to your fork's **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Select **main** branch, **/ (root)** folder
4. Click **Save**
5. Your site will be live at `https://yourusername.github.io/beside-you/`

That's it. No build step. No server. No hosting costs.

## Step 5 (optional): Rename

If you want a different name or URL:
1. Rename the repo in Settings
2. The GitHub Pages URL will update automatically

## Testing

Open `index.html` in your browser. Click through every screen. Check that:
- [ ] Crisis numbers are correct and tap-to-call works
- [ ] Resources link to the right organisations
- [ ] Glossary terms display correctly
- [ ] Export/import still works
- [ ] Dark and light themes both look right

## Keeping up to date

To pull in improvements from the main BesideYou repo:
1. Go to your fork on GitHub
2. Click **Sync fork** → **Update branch**

This won't overwrite your `data.js` changes unless there's a conflict.

## Need help?

Open an issue on the main repo. We're here.

---

*The best cancer support tool for your community is the one your community builds.*
