"""Render the @newsmacro115 carousel (1080 x 1350 PNG) from a daily content.json.

Usage: python3 kit/slides.py content.json OUT_DIR
Writes OUT_DIR/01.png ... NN.png, OUT_DIR/contact.png and prints a JSON report.
Exit code 2 if any slide overflows (text too long): shorten the text and re-run.

Validated style (3 Nov 2026): white background, cover and last slide in electric
blue, huge uppercase Archivo titles, IBM Plex Mono labels, black rules, square
corners. Do not change colours, fonts or layout.
"""
import html, json, math, pathlib, sys

KIT = pathlib.Path(__file__).resolve().parent
FONTS = KIT / "fonts"

INK, BLUE, RED, GREEN, GREY, PALE = "#0B0B0C", "#2340FF", "#D92D16", "#00875A", "#5C5C66", "#EEF1FF"
DIR_COLOR = {"down": RED, "up": GREEN, "flat": BLUE, "neutral": INK}
MONO = "'IBM Plex Mono', monospace"


def e(s):
    """Escape text and keep French spacing: thin non-breaking before % $ pb h."""
    s = html.escape(str(s))
    for unit in (" %", " $", " pb", " h", " Md$", " €"):
        s = s.replace(unit, "&nbsp;" + unit.strip())
    return s


def arrow(direction, color, size=48, stroke=2.6):
    paths = {
        "down": '<path d="M12 4v15"></path><path d="M6 13l6 6 6-6"></path>',
        "up": '<path d="M12 20V5"></path><path d="M6 11l6-6 6 6"></path>',
        "flat": '<path d="M4 12h15"></path><path d="M13 6l6 6-6 6"></path>',
    }
    p = paths.get(direction, paths["flat"])
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="square" aria-hidden="true" style="flex:none">{p}</svg>')


def fr_num(x, dec=1):
    s = f"{x:.{dec}f}".replace(".", ",")
    return s.replace("-", "−")


# ---------------------------------------------------------------- blocks
def b_rows(b):
    out = [f'<div style="display:flex;flex-direction:column;border-top:3px solid {INK}">']
    for r in b["rows"]:
        d = r.get("dir", "flat")
        c = DIR_COLOR.get(d, INK)
        out.append(
            f'<div data-row style="display:flex;justify-content:space-between;align-items:center;gap:24px;padding:40px 0;border-bottom:3px solid {INK}">'
            f'<span style="flex:1;min-width:0;font-size:48px;font-weight:700">{e(r["label"])}</span>'
            f'<span data-shrink style="display:flex;align-items:center;gap:16px;font-size:56px;font-weight:800;color:{c};white-space:nowrap;font-variant-numeric:tabular-nums">{arrow(d, c)}{e(r["value"])}</span>'
            f'</div>')
    out.append("</div>")
    return "".join(out)


def b_table6(b):
    out = [f'<div style="display:flex;flex-direction:column;border-top:3px solid {INK}">']
    for r in b["rows"]:
        d = r.get("dir", "flat")
        badge = {"down": RED, "up": GREEN}.get(d, GREY)
        hl = r.get("highlight")
        out.append(
            f'<div data-row style="display:flex;align-items:center;gap:28px;padding:24px 0;border-bottom:2px solid {INK};{"background:" + PALE if hl else ""}">'
            f'<span style="flex:1;min-width:0;{"padding-left:16px;" if hl else ""}font-size:38px;font-weight:{800 if hl else 600}">{e(r["label"])}</span>'
            f'<span data-shrink style="width:270px;flex:none;text-align:right;font-size:50px;font-weight:800;white-space:nowrap;font-variant-numeric:tabular-nums">{e(r["level"])}</span>'
            f'<span data-shrink style="width:190px;flex:none;box-sizing:border-box;padding:10px 0;text-align:center;background:{badge};color:#FFFFFF;font-family:{MONO};font-size:30px;font-weight:600;white-space:nowrap">{e(r["change"])}</span>'
            f'</div>')
    out.append("</div>")
    return "".join(out)


