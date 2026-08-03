# Engage Church Bloomfield

Flask site built by Between Sundays Agency. No database. All content lives in
`app.py` under the CONTENT section, so copy edits never touch templates.

## Run locally

```bash
pip install -r requirements.txt
python app.py           # http://127.0.0.1:5000
```

## Deploy to Render

Push to GitHub, connect the repo, and set the environment variables below in the
Render dashboard. The dashboard is the source of truth for env vars. Do not
re-sync `render.yaml` against a running service.

| Variable | Required | Notes |
|---|---|---|
| `SECRET_KEY` | Yes | Any long random string. Render can generate it |
| `RESEND_API_KEY` | Yes | Resend SMTP relay password. Without it, forms log instead of sending |
| `MAIL_FROM` | Yes | Must be on a domain verified in Resend |
| `CONTACT_TO` | Yes | Where form submissions land |
| `YOUTUBE_CHANNEL_ID` | No | Blank sends every sermon link straight to YouTube. Set it to `UCr-CovLjIcJDxa9hb4YdIMg` and the links switch to the on-site Sermons page, populated from the feed |
| `YOUTUBE_CHANNEL_URL` | No | Public channel link used on buttons |
| `GIVE_URL` | No | Giving platform link. Currently the legacy Tithe.ly URL |
| `PRECHECK_URL` | No | Kids pre-check link. Blank hides the button rather than shipping a dead link |

## Editing content

Everything below is a plain Python structure in `app.py`:

- `CHURCH` — name, address, phone, email, legal name for the footer
- `SERVICES` — service days and times
- `VALUES` — the six brand values
- `STAFF_PASTORAL` / `STAFF_LEADERSHIP` — two groups, rendered as separate sections
- `MINISTRIES` — name, audience, meeting time, description
- `VISIT_FAQS` — the Plan Your Visit questions
- `BELIEFS` — statement of faith
- `CONTACT_ROUTES` — form topics and the address each one delivers to

To send a ministry's inquiries to its own inbox, change that entry's second
value in `CONTACT_ROUTES`. Nothing else needs to change.

## Sermons

Every sermon link on the site (header, hero button, home section, footer) points
at one shared destination controlled by `sermons_url`. With `YOUTUBE_CHANNEL_ID`
unset, that destination is the YouTube channel and the links open in a new tab.
Set the channel ID and they all switch to the on-site `/sermons` page with no
template changes.

Pulled from the channel's public RSS feed. No API key, no quota, cached one
hour. YouTube publishes the 15 most recent uploads on that feed, so the page
shows a rolling quarter and links to the full archive on YouTube. If a
searchable archive by series is needed later, that means switching to the
YouTube Data API and is a separate scope item.

## Forms

Delivered through the Resend SMTP relay. Protections in place:

- Hidden honeypot field
- Minimum time-on-form check of 2.5 seconds
- Server-side email format validation
- `Reply-To` set to the submitter so staff can hit reply
- Automatic confirmation email back to the submitter

## Legacy redirects

`/connect`, `/form/contact`, `/form/plan-a-visit`, and `/precheck` 301 to their
new equivalents. Add server-level redirects from `bloomfieldgb.com` to
`engagebloomfield.com` at DNS or proxy level during cutover. Keep the old domain
registered.

## Placeholder content to replace before launch

| Item | Location | Status |
|---|---|---|
| Ministry meeting times | `MINISTRIES` | Needs church confirmation |
| Small Groups day and time | `MINISTRIES` | Currently "Various days and times" |
| Legal entity name | `CHURCH["legal_name"]` | Needs confirmation for footer and giving receipts |
| Parking and entrance detail | `VISIT_FAQS` | Written from assumption, confirm the lot and door |
| Facebook and Instagram links | `CHURCH` | Blank until new accounts exist |
| Photos | `static/img/photos/` | Four supplied images. `preaching.jpg` is the Home sermon section fallback and shows once the YouTube channel is set. The other three show people from behind. Replace after the Sunday shoot |
| Staff photo, Joel and Cory | `static/img/staff/` | Lower resolution than the others. Reshoot |
| Next Steps page | `/next-steps` | Scaffolded and kept out of the nav until content is delivered |

## Pre-launch checklist

- [ ] Verify sending domain in Resend
- [ ] Set all required env vars in Render
- [ ] Submit a test message through each form and confirm delivery plus confirmation email
- [ ] Confirm ministry times and parking detail with the church
- [ ] Add YouTube channel ID
- [ ] Rename the Google Business Profile, do not create a second listing
- [ ] Point `engagebloomfield.com` at Render, redirect `bloomfieldgb.com`
- [ ] Export all media from The Church Co before that subscription lapses
