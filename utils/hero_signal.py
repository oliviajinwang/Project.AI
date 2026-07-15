"""Interactive "Brain Health Signal" hero visualization for the landing page.

Renders a softly glowing point-cloud constellation on a canvas. On load it
boots as a BRAINGUARD wordmark, holds briefly, then rearranges once into a
brain and stays there -- a one-time startup transition. Afterward, moving
the cursor (or scrolling / tapping on touch devices) gently illuminates one
of five brain regions and reveals a modifiable-factor label.

Decorative only -- contains no scoring, auth, or data logic. It runs inside
a sandboxed Streamlit component iframe, which cannot see the parent page's
CSS variables, so the handful of colors used here are hard-coded mirrors of
the theme tokens in utils/layout.py (--brand-navy, --y2k-*, --bg-page).

Accessibility:
- The headline is real DOM text overlaid on the canvas (readable by screen
  readers); the canvas itself is aria-hidden.
- The five factor names are also provided as visually-hidden text.
- Under prefers-reduced-motion the component draws a single static brain
  frame with all five labels visible and runs no animation at all.
"""

from __future__ import annotations

import streamlit as st

# ~80% of a typical laptop viewport; st.iframe needs a fixed pixel height.
HERO_HEIGHT = 720

_HERO_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500;600&display=swap');

/* Hard-coded mirrors of the utils/layout.py theme tokens (iframes cannot
   read the parent document's CSS variables). */
:root {
    --navy: #102A43;
    --ink-2: #3E5668;
    --muted: #627482;
    --page: #FCFAF6;
    --cyan: #46C7DC;
    --cyan-glow: rgba(70, 199, 220, 0.35);
    --silver: #CBD5DA;
    --silver-dark: #8FA0A8;
}

html, body { margin:0; padding:0; height:100%; overflow:hidden; background:var(--page); }

#hero { position:relative; width:100%; height:100%; font-family:'Inter', sans-serif; }

/* Technical dot grid + scanline grain, both capped well under 3% visual weight. */
#hero::before {
    content:""; position:absolute; inset:0; pointer-events:none;
    background-image:radial-gradient(circle, rgba(16,42,67,0.10) 1px, transparent 1.4px);
    background-size:26px 26px;
    -webkit-mask-image:radial-gradient(ellipse at 50% 45%, black 30%, transparent 78%);
    mask-image:radial-gradient(ellipse at 50% 45%, black 30%, transparent 78%);
}
#hero::after {
    content:""; position:absolute; inset:0; pointer-events:none; opacity:0.03;
    background-image:repeating-linear-gradient(0deg, #102A43 0px, #102A43 1px, transparent 1px, transparent 3px);
}

canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }

/* Overlaid hero copy: real DOM text with a soft page-colored fog behind it
   so contrast stays high over the point cloud. */
.copy {
    position:absolute; left:50%; top:44%; transform:translate(-50%,-50%);
    z-index:3; pointer-events:none; text-align:center; width:min(92%, 660px);
    padding:34px 10px;
    background:radial-gradient(ellipse closest-side, rgba(252,250,246,0.94) 42%, rgba(252,250,246,0.55) 72%, transparent 100%);
    transition:opacity 800ms ease; /* fades while the wordmark holds center stage */
}
.eyebrow {
    font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:600;
    letter-spacing:.12em; text-transform:uppercase; color:var(--silver-dark);
}
h1 {
    font-family:'Fraunces', Georgia, serif; font-weight:600;
    font-size:clamp(30px, 5.4vw, 46px); line-height:1.12; letter-spacing:-.03em;
    color:var(--navy); margin:12px 0 0;
}

/* Factor labels: opaque, high-contrast pills so text stays readable over
   the glowing points. Revealed by easing opacity only (no movement). */
.label {
    position:absolute; z-index:4; transform:translate(-50%, -150%);
    display:flex; align-items:center; gap:7px; white-space:nowrap;
    padding:6px 11px; border-radius:999px;
    background:rgba(255,255,255,0.95); border:1px solid var(--silver);
    box-shadow:0 1px 4px rgba(16,42,67,0.10), 0 0 14px var(--cyan-glow);
    font-family:'JetBrains Mono', monospace; font-size:11.5px; font-weight:600;
    letter-spacing:.09em; text-transform:uppercase; color:var(--navy);
    opacity:0; transition:opacity 480ms ease; pointer-events:none;
}
.label i { width:6px; height:6px; border-radius:50%; background:var(--cyan); box-shadow:0 0 6px var(--cyan-glow); }
/* Low-center regions place their pill below the anchor so it never sits on
   top of the overlaid headline. */