def b_figure(b):
    c = DIR_COLOR.get(b.get("dir", "neutral"), INK)
    sub = f'<span style="font-size:40px;font-weight:600">{e(b["subtitle"])}</span>' if b.get("subtitle") else ""
    return (f'<div style="display:flex;flex-direction:column;gap:10px">'
            f'<span data-fit="1" style="font-size:230px;font-weight:900;line-height:0.9;letter-spacing:-0.04em;color:{c};white-space:nowrap;font-variant-numeric:tabular-nums">{e(b["value"])}</span>'
            f'{sub}</div>')


def nice_ticks(lo, hi, n=4):
    span = hi - lo
    raw = span / (n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=10 * mag)
    start = math.floor(lo / step) * step
    ticks = [start + i * step for i in range(n + 2)]
    while ticks[-2] >= hi and len(ticks) > 2:
        ticks.pop()
    end = ticks[-1]
    return start, end, [t for t in ticks if t <= end + 1e-9]


def b_range(b):
    """Positions of up to 4 values on a shared scale. roles: before / main / now."""
    pts = b["points"]
    vals = [p["value"] for p in pts]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.15 or abs(hi) * 0.02 or 1
    start, end, ticks = nice_ticks(lo - pad, hi + pad)
    unit = b.get("unit", "")
    dec = b.get("tick_decimals", 0)
    main_c = DIR_COLOR.get(b.get("dir", "down"), RED)
    out = [f'<div style="display:flex;flex-direction:column;gap:30px;padding-top:36px;border-top:3px solid {INK}">']
    for p in pts:
        role = p.get("role", "before")
        c = {"before": INK, "main": main_c, "now": BLUE}.get(role, INK)
        pos = (p["value"] - start) / (end - start) * 100
        vcol = "" if role == "before" else f"color:{c};"
        out.append(
            f'<div style="display:flex;align-items:center;gap:24px">'
            f'<span style="width:180px;flex:none;font-family:{MONO};font-size:26px;font-weight:600;text-transform:uppercase">{e(p["label"])}</span>'
            f'<div style="flex:1;position:relative;height:32px"><div style="position:absolute;left:0;right:0;top:14px;height:4px;background:#D8D8DE"></div>'
            f'<div style="position:absolute;left:{pos:.1f}%;top:0;width:32px;height:32px;background:{c};transform:translateX(-50%)"></div></div>'
            f'<span style="width:200px;flex:none;text-align:right;font-size:40px;font-weight:800;{vcol}white-space:nowrap;font-variant-numeric:tabular-nums">{e(p["display"])}</span>'
            f'</div>')
    tk = []
    for i, t in enumerate(ticks):
        pos = (t - start) / (end - start) * 100
        lab = fr_num(t, dec) + (("&nbsp;" + e(unit)) if (unit and i == len(ticks) - 1) else "")
        if i == 0:
            tk.append(f'<span style="position:absolute;left:0;top:0">{lab}</span>')
        elif i == len(ticks) - 1:
            tk.append(f'<span style="position:absolute;right:0;top:0">{lab}</span>')
        else:
            tk.append(f'<span style="position:absolute;left:{pos:.2f}%;top:0;transform:translateX(-50%)">{lab}</span>')
    out.append(
        f'<div style="display:flex;align-items:center;gap:24px"><span style="width:180px;flex:none"></span>'
        f'<div style="flex:1;position:relative;height:30px;font-family:{MONO};font-size:22px;color:{GREY};font-variant-numeric:tabular-nums">{"".join(tk)}</div>'
        f'<span style="width:200px;flex:none"></span></div></div>')
    return "".join(out)


