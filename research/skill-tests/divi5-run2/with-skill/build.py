import sys, json
sys.path.insert(0, "/Volumes/Content/projects/TFM/Divi-genie/Skill/divi-page-builder/scripts")
import divi5_blocks as d
V = "5.13.1"
def var(kind, name):
    t = "color" if kind == "c" else "content"
    return '$variable({"type":"%s","value":{"name":"%s","settings":{}}})$' % (t, name)
NAVY, ORANGE, ORLT = var("c","gcid-r6navy0001"), var("c","gcid-r6orange001"), var("c","gcid-r6orangelt1")
RAD, PAD = var("v","gvid-r6radius01"), var("v","gvid-r6secpad01")
def B(name, attrs, children=None):
    a = dict(attrs); a["builderVersion"] = V
    return d.new_block(name, a, children)
LAY = {"desktop": {"value": {"display": "block"}}}
def section(label, bg, pad, children):
    dec = {"layout": LAY, "background": {"desktop": {"value": {"color": bg}}}, "spacing": pad}
    return B("section", {"module": {"meta": {"adminLabel": {"desktop": {"value": label}}}, "decoration": dec}}, children)
def spad(t, tb, ph):
    f = lambda v: {"value": {"padding": {"top": v, "bottom": v, "syncVertical": "on", "syncHorizontal": "off"}}}
    return {"desktop": f(t), "tablet": f(tb), "phone": f(ph)}
def row(struct, children, sizing=None):
    dec = {"layout": LAY}
    if sizing: dec["sizing"] = {"desktop": {"value": sizing}}
    return B("row", {"module": {"advanced": {"columnStructure": {"desktop": {"value": struct}}}, "decoration": dec}}, children)
def col(t, children):
    return B("column", {"module": {"advanced": {"type": {"desktop": {"value": t}}}, "decoration": {"layout": LAY}}}, children)
def h2(text):
    return B("heading", {"title": {"innerContent": {"desktop": {"value": text}}, "decoration": {"font": {"font": {
        "desktop": {"value": {"headingLevel": "h2", "family": "Montserrat", "weight": "700", "color": NAVY, "size": "40px"}},
        "tablet": {"value": {"size": "32px"}}, "phone": {"value": {"size": "28px"}}}}}}})
CENTER = {"module": {"decoration": {"sizing": {"desktop": {"value": {"maxWidth": "720px", "alignment": "center"}}}}}}
def btn(text, url):
    return {"button": {"innerContent": {"desktop": {"value": {"text": text, "linkUrl": url}}},
        "decoration": {"button": {"desktop": {"value": {"enable": "on"}}},
            "background": {"desktop": {"value": {"color": ORANGE}, "hover": {"color": ORLT}}},
            "font": {"font": {"desktop": {"value": {"family": "Lato", "weight": "400", "color": NAVY, "size": "16px"}}}},
            "border": {"desktop": {"value": {"styles": {"all": {"width": "0px"}}, "radius": {"sync": "on", "topLeft": RAD, "topRight": RAD, "bottomRight": RAD, "bottomLeft": RAD}}}}}}}

# 1 Hero
hero_btn = btn("Call (305) 555-0100", "tel:+13055550100")
hero_btn["module"] = {"advanced": {"alignment": {"desktop": {"value": "center"}}}}
hero_btn["modulePreset"] = ["11111111-2222-3333-4444-555555555555"]
hero = section("Hero", NAVY, {"desktop": {"value": {"padding": {"top": PAD, "bottom": PAD, "syncVertical": "on", "syncHorizontal": "off"}}}}, [
  row("4_4", [col("4_4", [
    B("heading", dict({"title": {"innerContent": {"desktop": {"value": "Drain Cleaning &amp; Hydro Jetting in Miami"}},
        "decoration": {"font": {"font": {"desktop": {"value": {"headingLevel": "h1", "family": "Montserrat", "weight": "700", "color": "#ffffff", "size": "56px", "lineHeight": "1.1em", "textAlign": "center"}},
            "tablet": {"value": {"size": "42px"}}, "phone": {"value": {"size": "34px"}}}}}}}, **CENTER)),
    B("text", dict({"content": {"innerContent": {"desktop": {"value": "<p>Slow or backed-up drains? We clear kitchen, bathroom and main sewer lines the same day — with camera inspection and a written price before we start.</p>"}},
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Lato", "weight": "400", "color": "#f1f5f9", "size": "18px", "lineHeight": "1.7em", "textAlign": "center"}}}}}}}}, **CENTER)),
    B("button", hero_btn)],
  )], {"width": "90%", "maxWidth": "1200px"})])

# 2 Services
def blurb(title, uni, typ, wt):
    return B("blurb", {"title": {"innerContent": {"desktop": {"value": {"text": title}}},
        "decoration": {"font": {"font": {"desktop": {"value": {"headingLevel": "h3", "family": "Montserrat", "weight": "700", "color": NAVY, "size": "20px"}}}}}},
        "imageIcon": {"innerContent": {"desktop": {"value": {"useIcon": "on", "icon": {"unicode": uni, "type": typ, "weight": wt}}}},
            "advanced": {"color": {"desktop": {"value": ORANGE}}},
            "decoration": {"sizing": {"desktop": {"value": {"alignSelf": "flex-start", "iconFontSize": "56px"}}}}}})
svc = [("Kitchen drains", "&#xe005;", "fa", "900"), ("Bathroom drains", "&#xf2cc;", "fa", "900"),
       ("Main sewer lines", "&#xf773;", "fa", "900"), ("Hydro jetting", "&#xf043;", "fa", "900"),
       ("Camera inspection", "&#xf030;", "fa", "900")]
bl = [blurb(*s) for s in svc]
services = section("Services", "#ffffff", spad("90px", "60px", "45px"), [
  row("4_4", [col("4_4", [h2("Our Drain Cleaning Services")])]),
  row("1_3,1_3,1_3", [col("1_3", [b]) for b in bl[:3]]),
  row("1_2,1_2", [col("1_2", [b]) for b in bl[3:]])])

# 3 Stats
def counter(num, title, pct=False):
    n = {"innerContent": {"desktop": {"value": num}},
         "decoration": {"font": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "color": NAVY, "size": "56px"}},
             "tablet": {"value": {"size": "40px"}}, "phone": {"value": {"size": "32px"}}}}}}
    n["advanced"] = {"enablePercentSign": {"desktop": {"value": "off"}}}
    return B("number-counter", {"number": n, "title": {"innerContent": {"desktop": {"value": title}},
        "decoration": {"font": {"font": {"desktop": {"value": {"headingLevel": "h3", "family": "Lato", "weight": "400", "color": "#475569", "size": "18px"}}}}}}})