.label.below { transform:translate(-50%, 150%); }

.sr-only {
    position:absolute; width:1px; height:1px; padding:0; margin:-1px;
    overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}

/* Narrow screens: the fog would swallow the small brain, so stack them --
   constellation in the upper half (JS mirrors this split in layout()),
   headline in the lower half with a lighter fog. */
@media (max-width: 640px) {
    .copy {
        top:62%; width:96%; padding:16px 4px;
        background:radial-gradient(ellipse closest-side, rgba(252,250,246,0.92) 55%, transparent 100%);
    }
    h1 { font-size:clamp(24px, 7vw, 30px); }
    .eyebrow { font-size:10.5px; }
    .label { font-size:10.5px; padding:5px 9px; }
}
</style>
</head>
<body>
<div id="hero" role="img"
     aria-label="Decorative illustration: glowing points form the BrainGuard wordmark, then rearrange once into a brain whose regions illuminate to show modifiable factors.">
  <canvas id="cv" aria-hidden="true"></canvas>
  <div class="copy">
    <div class="eyebrow">Explainable screening support</div>
    <h1>A calmer way to start a<br>brain-health conversation.</h1>
  </div>
  <span class="sr-only">Modifiable brain-health factors shown: sleep, exercise,
  blood pressure, social connection, and education.</span>
</div>