def b_bars(b):
    bars = b["bars"]
    m = max(abs(x["pct"]) for x in bars) or 1
    tick = max([t for t in (0.25, 0.5, 1, 2, 3, 5, 10) if t <= m] or [0.25])
    scale = max(m, tick) * 1.1
    out = ['<div style="display:flex;flex-direction:column;gap:44px">']
    for x in bars:
        p = x["pct"]
        c = GREEN if p > 0 else RED if p < 0 else GREY
        w = abs(p) / scale * 50
        side = "left:50%" if p >= 0 else "right:50%"
        sign = "+" if p > 0 else ""
        lab = x.get("display") or f"{sign}{fr_num(p, x.get('decimals', 1))} %"
        out.append(
            f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font-size:40px;font-weight:700">{e(x["label"])}</span>'
            f'<span style="font-size:52px;font-weight:800;color:{c};font-variant-numeric:tabular-nums">{e(lab)}</span></div>'
            f'<div style="position:relative;height:60px"><div style="position:absolute;left:50%;top:0;width:3px;height:60px;background:{INK}"></div>'
            f'<div style="position:absolute;{side};top:8px;width:{w:.2f}%;height:44px;background:{c}"></div></div></div>')
    tpos = tick / scale * 50
    tl = fr_num(tick, 0 if tick >= 1 else 2 if tick == 0.25 else 1)
    out.append(
        f'<div style="position:relative;height:30px;font-family:{MONO};font-size:22px;color:{GREY};font-variant-numeric:tabular-nums">'
        f'<span style="position:absolute;left:{50 - tpos:.2f}%;top:0;transform:translateX(-50%)">−{tl}&nbsp;%</span>'
        f'<span style="position:absolute;left:50%;top:0;transform:translateX(-50%)">0</span>'
        f'<span style="position:absolute;left:{50 + tpos:.2f}%;top:0;transform:translateX(-50%)">+{tl}&nbsp;%</span></div></div>')
    return "".join(out)


def b_nodes(b):
    parts = []
    nodes = b["nodes"]
    for i, n in enumerate(nodes):
        if i:
            parts.append(f'<div style="flex:1;min-width:24px;height:3px;background:{INK}"></div>')
        sub = (f'<span style="font-family:{MONO};font-size:22px;font-weight:500;text-transform:uppercase">{e(n["sub"])}</span>'
               if n.get("sub") else "")
        if n.get("highlight"):
            parts.append(f'<div style="width:272px;flex:none;box-sizing:border-box;padding:{26 if sub else 40}px 12px;background:{BLUE};color:#FFFFFF;display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center">'
                         f'<span data-fit="2" style="font-size:36px;font-weight:800;text-transform:uppercase">{e(n["label"])}</span>{sub}</div>')
        else:
            parts.append(f'<div style="width:272px;flex:none;box-sizing:border-box;padding:{26 if sub else 40}px 12px;border:3px solid {INK};display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center">'
                         f'<span data-fit="2" style="font-size:36px;font-weight:800;text-transform:uppercase">{e(n["label"])}</span>{sub}</div>')
    line = f'<span style="font-size:40px;font-weight:600;text-align:center">{e(b["line"])}</span>' if b.get("line") else ""
    return f'<div style="display:flex;flex-direction:column;gap:28px"><div style="display:flex;align-items:center">{"".join(parts)}</div>{line}</div>'


def b_box(b):
    style = b.get("style", "alert")
    if style == "dark":
        return (f'<div style="display:flex;align-items:center;gap:24px;padding:32px 40px;background:{INK};color:#FFFFFF">'
                f'<span style="flex:none;font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#9FB0FF">{e(b["label"])}</span>'
                f'<span style="font-size:40px;font-weight:700;line-height:1.25">{e(b["text"])}</span></div>')
    if style == "blue":
        return (f'<div style="display:flex;flex-direction:column;gap:14px;padding:36px 40px;background:{BLUE};color:#FFFFFF">'
                f'<span style="font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase">{e(b["label"])}</span>'
                f'<span style="font-size:40px;font-weight:700;line-height:1.25">{e(b["text"])}</span></div>')
    c = RED if style == "alert" else GREEN if style == "good" else INK
    return (f'<div style="display:flex;flex-direction:column;gap:14px;padding:36px 40px;border:3px solid {c}">'
            f'<span style="font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:{c}">{e(b["label"])}</span>'
            f'<span style="font-size:40px;font-weight:700;line-height:1.25">{e(b["text"])}</span></div>')


def b_metrics(b):
    out = [f'<div style="display:flex;flex-direction:column;border-top:3px solid {INK}">']
    for m in b["metrics"]:
        c = DIR_COLOR.get(m.get("tone", "neutral"), INK)
        out.append(
            f'<div data-row style="display:flex;justify-content:space-between;align-items:center;gap:24px;padding:40px 0;border-bottom:3px solid {INK}">'
            f'<div style="display:flex;flex-direction:column;gap:8px;min-width:0">'
            f'<span style="font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:{GREY}">{e(m.get("small", ""))}</span>'
            f'<span style="font-size:40px;font-weight:700">{e(m["label"])}</span></div>'
            f'<span data-shrink style="font-size:120px;font-weight:900;letter-spacing:-0.03em;color:{c};white-space:nowrap;font-variant-numeric:tabular-nums">{e(m["value"])}</span></div>')
    out.append("</div>")
    return "".join(out)


