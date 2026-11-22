/* アトリエとなりの — no libraries, no build step. */
(() => {
  'use strict';

  const ROTS = ['-1deg', '0.7deg', '-0.4deg', '1.1deg', '-0.7deg', '0.4deg'];
  const TAPE_ROTS = ['-4deg', '3deg', '-1.5deg', '4.5deg', '-3deg', '1.5deg'];
  const TAPES = ['var(--tape-1)', 'var(--tape-2)', 'var(--tape-3)', 'var(--tape-4)', 'var(--tape-5)'];
  const KINDS = [['all', 'すべて'], ['shader', 'シェーダー'], ['3d', '3Dモデル・衣装'], ['goods', 'グッズ']];
  const BOOTH_TOP = 'https://johnsgc.booth.pm/';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  const $ = (id) => document.getElementById(id);
  const workFile = (w, name) => `media/works/${w.id}/${name}`;

  /* Small DOM helper: el('div', {class: 'x', style: {...}}, child, 'text') */
  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === undefined || v === null || v === false) continue;
      if (k === 'style') for (const [p, val] of Object.entries(v)) node.style.setProperty(p, val);
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? '' : v);
    }
    for (const c of children.flat()) if (c !== null && c !== undefined && c !== false) node.append(c);
    return node;
  }

  function svg(markup) {
    const t = document.createElement('template');
    t.innerHTML = markup.trim();
    return t.content.firstChild;
  }
  const playIcon = () => svg('<svg aria-hidden="true" width="12" height="12" viewBox="0 0 24 24" fill="#12214c"><path d="M7 4l13 8-13 8z"/></svg>');
  const extIcon = () => svg('<svg aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7"/><path d="M8 7h9v9"/></svg>');

  const metaLine = (w) => [w.title, w.year, (w.tags || []).join(' / ')].filter(Boolean).join(' · ');
  const isTodayCandidate = (w) => w.kind === 'shader' && !w.booth && (w.media === 'video' || w.media === 'image');

  /* ---------- lightbox ---------- */
  const lb = $('lightbox');
  function openLightbox(w) {
    const stage = $('lb-stage');
    stage.replaceChildren();
    if (w.media === 'video') {
      stage.append(el('video', { src: workFile(w, 'video.mp4'), poster: workFile(w, 'thumb.webp'), controls: true, autoplay: true, muted: true, loop: true, playsinline: true }));
    } else {
      stage.append(el('img', { src: workFile(w, w.media === 'image' ? 'image.png' : 'thumb.webp'), alt: w.ja }));
    }
    $('lb-caption').textContent = `${w.ja}　${metaLine(w)}`;
    lb.showModal();
  }
  $('lb-close').addEventListener('click', () => lb.close());
  lb.addEventListener('click', (e) => { if (e.target === lb) lb.close(); });
  lb.addEventListener('close', () => $('lb-stage').replaceChildren());

  /* ---------- works ---------- */
  function thumbOrPlaceholder(w, i) {
    const img = el('img', { src: workFile(w, 'thumb.webp'), alt: w.ja, loading: 'lazy', width: 400, height: 400 });
    img.addEventListener('error', () => {
      img.replaceWith(el('span', { class: 'work-placeholder', style: { '--tape': TAPES[(i + 2) % TAPES.length] } }, '画像準備中'));
    }, { once: true });
    return img;
  }

  function attachHoverVideo(box, w) {
    if (!canHover || reduceMotion) return;
    let video = null;
    box.addEventListener('pointerenter', () => {
      if (!video) {
        video = el('video', { src: workFile(w, 'video.mp4'), muted: true, loop: true, playsinline: true, preload: 'auto' });
        video.muted = true;
        box.append(video);
      }
      video.play().then(() => box.classList.add('playing')).catch(() => {});
    });
    box.addEventListener('pointerleave', () => {
      box.classList.remove('playing');
      if (video) video.pause();
    });
  }

  function workCard(w, i) {
    const hasMedia = w.media === 'video' || w.media === 'image';
    const media = hasMedia
      ? el('button', { class: 'work-media', type: 'button', 'aria-label': `${w.ja}を大きく見る`, onclick: () => openLightbox(w) })
      : el('div', { class: 'work-media' });
    media.append(thumbOrPlaceholder(w, i));
    if (w.media === 'video') {
      media.append(el('span', { class: 'badge badge-video' }, playIcon(), '動画'));
      attachHoverVideo(media, w);
    }
    if (w.event) media.append(el('span', { class: 'badge badge-event' }, w.event));

    const boothUrl = w.booth === true ? BOOTH_TOP : w.booth;
    return el('article', { class: 'sticker work', style: { '--r': ROTS[i % ROTS.length] } },
      el('span', { class: 'tape', 'aria-hidden': 'true', style: { '--tape': TAPES[i % TAPES.length], '--tr': TAPE_ROTS[i % TAPE_ROTS.length] } }),
      media,
      el('div', { class: 'work-body' },
        el('div', { class: 'work-title' }, el('h3', {}, w.ja), w.year ? el('span', { class: 'work-year' }, String(w.year)) : null),
        w.title && w.title !== w.ja ? el('span', { class: 'work-sub' }, w.title) : null,
        boothUrl ? el('a', { class: 'booth-link', href: boothUrl }, 'BOOTHで見る', extIcon()) : null,
        w.tags && w.tags.length ? el('ul', { class: 'tags' }, w.tags.map((t) => el('li', {}, t))) : null
      )
    );
  }

  function renderWorks(works, filter) {
    const grid = $('works-grid');
    const list = works.filter((w) => filter === 'all' || w.kind === filter);
    grid.replaceChildren(...(list.length ? list.map(workCard) : [el('p', { class: 'empty' }, 'まだありません。')]));
  }

  function renderChips(works) {
    let current = 'all';
    const chips = $('chips');
    const draw = () => {
      chips.replaceChildren(...KINDS.map(([key, label]) =>
        el('button', { class: 'chip', type: 'button', 'aria-pressed': String(key === current), onclick: () => { current = key; draw(); renderWorks(works, current); } }, label)
      ));
    };
    draw();
    renderWorks(works, current);
  }

  /* ---------- today's pick ---------- */
  function dailyIndex(length) {
    const d = new Date();
    let h = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    h = ((h ^ 61) ^ (h >>> 16)) * 9;
    h ^= h >>> 4;
    h = Math.imul(h, 0x27d4eb2d) >>> 0;
    h = (h ^ (h >>> 15)) >>> 0;
    return h % length;
  }

  function setupToday(works) {
    const pool = works.filter(isTodayCandidate);
    const card = $('today');
    if (!pool.length) { card.closest('.hero-today').hidden = true; return; }

    let index = dailyIndex(pool.length);
    let busy = false;
    const thumb = $('today-thumb');
    const video = $('today-video');
    const badge = $('today-event');

    const show = () => {
      const w = pool[index];
      thumb.src = workFile(w, 'thumb.webp');
      thumb.alt = w.ja;
      $('today-name').textContent = w.ja;
      $('today-name').title = w.ja;
      $('today-meta').textContent = metaLine(w);
      $('today-meta').title = metaLine(w);
      badge.hidden = !w.event;
      badge.textContent = w.event || '';
      video.pause();
      video.hidden = true;
      video.removeAttribute('src');
      if (w.media === 'video' && !reduceMotion) {
        video.muted = true;
        video.src = workFile(w, 'video.mp4');
        video.poster = workFile(w, 'thumb.webp');
        video.addEventListener('playing', () => { video.hidden = false; }, { once: true });
        video.play().catch(() => {});
      }
    };

    $('today-open').addEventListener('click', () => openLightbox(pool[index]));
    $('today-flip').addEventListener('click', () => {
      if (busy || pool.length < 2) return;
      const next = () => { index = (index + 1) % pool.length; show(); };
      if (reduceMotion) { next(); return; }
      busy = true;
      card.classList.add('peel-out');
      setTimeout(() => {
        card.classList.remove('peel-out');
        next();
        card.classList.add('drop-in');
        setTimeout(() => { card.classList.remove('drop-in'); busy = false; }, 400);
      }, 220);
    });

    show();
  }

  /* ---------- log ---------- */
  function renderLog(entries) {
    $('log-list').replaceChildren(...entries.map((e, i) => {
      const tape = TAPES[(i + 1) % TAPES.length];
      const src = typeof e.image === 'string' ? e.image : (e.image ? `media/log/${e.id}.webp` : null);
      let shot = null;
      if (src) {
        const img = el('img', { src, alt: e.title, loading: 'lazy', width: 480, height: 270 });
        shot = el('div', { class: 'log-shot' }, img);
        img.addEventListener('error', () => shot.remove(), { once: true });
      }
      return el('li', { class: 'log-item' },
        el('div', { class: 'log-rail', 'aria-hidden': 'true' },
          el('span', { class: 'log-dot', style: { '--tape': tape } }),
          el('span', { class: 'log-line' })),
        el('div', { class: 'sticker log-card', style: { '--r': ROTS[(i + 3) % ROTS.length] } },
          el('span', { class: 'tape', 'aria-hidden': 'true', style: { '--tape': tape, '--tr': TAPE_ROTS[i % TAPE_ROTS.length] } }),
          shot,
          el('span', { class: 'log-when' }, e.when),
          el('span', { class: 'log-title' }, e.title),
          e.body ? el('p', { class: 'log-body' }, e.body) : null)
      );
    }));
  }

  /* ---------- boot ---------- */
  $('year').textContent = String(new Date().getFullYear());

  const byYearDesc = (a, b) => (Number(b.year) || 0) - (Number(a.year) || 0);

  Promise.all([
    fetch('data/works.json').then((r) => r.json()),
    fetch('data/log.json').then((r) => r.json())
  ]).then(([works, log]) => {
    works = works.slice().sort(byYearDesc);
    setupToday(works);
    renderChips(works);
    renderLog(log);
  }).catch((err) => {
    console.error(err);
    $('works-grid').replaceChildren(el('p', { class: 'empty' }, 'データを読み込めませんでした。'));
  });
})();
