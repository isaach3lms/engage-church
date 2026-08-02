"""
Engage Church Bloomfield
Flask site built by Between Sundays Agency.

All editable content lives in the CONTENT section below. Changing copy,
staff, or ministries does not require touching templates.
"""

import os
import re
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

# ---------------------------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------------------------

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "website@engagebloomfield.com")
CONTACT_TO = os.environ.get("CONTACT_TO", "info@engagebloomfield.com")

# Sermons. Set YOUTUBE_CHANNEL_ID once the channel exists (starts with "UC").
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")
YOUTUBE_CHANNEL_URL = os.environ.get(
    "YOUTUBE_CHANNEL_URL", "https://www.youtube.com/@engagebloomfield"
)

# Giving. Currently the existing Tithe.ly link. Replace when Engage's own is live.
GIVE_URL = os.environ.get(
    "GIVE_URL",
    "https://tithe.ly/give_new/www/#/tithely/give-one-time/1449948",
)

# Kids pre-check. Blank hides the button rather than shipping a dead link.
PRECHECK_URL = os.environ.get("PRECHECK_URL", "")

# ---------------------------------------------------------------------------
# CONTENT
# ---------------------------------------------------------------------------

CHURCH = {
    "name": "Engage Church",
    "city": "Bloomfield",
    "tagline": "Engage with God. Engage in community.",
    "intro": (
        "We exist to help people take their next step with Jesus and live out "
        "their faith together. Everyone is welcome. You belong here."
    ),
    "address": "501 Christian St, Bloomfield, MO 63825",
    "map_url": "https://maps.app.goo.gl/aeivWH3TNEx2uPQm8",
    "phone_display": "(573) 568-3494",
    "phone_tel": "+15735683494",
    "email": "info@engagebloomfield.com",
    "facebook": "",
    "instagram": "",
    "youtube": YOUTUBE_CHANNEL_URL,
    # Legal entity name for the footer. CONFIRM with the church before launch.
    "legal_name": "Engage Church",
}

SERVICES = [
    {"day": "Sunday", "time": "10:30 AM", "note": "Worship Center"},
    {"day": "Wednesday", "time": "6:00 PM", "note": "All ages"},
]

# The brand board's six values, used as the Home page belief row.
VALUES = [
    ("Welcoming", "You can walk in without knowing anyone and still be glad you came."),
    ("Connected", "Faith was never meant to be worked out alone."),
    ("Forward moving", "There is always a next step, and it is always reachable."),
    ("Bold", "We say what Scripture says, plainly and without apology."),
    ("Faith centered", "Jesus is the point. Everything else follows from that."),
    ("Genuine", "No performance, no pretending, no polished version required."),
]

# Staff. Split into two groups so the page reads as an organization, not a roster.
STAFF_PASTORAL = [
    {
        "name": "Patrick Grissom",
        "role": "Lead Pastor",
        "spouse": "Heather Grissom",
        "spouse_role": "Worship Pastor",
        "photo": "staff/grissom.jpg",
    },
    {
        "name": "Lindy Parker",
        "role": "Children's Pastor",
        "photo": "staff/parker.jpg",
    },
    {
        "name": "Chris Battles",
        "role": "Youth Pastor",
        "spouse": "Amy Battles",
        "photo": "staff/battles-chris.jpg",
    },
]

STAFF_LEADERSHIP = [
    {
        "name": "David Battles",
        "role": "Elder",
        "spouse": "Sherry Battles",
        "photo": "staff/battles-david.jpg",
    },
    {
        "name": "Joel and Cory Battles",
        "role": "Office Admins",
        "photo": "staff/battles-joel-cory.jpg",
    },
]