def b_steps(b):
    steps = b["steps"]
    down = arrow("down", INK)
    out = ['<div style="display:flex;flex-direction:column;gap:16px">']
    for i, s in enumerate(steps, 1):
        if i > 1:
            out.append(f'<div style="display:flex;justify-content:center">{down}</div>')
        last = i == len(steps)
        st = f"background:{BLUE};color:#FFFFFF" if last else f"border:3px solid {INK}"
        out.append(f'<div style="display:flex;align-items:center;gap:32px;padding:40px;{st}">'
                   f'<span style="font-family:{MONO};font-size:30px;font-weight:600">{i:02d}</span>'
                   f'<span style="font-size:46px;font-weight:800;line-height:1.15">{e(s)}</span></div>')
    out.append("</div>")
    return "".join(out)


def b_agenda(b):
    out = [f'<div style="display:flex;flex-direction:column;border-top:3px solid {INK}">']
    for r in b["rows"]:
        out.append(f'<div data-row style="display:flex;align-items:center;gap:36px;padding:44px 0;border-bottom:3px solid {INK}">'
                   f'<span data-shrink style="width:230px;flex:none;font-size:72px;font-weight:900;color:{BLUE};white-space:nowrap;font-variant-numeric:tabular-nums">{e(r["time"])}</span>'
                   f'<span style="flex:1;min-width:0;font-size:44px;font-weight:700;line-height:1.15">{e(r["label"])}</span></div>')
    out.append("</div>")
    return "".join(out)


def b_note(b):
    return (f'<span style="font-family:{MONO};font-size:26px;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;color:{GREY}">{e(b["text"])}</span>')


def b_text(b):
    return f'<p style="margin:0;font-size:42px;font-weight:600;line-height:1.3">{e(b["text"])}</p>'


BLOCKS = {"rows": b_rows, "table6": b_table6, "figure": b_figure, "range": b_range, "bars": b_bars,
          "nodes": b_nodes, "box": b_box, "metrics": b_metrics, "steps": b_steps, "agenda": b_agenda,
          "note": b_note, "text": b_text}


# ---------------------------------------------------------------- frames
def header(date_s, color):
    return (f'<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:20px;border-bottom:3px solid {color};'
            f'font-family:{MONO};font-size:24px;font-weight:500;letter-spacing:0.06em;text-transform:uppercase"><span>Briefing marchés</span><span>{date_s}</span></div>')


def footer(i, n, color, right=None):
    if right is None:
        right = (f'<span style="display:flex;align-items:center;gap:12px">Glisse<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{color}" '
                 f'stroke-width="2.2" stroke-linecap="square" aria-hidden="true"><path d="M4 12h15"></path><path d="M13 6l6 6-6 6"></path></svg></span>')
    return (f'<div style="display:flex;justify-content:space-between;align-items:center;padding-top:20px;border-top:3px solid {color};'
            f'font-family:{MONO};font-size:24px;font-weight:500;letter-spacing:0.06em;text-transform:uppercase"><span>{i:02d}/{n:02d}</span>{right}</div>')


def frame(bg, fg, inner):
    return (f'<div id="slide" style="width:1080px;height:1350px;box-sizing:border-box;padding:64px 72px;background:{bg};color:{fg};'
            f"font-family:'Archivo',system-ui,sans-serif;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden\">{inner}</div>")


def cover(c, date_s, n):
    mid = (f'<div id="main" style="display:flex;flex-direction:column;gap:44px">'
           f'<div style="display:flex;flex-direction:column;gap:8px">'
           f'<span style="font-family:{MONO};font-size:30px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase">{e(c["kicker"])}</span>'
           f'<span data-fit="1" style="font-size:250px;font-weight:900;line-height:0.9;letter-spacing:-0.04em;white-space:nowrap;font-variant-numeric:tabular-nums">{e(c["figure"])}</span></div>'
           f'<h1 data-fit="3" style="margin:0;font-size:108px;font-weight:800;font-stretch:125%;line-height:0.92;letter-spacing:-0.01em;text-transform:uppercase">{e(c["title"])}</h1>'
           f'<p style="margin:0;font-size:42px;font-weight:500;line-height:1.3">{e(c["subtitle"])}</p></div>')
    return frame(BLUE, "#FFFFFF", header(date_s, "#FFFFFF") + mid + footer(1, n, "#FFFFFF"))