stats = section("By The Numbers", "#f1f5f9", spad("70px", "50px", "40px"), [
  row("4_4", [col("4_4", [h2("Drain Cleaning by the Numbers")])]),
  row("1_3,1_3,1_3", [col("1_3", [counter("25+", "Years in business")]),
                      col("1_3", [counter("60", "Minute response")]),
                      col("1_3", [counter("4.9", "★ from 1,200 reviews")])])])

# 4 FAQ
pairs = [("Is hydro jetting safe for old pipes?", "We inspect with a camera first and only jet pipes that can take it."),
         ("Do you charge extra at night?", "No — same price 24/7.")]
ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
script = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
fnt = lambda size, extra=None: {"desktop": {"value": dict({"family": "Montserrat", "weight": "700", "color": NAVY, "size": size}, **(extra or {}))}}
acc = B("accordion", {
  "title": {"decoration": {"font": {"font": fnt("18px", {"headingLevel": "h3"})}}},
  "closedToggle": {"decoration": {"font": {"font": fnt("18px")}}},
  "openToggle": {"decoration": {"font": {"font": {"desktop": {"value": {"color": NAVY}}}}}},
  "closedToggleIcon": {"decoration": {"icon": {"desktop": {"value": {"color": ORANGE}}}}},
  "content": {"decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Lato", "weight": "400", "color": "#475569", "size": "16px", "lineHeight": "1.7em"}}}}}}}},
  [B("accordion-item", dict({"title": {"innerContent": {"desktop": {"value": q}}}, "content": {"innerContent": {"desktop": {"value": "<p>%s</p>" % a}}}},
        **({"module": {"advanced": {"open": {"desktop": {"value": "on"}}}}} if i == 0 else {}))) for i, (q, a) in enumerate(pairs)])
faq = section("FAQ", "#ffffff", spad("90px", "60px", "45px"), [
  row("4_4", [col("4_4", [h2("Drain Cleaning FAQ"), acc, B("code", {"content": {"innerContent": {"desktop": {"value": script}}}})])])])

# 5 CTA band
cta_btn = btn("Call (305) 555-0100", "tel:+13055550100")
cta = B("cta", {"title": {"innerContent": {"desktop": {"value": "Need a Drain Cleared Today?"}},
      "decoration": {"font": {"font": {"desktop": {"value": {"headingLevel": "h4", "family": "Montserrat", "weight": "700", "color": "#ffffff", "size": "30px"}}}}}},
    "content": {"innerContent": {"desktop": {"value": "<p>Call now for same-day service and a written price before we start.</p>"}},
      "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Lato", "weight": "400", "color": "#f1f5f9", "size": "18px"}}}}}}},
    "button": cta_btn["button"],
    "module": {"decoration": {"background": {"desktop": {"value": {"color": NAVY}}},
      "spacing": {"desktop": {"value": {"padding": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}}}}}})
band = section("Free Quote CTA", NAVY, spad("70px", "50px", "40px"), [row("4_4", [col("4_4", [cta])])])

page = d.wrap_placeholder([hero, services, stats, faq, band])
open("page.html", "w").write(d.serialize(page))
print("ok")