# Ministries. Times marked TBC need church confirmation before launch.
MINISTRIES = [
    {
        "slug": "kids",
        "name": "Kids",
        "when": "Sundays, 10:30 AM",
        "ages": "Birth through 5th grade",
        "blurb": (
            "Kids learn the same thing the adults are learning, in a room built "
            "for their age. Check-in takes about two minutes and only the adult "
            "who dropped a child off can pick them up."
        ),
    },
    {
        "slug": "youth",
        "name": "Youth",
        "when": "Wednesdays, 6:00 PM",
        "ages": "6th through 12th grade",
        "blurb": (
            "Games, teaching, and small group conversation. Students are allowed "
            "to ask hard questions here, and they do."
        ),
    },
    {
        "slug": "small-groups",
        "name": "Small Groups",
        "when": "Various days and times",
        "ages": "Adults",
        "blurb": (
            "Eight to twelve people, a living room, and an honest conversation "
            "about Scripture and life. This is where most people stop feeling "
            "like a visitor."
        ),
    },
    {
        "slug": "worship",
        "name": "Worship",
        "when": "Rehearsal Wednesdays, 6:00 PM",
        "ages": "Musicians, vocalists, and tech",
        "blurb": (
            "Singers, players, sound, and screens. If you can serve once a month, "
            "there is a place for you on this team."
        ),
    },
    {
        "slug": "mens-conference",
        "name": "Men's Conference",
        "when": "Annual",
        "ages": "Men, all ages",
        "blurb": (
            "One weekend a year set aside for teaching, worship, and the kind of "
            "conversation men rarely make time for."
        ),
    },
    {
        "slug": "womens-conference",
        "name": "Women's Conference",
        "when": "Annual",
        "ages": "Women, all ages",
        "blurb": (
            "A weekend built for rest, teaching, and connection with women across "
            "every stage of life."
        ),
    },
]

# Contact routing. Every value can point at its own address later without a
# template change. Anything falling back to CONTACT_TO gets a tagged subject.
CONTACT_ROUTES = {
    "visit": ("Plan a visit", CONTACT_TO),
    "kids": ("Kids", CONTACT_TO),
    "youth": ("Youth", CONTACT_TO),
    "small-groups": ("Small Groups", CONTACT_TO),
    "worship": ("Worship", CONTACT_TO),
    "prayer": ("Prayer request", CONTACT_TO),
    "general": ("General question", CONTACT_TO),
}

BELIEFS = [
    ("God", "There is one true, living, and eternal God, revealed as Father, Son, and Holy Spirit."),
    ("The Bible", "The Old and New Testaments are the inspired and infallible Word of God, and the only reliable guide of Christian faith and conduct."),
    ("Man", "God created man in his own image to bring Him honor through obedience. When man disobeyed, he became fallen and sinful, unable to save himself. Infants are in the covenant of God's grace, and all people become accountable to God when they reach a state of moral responsibility."),
    ("Salvation", "Salvation has been provided for all people through the life, death, resurrection, ascension, and intercession of Jesus Christ, and is received only through repentance and faith in Him."),
    ("Christian Duties", "Christians live faithfully by serving in and through the local church, praying diligently, witnessing earnestly, showing loving kindness, giving as God prospers, and conducting themselves in a way that brings glory to God."),
    ("The Church", "The Church Universal is the body of Christ and the fellowship of all believers. A local church is a fellowship of Christians voluntarily banded together for worship, nurture, and service."),
    ("Ordinances", "Baptism and the Lord's Supper are ordinances instituted by Christ. The biblical mode of baptism is immersion, symbolizing the internal decision to follow Christ. The Lord's Supper is open to all Christians."),
    ("The Lord's Day", "The first day of the week is set apart for worshiping God, witnessing for Christ, and ministering to the needs of others."),
    ("Last Things", "We believe in the personal return of Jesus Christ and the bodily resurrection of the dead. God will judge all people by Jesus Christ, rewarding the righteous with eternal life and banishing the unrighteous to everlasting punishment."),
    ("Marriage and Sexuality", "Marriage has one meaning: a single, exclusive union of one man and one woman, sanctioned by God as delineated in Scripture. Sexual intimacy is intended to occur only within that union."),
]