def content_slide(s, k, i, n, date_s):
    size = s.get("title_size", 112)
    blocks = "".join(BLOCKS[b["type"]](b) for b in s["blocks"])
    mid = (f'<div id="main" style="display:flex;flex-direction:column;gap:{s.get("gap", 60)}px">'
           f'<div style="display:flex;flex-direction:column;gap:20px">'
           f'<span style="font-family:{MONO};font-size:26px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:{BLUE}">{k:02d} — {e(s["kicker"])}</span>'
           f'<h2 data-fit="2" style="margin:0;font-size:{size}px;font-weight:800;font-stretch:125%;line-height:0.92;letter-spacing:-0.01em;text-transform:uppercase">{e(s["title"])}</h2></div>'
           f'<div style="display:flex;flex-direction:column;gap:{s.get("block_gap", 44)}px">{blocks}</div></div>')
    return frame("#FFFFFF", INK, header(date_s, INK) + mid + footer(i, n, INK))


def outro(o, date_s, n):
    icons = [
        ('<path d="M6 3h12v18l-6-4-6 4z"></path>', "Enregistre", ""),
        ('<path d="M21 3L10 14"></path><path d="M21 3l-7 18-4-7-7-4z"></path>', "Partage", "border-left:3px solid #FFFFFF;border-right:3px solid #FFFFFF;"),
        ('<circle cx="9" cy="8" r="4"></circle><path d="M2 21c0-3.9 3.1-7 7-7s7 3.1 7 7"></path><path d="M19 8v6"></path><path d="M16 11h6"></path>', "Abonne-toi", ""),
    ]
    cells = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:20px;padding:44px 0;{extra}">'
        f'<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter" aria-hidden="true">{p}</svg>'
        f'<span style="font-family:{MONO};font-size:26px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase">{lab}</span></div>'
        for p, lab, extra in icons)
    mid = (f'<div id="main" style="display:flex;flex-direction:column;gap:80px">'
           f'<h2 style="margin:0;font-size:120px;font-weight:800;font-stretch:125%;line-height:0.92;letter-spacing:-0.01em;text-transform:uppercase">Chaque matin, 8&nbsp;h&nbsp;30</h2>'
           f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:3px solid #FFFFFF;border-bottom:3px solid #FFFFFF">{cells}</div>'
           f'<span style="font-size:52px;font-weight:800">@newsmacro115</span></div>')
    bottom = (f'<div style="display:flex;flex-direction:column;gap:24px">'
              f'<span style="font-family:{MONO};font-size:22px;font-weight:500;line-height:1.5;letter-spacing:0.02em;text-transform:uppercase">'
              f'Information générale, pas un conseil en investissement. Sources&nbsp;: {e(o["sources"])}.</span>'
              f'{footer(n, n, "#FFFFFF", "<span>À demain</span>")}</div>')
    return frame(BLUE, "#FFFFFF", header(date_s, "#FFFFFF") + mid + bottom)