<script>
(function () {
  'use strict';
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hero = document.getElementById('hero');
  var cv = document.getElementById('cv');
  var ctx = cv.getContext('2d');
  var copy = document.querySelector('.copy');

  /* ---- deterministic RNG so the constellation is identical every visit ---- */
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  var rand = mulberry32(20260715);

  /* ---- original, stylized brain-profile outline (normalized 0..1) ---- */
  var OUTLINE = [
    [0.16,0.52],[0.17,0.40],[0.23,0.28],[0.33,0.18],[0.46,0.12],[0.60,0.11],
    [0.72,0.15],[0.81,0.23],[0.86,0.33],[0.87,0.44],[0.84,0.54],[0.77,0.62],
    [0.69,0.66],[0.71,0.73],[0.66,0.80],[0.57,0.83],[0.50,0.79],[0.44,0.74],
    [0.34,0.71],[0.25,0.65],[0.19,0.59]
  ];
  function inPoly(x, y) {
    var inside = false;
    for (var i = 0, j = OUTLINE.length - 1; i < OUTLINE.length; j = i++) {
      var xi = OUTLINE[i][0], yi = OUTLINE[i][1], xj = OUTLINE[j][0], yj = OUTLINE[j][1];
      if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }

  /* ---- five modifiable-factor regions (normalized anchors) ---- */
  var REGIONS = [
    { nx: 0.33, ny: 0.66, name: 'Sleep', below: true },
    { nx: 0.56, ny: 0.17, name: 'Exercise' },
    { nx: 0.66, ny: 0.76, name: 'Blood pressure', below: true },
    { nx: 0.27, ny: 0.34, name: 'Social connection' },
    { nx: 0.79, ny: 0.40, name: 'Education' }
  ];
  REGIONS.forEach(function (r) {
    var el = document.createElement('div');
    el.className = r.below ? 'label below' : 'label';
    var dot = document.createElement('i');
    el.appendChild(dot);
    el.appendChild(document.createTextNode(r.name));
    hero.appendChild(el);
    r.el = el;
    r.intensity = 0;
  });

  /* ---- sample the BRAINGUARD wordmark into normalized target points ---- */
  function sampleWord() {
    var W = 1200, H = 260;
    var off = document.createElement('canvas');
    off.width = W; off.height = H;
    var c = off.getContext('2d');
    c.fillStyle = '#000';
    c.font = '800 168px Inter, Arial, sans-serif';
    if ('letterSpacing' in c) c.letterSpacing = '10px';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('BRAINGUARD', W / 2, H / 2 + 6);
    var data = c.getImageData(0, 0, W, H).data;
    var pts = [], step = 12;
    for (var y = step / 2; y < H; y += step) {
      for (var x = step / 2; x < W; x += step) {
        if (data[((y | 0) * W + (x | 0)) * 4 + 3] > 128) pts.push([x / W, y / H]);
      }
    }
    while (pts.length > 470) pts.splice((rand() * pts.length) | 0, 1);
    return pts; // normalized to the word's own box
  }

  /* ---- evenly sample N points inside the brain polygon ---- */
  function sampleBrain(n) {
    var pts = [];
    function candidate() {
      for (;;) {
        var x = 0.14 + rand() * 0.75, y = 0.09 + rand() * 0.76;
        if (inPoly(x, y)) return [x, y];
      }
    }
    pts.push(candidate());
    while (pts.length < n) {
      var best = null, bestD = -1;
      for (var k = 0; k < 10; k++) {
        var cnd = candidate(), d = Infinity;
        for (var i = 0; i < pts.length; i++) {
          var dx = cnd[0] - pts[i][0], dy = (cnd[1] - pts[i][1]) * 0.8;
          var dd = dx * dx + dy * dy;
          if (dd < d) d = dd;
        }
        if (d > bestD) { bestD = d; best = cnd; }
      }
      pts.push(best);
    }
    return pts;
  }

  /* ---- nearest-neighbor edges (indices), computed on normalized coords ---- */
  function buildEdges(pts, maxDist, maxPer) {
    var edges = [], seen = {};
    for (var i = 0; i < pts.length; i++) {
      var near = [];
      for (var j = 0; j < pts.length; j++) {
        if (i === j) continue;
        var dx = pts[i][0] - pts[j][0], dy = pts[i][1] - pts[j][1];
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < maxDist) near.push([d, j]);
      }
      near.sort(function (a, b) { return a[0] - b[0]; });
      for (var k = 0; k < Math.min(maxPer, near.length); k++) {
        var j2 = near[k][1];
        var key = i < j2 ? i + '_' + j2 : j2 + '_' + i;
        if (!seen[key]) { seen[key] = 1; edges.push([i, j2]); }
      }
    }
    return edges;
  }

  /* ---- build geometry ---- */
  var textPts = sampleWord();
  var N = textPts.length;
  var brainPts = sampleBrain(N);
  // Pair brain->text points by x-order so the morph sweeps cleanly.
  brainPts.sort(function (a, b) { return (a[0] - b[0]) || (a[1] - b[1]); });
  textPts.sort(function (a, b) { return (a[0] - b[0]) || (a[1] - b[1]); });

  var brainEdges = buildEdges(brainPts, 0.075, 3);
  var textEdges = buildEdges(textPts, 0.055, 2);

  var P = [];
  for (var i = 0; i < N; i++) {
    P.push({
      bx: 0, by: 0, tx: 0, ty: 0, x: 0, y: 0,
      stag: brainPts[i][0],            // left-to-right morph stagger
      phase: rand() * Math.PI * 2,     // idle drift phase
      w: [0, 0, 0, 0, 0]               // per-region glow weights
    });
  }

  /* ---- layout (canvas px), recomputed on resize ---- */
  var W = 0, H = 0, dpr = 1, brainBox = {}, wordBox = {};
  function layout() {
    W = hero.clientWidth; H = hero.clientHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // The parent page overlays the tagline + CTA on the hero's lower band,
    // so bias the constellation upward. Narrow screens also move the
    // headline below the brain (see the max-width media query).
    var narrow = W < 640;
    var cy = narrow ? H * 0.32 : H * 0.44;
    var bw = Math.min(W * (narrow ? 0.96 : 0.82), (narrow ? H * 0.52 : H * 0.78) / 0.78);
    var bh = bw * 0.78;
    brainBox = { x: (W - bw) / 2, y: cy - bh / 2, w: bw, h: bh };

    var tw = Math.min(W * 0.92, 1100);
    var th = tw * 260 / 1200;
    wordBox = { x: (W - tw) / 2, y: cy - th / 2, w: tw, h: th };

    for (var i = 0; i < N; i++) {
      var p = P[i];
      p.bx = brainBox.x + brainPts[i][0] * brainBox.w;
      p.by = brainBox.y + brainPts[i][1] * brainBox.h;
      p.tx = wordBox.x + textPts[i][0] * wordBox.w;
      p.ty = wordBox.y + textPts[i][1] * wordBox.h;
      for (var r = 0; r < 5; r++) {
        var ax = brainBox.x + REGIONS[r].nx * brainBox.w;
        var ay = brainBox.y + REGIONS[r].ny * brainBox.h;
        var dx = p.bx - ax, dy = p.by - ay;
        var rad = brainBox.w * 0.17;
        p.w[r] = Math.exp(-(dx * dx + dy * dy) / (rad * rad));
      }
    }
    REGIONS.forEach(function (r) {
      r.px = brainBox.x + r.nx * brainBox.w;
      r.py = brainBox.y + r.ny * brainBox.h;
      r.el.style.left = r.px + 'px';
      r.el.style.top = r.py + 'px';
    });
  }

  /* ---- interaction state ---- */
  var active = -1;              // pointer/wheel-selected region
  var autoIdx = 0;              // idle auto-cycle region
  var lastPointer = -1e9, lastCycle = 0, lastWheel = 0;

  function nearestRegion(x, y) {
    var best = -1, bestD = brainBox.w * 0.42;
    REGIONS.forEach(function (r, k) {
      var d = Math.hypot(x - r.px, y - r.py);
      if (d < bestD) { bestD = d; best = k; }
    });
    return best;
  }
  hero.addEventListener('pointermove', function (e) {
    var rect = hero.getBoundingClientRect();
    active = nearestRegion(e.clientX - rect.left, e.clientY - rect.top);
    lastPointer = performance.now();
  });
  hero.addEventListener('pointerleave', function () { active = -1; });
  hero.addEventListener('wheel', function (e) {
    var now = performance.now();
    if (now - lastWheel > 500) {
      lastWheel = now;
      autoIdx = (autoIdx + (e.deltaY > 0 ? 1 : 4)) % 5;
      active = -1;
      lastPointer = -1e9; // let the wheel-selected region show immediately
      lastCycle = now;
    }
  }, { passive: true });

  /* ---- morph state machine (plays once; click replays) ---- */
  /* One-time startup sequence: boot as the BRAINGUARD wordmark, hold,
     then settle into the brain and stay there. No replay. */
  var mode = 'hold', mStart = performance.now(), u = 0;
  var DUR = { hold: 2200, toBrain: 2600 };
  function begin(m) { mode = m; mStart = performance.now(); u = 0; }

  function easeInOut(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /* ---- drawing ---- */
  var NAVY = '16,42,67', CYAN = '70,199,220', STEEL = '53,109,139';

  function pointPos(p, now) {
    var m;
    if (mode === 'brain') m = 0;
    else if (mode === 'hold') m = 1;
    else {
      var raw = Math.min(1, Math.max(0, (u - p.stag * 0.18) / 0.82));
      m = 1 - easeInOut(raw);
    }
    var driftX = 0, driftY = 0;
    if (m < 0.99) {
      var s = (1 - m);
      driftX = Math.sin(now * 0.0006 + p.phase) * 1.6 * s;
      driftY = Math.cos(now * 0.0005 + p.phase * 1.3) * 1.4 * s;
    }
    p.x = p.bx + (p.tx - p.bx) * m + driftX;
    p.y = p.by + (p.ty - p.by) * m + driftY;
    return m;
  }

  function draw(now, globalM) {
    ctx.clearRect(0, 0, W, H);

    // edges: brain set fades out as the word forms; text set fades in
    ctx.lineWidth = 1;
    var aBrain = 0.15 * (1 - globalM), aText = 0.30 * globalM;
    if (aBrain > 0.02) {
      for (var e = 0; e < brainEdges.length; e++) {
        var p1 = P[brainEdges[e][0]], p2 = P[brainEdges[e][1]];
        var lit = (litOf(p1) + litOf(p2)) / 2;
        ctx.strokeStyle = lit > 0.12
          ? 'rgba(' + CYAN + ',' + (aBrain + lit * 0.4) + ')'
          : 'rgba(' + STEEL + ',' + aBrain + ')';
        ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
      }
    }
    if (aText > 0.02) {
      ctx.strokeStyle = 'rgba(' + STEEL + ',' + aText + ')';
      for (var e2 = 0; e2 < textEdges.length; e2++) {
        var q1 = P[textEdges[e2][0]], q2 = P[textEdges[e2][1]];
        ctx.beginPath(); ctx.moveTo(q1.x, q1.y); ctx.lineTo(q2.x, q2.y); ctx.stroke();
      }
    }

    // points with soft additive glow for lit regions / the held wordmark
    for (var i = 0; i < N; i++) {
      var p = P[i];
      var lit = litOf(p) * (1 - globalM);
      var glow = lit * 0.20 + globalM * 0.08;
      if (glow > 0.02) {
        ctx.fillStyle = 'rgba(' + CYAN + ',' + glow + ')';
        ctx.beginPath(); ctx.arc(p.x, p.y, 6.5, 0, 6.2832); ctx.fill();
      }
      var pulse = REDUCED ? 0 : Math.sin(now * 0.0015 + p.phase) * 0.06;
      var alpha = 0.44 + pulse + lit * 0.45 + globalM * 0.3;
      var mix = Math.min(1, lit + globalM * 0.55);
      ctx.fillStyle = mix > 0.25 ? 'rgba(' + CYAN + ',' + alpha + ')' : 'rgba(' + NAVY + ',' + alpha + ')';
      ctx.beginPath(); ctx.arc(p.x, p.y, 1.7 + lit * 1.3 + globalM * 0.3, 0, 6.2832); ctx.fill();
    }
  }

  function litOf(p) {
    var v = 0;
    for (var r = 0; r < 5; r++) v += REGIONS[r].intensity * p.w[r];
    return Math.min(1, v);
  }

  /* ---- static fallback for prefers-reduced-motion ---- */
  if (REDUCED) {
    layout();
    REGIONS.forEach(function (r) { r.intensity = 0.55; r.el.style.opacity = 0.95; });
    for (var i2 = 0; i2 < N; i2++) { P[i2].x = P[i2].bx; P[i2].y = P[i2].by; }
    draw(0, 0);
    window.addEventListener('resize', function () {
      layout();
      for (var i3 = 0; i3 < N; i3++) { P[i3].x = P[i3].bx; P[i3].y = P[i3].by; }
      draw(0, 0);
    });
    return;
  }

  /* ---- main loop ---- */
  layout();
  window.addEventListener('resize', layout);
  var running = true;
  document.addEventListener('visibilitychange', function () {
    running = !document.hidden;
    if (running) requestAnimationFrame(tick);
  });

  function tick(now) {
    if (!running) return;

    // advance the one-time startup sequence: hold wordmark -> brain
    if (mode === 'hold' && now - mStart > DUR.hold) {
      begin('toBrain');
    } else if (mode === 'toBrain') {
      u = Math.min(1, (now - mStart) / DUR.toBrain);
      if (u >= 1) mode = 'brain';
    }

    // headline yields the center while the wordmark forms and holds,
    // then returns (CSS transition supplies the smoothing)
    copy.style.opacity = (mode === 'brain' || (mode === 'toBrain' && u > 0.45)) ? 1 : 0;

    // idle auto-cycle through the regions while in brain mode
    var pointerFresh = now - lastPointer < 4000;
    if (mode === 'brain' && !pointerFresh && now - lastCycle > 3200) {
      lastCycle = now; autoIdx = (autoIdx + 1) % 5;
    }
    var target = mode !== 'brain' ? -1 : (pointerFresh ? active : autoIdx);
    REGIONS.forEach(function (r, k) {
      var t = k === target ? 1 : 0;
      r.intensity += (t - r.intensity) * 0.055;
      r.el.style.opacity = (r.intensity * 0.95).toFixed(3);
    });

    // move points, take the average morph position for edge crossfade
    var mSum = 0;
    for (var i = 0; i < N; i++) mSum += pointPos(P[i], now);
    draw(now, mSum / N);

    requestAnimationFrame(tick);
  }

  // Sample-render the wordmark only after the display font is ready, so the
  // point targets match the real letterforms; fall back after 1.6s.
  var kicked = false;
  function kick() {
    if (kicked) return;
    kicked = true;
    textPts = sampleWord();
    // re-pair in case the sample count changed with the loaded font
    while (textPts.length < N) textPts.push(textPts[(rand() * textPts.length) | 0]);
    textPts.length = N;
    textPts.sort(function (a, b) { return (a[0] - b[0]) || (a[1] - b[1]); });
    textEdges = buildEdges(textPts, 0.055, 2);
    layout();
    begin('hold'); // start the wordmark hold only once we can actually draw it
    requestAnimationFrame(tick);
  }
  if (document.fonts && document.fonts.load) {
    Promise.race([
      document.fonts.load('800 168px Inter').then(function () { return document.fonts.ready; }),
      new Promise(function (res) { setTimeout(res, 1600); })
    ]).then(kick, kick);
  } else {
    kick();
  }
})();
</script>
</body>
</html>
"""


def render_brain_signal_hero() -> None:
    """Render the interactive hero. Height is fixed (component iframes
    cannot auto-size a 100%-height canvas); the canvas lays itself out
    responsively within it at any width.

    Uses st.iframe (Streamlit >= 1.59); falls back to the legacy
    components.html on older runtimes such as a pinned deployment.
    """
    if hasattr(st, "iframe"):
        st.iframe(_HERO_HTML, height=HERO_HEIGHT)
    else:
        import streamlit.components.v1 as components

        components.html(_HERO_HTML, height=HERO_HEIGHT, scrolling=False)