VISIT_FAQS = [
    ("How long is the service?",
     "About seventy minutes, start to finish."),
    ("What should I wear?",
     "Whatever you own. Some people wear jeans, some wear a tie. Nobody will notice either way."),
    ("Will I be singled out?",
     "No. You will not be asked to stand up, introduce yourself, or fill anything out. If you want to talk to someone, we are easy to find. If you would rather slip in and slip out, that is completely fine."),
    ("What about the offering?",
     "There is no giving expectation for guests. The plate is passed and passing it along is normal."),
    ("Where do I park and which door?",
     "Park in the main lot off Christian Street and use the front entrance. Someone will be at the door."),
    ("What happens with my kids?",
     "Kids check in at the desk just inside the main entrance. You get a matching tag, and only you can pick them up. If it is your first time, arrive about ten minutes early and someone will walk you through it."),
]

# ---------------------------------------------------------------------------
# SERMONS
# ---------------------------------------------------------------------------

_sermon_cache = {"at": 0.0, "items": []}
SERMON_CACHE_SECONDS = 3600


def fetch_sermons(limit=12):
    """Latest videos from the church YouTube channel via its public RSS feed.

    No API key and no quota. Returns at most the 15 most recent uploads,
    which is what YouTube publishes on the feed.
    """
    if not YOUTUBE_CHANNEL_ID:
        return []

    now = time.time()
    if _sermon_cache["items"] and now - _sermon_cache["at"] < SERMON_CACHE_SECONDS:
        return _sermon_cache["items"][:limit]

    try:
        import feedparser
        feed_url = (
            "https://www.youtube.com/feeds/videos.xml?channel_id="
            + YOUTUBE_CHANNEL_ID
        )
        parsed = feedparser.parse(feed_url)
        items = []
        for entry in parsed.entries:
            video_id = entry.get("yt_videoid")
            if not video_id:
                continue
            published = ""
            if getattr(entry, "published_parsed", None):
                published = datetime(
                    *entry.published_parsed[:6], tzinfo=timezone.utc
                ).strftime("%B %-d, %Y")
            items.append({
                "id": video_id,
                "title": entry.get("title", "Sermon"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumb": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "published": published,
            })
        if items:
            _sermon_cache["at"] = now
            _sermon_cache["items"] = items
        return items[:limit]
    except Exception as exc:  # never let a feed outage take the page down
        app.logger.warning("Sermon feed unavailable: %s", exc)
        return _sermon_cache["items"][:limit]


# ---------------------------------------------------------------------------
# MAIL
# ---------------------------------------------------------------------------

def send_mail(to_addr, subject, body, reply_to=None):
    """Send through the Resend SMTP relay."""
    if not RESEND_API_KEY:
        app.logger.warning("RESEND_API_KEY missing. Message not sent:\n%s", body)
        return False

    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.resend.com", 587, timeout=15) as server:
            server.starttls()
            server.login("resend", RESEND_API_KEY)
            server.send_message(msg)
        return True
    except Exception as exc:
        app.logger.error("Resend delivery failed: %s", exc)
        return False


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def handle_form(default_topic="general"):
    """Validate and deliver a contact submission. Returns (ok, message)."""
    # Honeypot. Real people leave this empty.
    if request.form.get("website", "").strip():
        return True, "Thanks. We will be in touch soon."

    # Timing check. Bots submit instantly.
    try:
        elapsed = time.time() - float(request.form.get("t", "0"))
    except ValueError:
        elapsed = 0
    if elapsed < 2.5:
        return False, "That submission came through too fast. Please try again."

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    topic = request.form.get("topic", default_topic).strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        return False, "Please add your name and a short message."
    if not EMAIL_RE.match(email):
        return False, "That email address does not look right. Please check it."

    label, recipient = CONTACT_ROUTES.get(topic, CONTACT_ROUTES["general"])

    body = (
        f"New message from engagebloomfield.com\n\n"
        f"Topic:   {label}\n"
        f"Name:    {name}\n"
        f"Email:   {email}\n"
        f"Phone:   {phone or 'not provided'}\n\n"
        f"{message}\n"
    )
    sent = send_mail(recipient, f"[{label}] {name}", body, reply_to=email)

    if sent:
        send_mail(
            email,
            f"We got your message, {name.split()[0]}",
            (
                f"Hi {name.split()[0]},\n\n"
                "Thanks for reaching out to Engage Church. Someone will get back "
                "to you within a couple of days.\n\n"
                "If it is urgent, call us at "
                f"{CHURCH['phone_display']}.\n\n"
                "Engage Church\n"
                f"{CHURCH['address']}\n"
            ),
        )
        return True, "Thanks. We got your message and will be in touch soon."

    return False, (
        "Something went wrong sending that. Please call us at "
        f"{CHURCH['phone_display']} and we will help."
    )


# ---------------------------------------------------------------------------
# TEMPLATE GLOBALS
# ---------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    return {
        "church": CHURCH,
        "services": SERVICES,
        "give_url": GIVE_URL,
        "precheck_url": PRECHECK_URL,
        "youtube_url": YOUTUBE_CHANNEL_URL,
        "contact_routes": CONTACT_ROUTES,
        "now": datetime.now(),
        "form_ts": time.time(),
    }


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "home.html",
        values=VALUES[:3],
        ministries=MINISTRIES[:3],
        sermons=fetch_sermons(limit=1),
    )