FIT_JS = r"""
() => {
  const report = [];
  const slide = document.getElementById('slide');
  // 1. headline-like elements: shrink until they fit their max line count and width
  for (const el of document.querySelectorAll('[data-fit]')) {
    const maxLines = parseInt(el.dataset.fit, 10);
    let fs = parseFloat(getComputedStyle(el).fontSize), n = 0;
    const lh = () => parseFloat(getComputedStyle(el).lineHeight) || fs * 1.2;
    const bad = () => el.scrollWidth > el.clientWidth + 1 || el.getBoundingClientRect().height > lh() * maxLines + 2
                      || el.getBoundingClientRect().right > slide.getBoundingClientRect().right - 71;
    while (bad() && n < 40) { fs *= 0.95; el.style.fontSize = fs + 'px'; n++; }
    if (n) report.push({shrunk: el.textContent.slice(0, 40), steps: n});
    if (bad()) report.push({overflow: 'fit', text: el.textContent.slice(0, 60)});
  }
  // 2. rows: shrink nowrap values until the row stops overflowing sideways
  for (const row of document.querySelectorAll('[data-row]')) {
    const vals = row.querySelectorAll('[data-shrink]');
    let n = 0;
    const over = () => row.scrollWidth > row.clientWidth + 1 || [...vals].some(v => v.scrollWidth > v.clientWidth + 1);
    while (over() && n < 25) {
      for (const v of vals) v.style.fontSize = (parseFloat(getComputedStyle(v).fontSize) * 0.95) + 'px';
      n++;
    }
    if (over()) report.push({overflow: 'row', text: row.textContent.slice(0, 60)});
  }
  // 3. the whole slide must fit vertically between header and footer
  const kids = [...slide.children];
  const used = kids.reduce((s, k) => s + k.getBoundingClientRect().height, 0);
  const avail = slide.clientHeight - 128;
  if (used > avail + 1) report.push({overflow: 'height', excess_px: Math.round(used - avail)});
  for (const k of kids) if (k.scrollHeight > k.clientHeight + 2) report.push({overflow: 'clip', text: k.textContent.slice(0, 40)});
  return report;
}
"""


def build_pages(content):
    d = content["date"]  # YYYY-MM-DD
    date_s = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
    s = content["slides"]
    middle = s["pages"]
    n = len(middle) + 2
    pages = [cover(s["cover"], date_s, n)]
    for k, page in enumerate(middle, 1):
        pages.append(content_slide(page, k, k + 1, n, date_s))
    pages.append(outro(s["outro"], date_s, n))
    return pages


def main():
    content = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    font_css = f"""
@font-face {{ font-family:'Archivo'; src:url('file://{FONTS}/Archivo-VF.ttf'); font-weight:100 900; font-stretch:62% 125%; }}
@font-face {{ font-family:'IBM Plex Mono'; src:url('file://{FONTS}/IBMPlexMono-Regular.ttf'); font-weight:400; }}
@font-face {{ font-family:'IBM Plex Mono'; src:url('file://{FONTS}/IBMPlexMono-Medium.ttf'); font-weight:500; }}
@font-face {{ font-family:'IBM Plex Mono'; src:url('file://{FONTS}/IBMPlexMono-SemiBold.ttf'); font-weight:600; }}
body {{ margin:0; }} *{{ -webkit-font-smoothing:antialiased; }}"""
    pages = build_pages(content)
    if not 6 <= len(pages) <= 20:
        sys.exit(f"carousel must have 6 to 20 slides, got {len(pages)}")
    from playwright.sync_api import sync_playwright
    report, files = {}, []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for i, body in enumerate(pages, 1):
            htmlp = out / f"{i:02d}.html"
            htmlp.write_text(f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><style>{font_css}</style></head><body>{body}</body></html>", encoding="utf-8")
            page.goto(htmlp.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(250)
            ok = page.evaluate("[document.fonts.check(\"800 40px Archivo\"), document.fonts.check(\"600 20px 'IBM Plex Mono'\")]")
            if not all(ok):
                report[f"{i:02d}"] = [{"overflow": "fonts not loaded"}]
            r = page.evaluate(FIT_JS)
            if r:
                report.setdefault(f"{i:02d}", []).extend(r)
            png = out / f"{i:02d}.png"
            page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            files.append(png)
            htmlp.unlink()
        browser.close()
    # contact sheet for the visual check
    from PIL import Image
    cols = 5
    rows_n = math.ceil(len(files) / cols)
    W, H = 270, 338
    sheet = Image.new("RGB", (cols * (W + 8) + 8, rows_n * (H + 8) + 8), "#BBBBBB")
    for k, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((W, H))
        sheet.paste(im, (8 + (k % cols) * (W + 8), 8 + (k // cols) * (H + 8)))
    sheet.save(out / "contact.png")
    errors = {k: [x for x in v if "overflow" in x] for k, v in report.items()}
    errors = {k: v for k, v in errors.items() if v}
    print(json.dumps({"slides": len(files), "dir": str(out), "adjustments": report, "errors": errors}, ensure_ascii=False, indent=1))
    sys.exit(2 if errors else 0)


if __name__ == "__main__":
    main()