@app.route("/visit", methods=["GET", "POST"])
def visit():
    if request.method == "POST":
        ok, msg = handle_form(default_topic="visit")
        flash(msg, "success" if ok else "error")
        if ok:
            return redirect(url_for("visit") + "#connect")
    return render_template("visit.html", faqs=VISIT_FAQS)


@app.route("/about")
def about():
    return render_template(
        "about.html",
        pastoral=STAFF_PASTORAL,
        leadership=STAFF_LEADERSHIP,
        beliefs=BELIEFS,
        values=VALUES,
    )


@app.route("/ministries", methods=["GET", "POST"])
def ministries():
    if request.method == "POST":
        ok, msg = handle_form(default_topic="general")
        flash(msg, "success" if ok else "error")
        if ok:
            return redirect(url_for("ministries") + "#connect")
    return render_template("ministries.html", ministries=MINISTRIES)


@app.route("/sermons")
def sermons():
    return render_template("sermons.html", sermons=fetch_sermons(limit=15))


@app.route("/give")
def give():
    return render_template("give.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        ok, msg = handle_form(default_topic="general")
        flash(msg, "success" if ok else "error")
        if ok:
            return redirect(url_for("contact") + "#connect")
    return render_template("contact.html")


@app.route("/next-steps")
def next_steps():
    """Scaffolded. Kept out of the nav until baptism, membership, and
    pathway content is delivered by the church."""
    return render_template("next_steps.html")


# Legacy URL map from bloomfieldgb.com. Keeps old links alive after cutover.
LEGACY_REDIRECTS = {
    "/connect": "ministries",
    "/form/contact": "contact",
    "/form/plan-a-visit": "visit",
    "/precheck": "visit",
}


@app.route("/connect")
@app.route("/form/contact")
@app.route("/form/plan-a-visit")
@app.route("/precheck")
def legacy():
    target = LEGACY_REDIRECTS.get(request.path)
    if not target:
        abort(404)
    return redirect(url_for(target), code=301)


@app.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\nAllow: /\n\n"
        "Sitemap: https://engagebloomfield.com/sitemap.xml\n"
    )
    return app.response_class(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    base = "https://engagebloomfield.com"
    paths = ["/", "/visit", "/about", "/ministries", "/sermons", "/give", "/contact"]
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in paths)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return app.response_class(xml, mimetype="application/xml")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
