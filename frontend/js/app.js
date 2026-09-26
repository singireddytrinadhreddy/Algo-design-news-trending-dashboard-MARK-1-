/**
 * SocialPulse Dashboard Application
 */

import { api } from "./api.js";
import { timeAgo, formatNumber, escapeHTML, truncate } from "./utils.js";

// ============================================================
// Global State
// ============================================================
const state = {
  activeSource: "all",
  sourceCategory: "all", // "all" | "A" | "B"
  recency: "24h",
  category: "",
  sort: "recency",
  page: 1,
  perPage: 30,
  
  sources: [],
  categories: [],
  items: [],
  total: 0,
  totalPages: 1,
  isLoading: false
};

// ============================================================
// Particle Network Background Animation
// ============================================================
function initNetworkCanvas() {
  const canvas = document.getElementById("network-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let width, height;
  let particles = [];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  const count = Math.min(65, Math.floor(window.innerWidth / 20));
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.5 + 0.8
    });
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(45, 212, 200, 0.35)";
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(139, 124, 246, ${0.12 * (1 - dist / 130)})`;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(animate);
  }
  animate();
}

// ============================================================
// Render Functions
// ============================================================

function renderSourceTabs() {
  const container = document.getElementById("source-tabs-container");
  if (!container) return;

  const catASources = state.sources.filter(s => s.source_category === "A");
  const catBSources = state.sources.filter(s => s.source_category === "B");

  let html = `
    <button class="source-tab ${state.activeSource === "all" ? "active" : ""}" data-slug="all">
      <span>All Sources</span>
    </button>
  `;

  if (catASources.length > 0) {
    catASources.forEach(s => {
      const isActive = state.activeSource === s.slug ? "active" : "";
      html += `
        <button class="source-tab ${isActive}" data-slug="${escapeHTML(s.slug)}" data-cat="A">
          <img src="/static/assets/icons/${escapeHTML(s.icon_filename || 'youtube.svg')}" alt="" />
          <span>${escapeHTML(s.display_name)}</span>
          <span class="tab-indicator"></span>
        </button>
      `;
    });
  }

  if (catASources.length > 0 && catBSources.length > 0) {
    html += `<div class="tab-divider"></div>`;
  }

  if (catBSources.length > 0) {
    catBSources.forEach(s => {
      const isActive = state.activeSource === s.slug ? "active" : "";
      html += `
        <button class="source-tab cat-b-tab ${isActive}" data-slug="${escapeHTML(s.slug)}" data-cat="B">
          <img src="/static/assets/icons/${escapeHTML(s.icon_filename || 'google-trends.svg')}" alt="" />
          <span>${escapeHTML(s.display_name)}</span>
          <span class="tab-indicator" style="background: var(--cat-b-amber);"></span>
        </button>
      `;
    });
  }

  container.innerHTML = html;

  // Add click events
  container.querySelectorAll(".source-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const slug = tab.getAttribute("data-slug");
      state.activeSource = slug;
      state.page = 1;
      renderSourceTabs();
      fetchAndRenderTrends();
    });
  });
}

function renderCategoryFilter() {
  const select = document.getElementById("category-filter");
  if (!select) return;

  let html = `<option value="">All Categories (${state.categories.length})</option>`;
  state.categories.forEach(c => {
    const selected = state.category === c.name ? "selected" : "";
    html += `<option value="${escapeHTML(c.name)}" ${selected}>${escapeHTML(c.name)}</option>`;
  });
  select.innerHTML = html;
}

function renderSkeletons() {
  const grid = document.getElementById("trends-grid");
  if (!grid) return;

  let html = "";
  for (let i = 0; i < 6; i++) {
    html += `
      <div class="skeleton-card">
        <div style="display:flex; justify-content:space-between;">
          <div class="skeleton-line" style="width:100px; height:20px;"></div>
          <div class="skeleton-line" style="width:60px; height:16px;"></div>
        </div>
        <div>
          <div class="skeleton-line" style="width:90%; height:22px; margin-bottom:8px;"></div>
          <div class="skeleton-line" style="width:70%; height:16px; margin-bottom:14px;"></div>
          <div class="skeleton-line" style="width:40%; height:24px;"></div>
        </div>
        <div class="skeleton-line" style="width:100%; height:45px;"></div>
      </div>
    `;
  }
  grid.innerHTML = html;
}

function renderTrendsGrid() {
  const grid = document.getElementById("trends-grid");
  const counter = document.getElementById("results-counter");
  if (!grid) return;

  if (state.items.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">🔍</div>
        <h3>No Trending Items Found</h3>
        <p>No real-time items match your selected filters (Recency: ${escapeHTML(state.recency)}, Source: ${escapeHTML(state.activeSource)}). Try switching time windows or sources.</p>
      </div>
    `;
    if (counter) counter.innerText = `0 items found`;
    return;
  }

  if (counter) {
    counter.innerText = `Showing ${state.items.length} of ${state.total} items`;
  }

  let html = "";
  state.items.forEach(item => {
    const isCatA = item.source_category === "A";
    const cardClass = isCatA ? "card-cat-a" : "card-cat-b";
    const badgeClass = isCatA ? "badge-cat-a" : "badge-cat-b";
    
    // Category B badge copy
    let badgeText = item.source.source_type_label;
    if (item.source.slug === "google_trends") {
      badgeText = "SEARCH INTEREST";
    } else if (item.source.slug.includes("news")) {
      badgeText = "NEWS COVERAGE";
    }

    // CTA Link Copy
    let ctaCopy = `View on ${escapeHTML(item.source.display_name)} →`;
    if (item.source.slug === "google_trends") {
      ctaCopy = "View on Google →";
    } else if (!isCatA) {
      ctaCopy = "Read Article →";
    }

    // Metric display
    let metricHTML = "";
    if (item.engagement && item.engagement.value !== null) {
      metricHTML += `
        <span class="metric-chip">
          <span class="metric-val">${formatNumber(item.engagement.value)}</span>
          <span>${escapeHTML(item.engagement.label || "engagements")}</span>
        </span>
      `;
    }
    if (item.secondary_engagement && item.secondary_engagement.value !== null) {
      metricHTML += `
        <span class="metric-chip">
          <span class="metric-val">${formatNumber(item.secondary_engagement.value)}</span>
          <span>${escapeHTML(item.secondary_engagement.label || "comments")}</span>
        </span>
      `;
    }

    // AI Summary display
    const aiSummaryHTML = item.ai_summary ? `
      <div class="ai-summary-box">
        <div class="ai-summary-header">✨ Why It's Trending</div>
        <div class="ai-summary-text">${escapeHTML(item.ai_summary)}</div>
      </div>
    ` : "";

    html += `
      <article class="trend-card ${cardClass}" data-id="${item.id}">
        <div>
          <div class="card-header">
            <div class="source-info">
              <img class="source-icon" src="/static/assets/icons/${escapeHTML(item.source.icon_filename || 'youtube.svg')}" alt="" />
              <span class="source-name">${escapeHTML(item.source.display_name)}</span>
              <span class="${badgeClass}">${escapeHTML(badgeText)}</span>
            </div>
            <span class="card-time">${timeAgo(item.published_at || item.fetched_at)}</span>
          </div>

          <div class="card-body">
            <h2 class="card-title" title="${escapeHTML(item.title)}">${escapeHTML(item.title)}</h2>
            ${item.author ? `<div class="card-author">${escapeHTML(item.author)}</div>` : ""}
            ${metricHTML ? `<div class="metric-row">${metricHTML}</div>` : ""}
            ${aiSummaryHTML}
          </div>
        </div>

        <div class="card-footer">
          <div class="card-tags">
            <span class="category-pill">${escapeHTML(item.category ? item.category.name : "Trending")}</span>
            ${['mastodon', 'bluesky'].includes(item.source.slug) ? `<span class="global-pill" title="Global network trend — public API does not support regional filtering">🌐 GLOBAL</span>` : ""}
            ${item.location_india ? `<span class="location-chip" title="Location: ${escapeHTML(item.location_india)}">📍 ${escapeHTML(item.location_india)}</span>` : ""}
          </div>
          <a class="card-cta-btn" href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()">
            ${ctaCopy}
          </a>
        </div>
      </article>
    `;
  });

  grid.innerHTML = html;

  // Add click handler to open drawer on card click
  grid.querySelectorAll(".trend-card").forEach(card => {
    card.addEventListener("click", () => {
      const id = parseInt(card.getAttribute("data-id"));
      openDetailDrawer(id);
    });
  });
}

function renderPagination() {
  const container = document.getElementById("pagination-controls");
  if (!container) return;

  if (state.totalPages <= 1) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `
    <button class="page-btn" id="prev-page-btn" ${state.page <= 1 ? "disabled" : ""}>← Previous</button>
    <span class="page-info">Page ${state.page} of ${state.totalPages}</span>
    <button class="page-btn" id="next-page-btn" ${state.page >= state.totalPages ? "disabled" : ""}>Next →</button>
  `;

  const prevBtn = document.getElementById("prev-page-btn");
  const nextBtn = document.getElementById("next-page-btn");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (state.page > 1) {
        state.page--;
        fetchAndRenderTrends();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      if (state.page < state.totalPages) {
        state.page++;
        fetchAndRenderTrends();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }
}

// ============================================================
// Detail Drawer
// ============================================================

async function openDetailDrawer(itemId) {
  const overlay = document.getElementById("drawer-overlay");
  const drawer = document.getElementById("detail-drawer");
  const content = document.getElementById("drawer-content");
  if (!drawer || !content) return;

  content.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">Loading item details...</div>`;
  overlay.classList.add("open");
  drawer.classList.add("open");

  try {
    const item = await api.getTrendById(itemId);
    const isCatA = item.source_category === "A";

    let provenanceDescription = "";
    let ctaButtonCopy = `View on ${escapeHTML(item.source.display_name)} →`;

    if (['mastodon', 'bluesky'].includes(item.source.slug)) {
      provenanceDescription = `
        <strong>Category A (Direct Official API — Global Signal):</strong> This item was fetched directly from the official ${escapeHTML(item.source.display_name)} API in real-time. Because ${escapeHTML(item.source.display_name)}'s decentralized public API does not provide regional filtering, this reflects global federated discussions rather than India-specific trends.
      `;
    } else if (isCatA) {
      provenanceDescription = `
        <strong>Category A (Direct Official API):</strong> This item was fetched directly from the official ${escapeHTML(item.source.display_name)} API in real-time. Engagement numbers and URLs represent authentic live content on the platform.
      `;
    } else if (item.source.slug === "google_trends") {
      provenanceDescription = `
        <strong>Category B (Search Interest Signal):</strong> This represents algorithmic search interest volume on Google Search. It is not social media post data.
      `;
      ctaButtonCopy = "Explore on Google Trends →";
    } else {
      provenanceDescription = `
        <strong>Category B (Derived News Coverage):</strong> This is a verified journalistic news article reporting ON trends, viral moments, or discussions relating to ${escapeHTML(item.source.display_name.replace("News Coverage: ", ""))}. The link points to the authoritative published news article.
      `;
      ctaButtonCopy = "Read Full News Article →";
    }

    content.innerHTML = `
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; flex-wrap:wrap; gap:8px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <img style="width:24px; height:24px;" src="/static/assets/icons/${escapeHTML(item.source.icon_filename || 'youtube.svg')}" alt="" />
          <span style="font-weight:700; font-size:14px;">${escapeHTML(item.source.display_name)}</span>
          <span class="${isCatA ? 'badge-cat-a' : 'badge-cat-b'}">${escapeHTML(item.source.source_type_label)}</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <span class="category-pill">${escapeHTML(item.category ? item.category.name : "Trending")}</span>
          ${['mastodon', 'bluesky'].includes(item.source.slug) ? `<span class="global-pill" title="Global network trend — public API does not support regional filtering">🌐 GLOBAL</span>` : ""}
          ${item.location_india ? `<span class="location-chip">📍 ${escapeHTML(item.location_india)}</span>` : ""}
        </div>
      </div>

      <h2 style="font-family:var(--font-display); font-size:22px; line-height:1.3; margin-bottom:12px; color:#fff;">
        ${escapeHTML(item.title)}
      </h2>

      ${item.author ? `<p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">${escapeHTML(item.author)} · ${timeAgo(item.published_at || item.fetched_at)}</p>` : ""}

      ${item.location_india ? `
        <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(45,212,200,0.12); border:1px solid rgba(45,212,200,0.3); border-radius:6px; padding:5px 12px; margin-bottom:16px; font-size:12px; color:#2dd4c8; font-weight:600;">
          <span>📍 Target Location:</span>
          <span style="color:#ffffff;">${escapeHTML(item.location_india)}</span>
        </div>
      ` : ""}

      ${item.description ? `<p style="font-size:14px; line-height:1.6; color:var(--text-secondary); margin-bottom:20px;">${escapeHTML(item.description)}</p>` : ""}

      <!-- AI Summary -->
      ${item.ai_summary ? `
        <div class="ai-summary-box" style="margin:20px 0;">
          <div class="ai-summary-header" style="font-size:13px;">✨ AI Intelligence Summary (Gemini)</div>
          <p class="ai-summary-text" style="font-size:14px; margin-top:6px;">${escapeHTML(item.ai_summary)}</p>
        </div>
      ` : ""}

      <!-- Data Source Provenance Box -->
      <div class="provenance-card">
        <div class="provenance-title">Data Source Provenance</div>
        <div class="provenance-desc">${provenanceDescription}</div>
      </div>

      <a class="drawer-cta-btn ${isCatA ? '' : 'signal-cta'}" href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer">
        ${ctaButtonCopy}
      </a>
    `;
  } catch (err) {
    content.innerHTML = `<div style="color:var(--negative); padding:20px;">Failed to load item: ${escapeHTML(err.message)}</div>`;
  }
}

function closeDetailDrawer() {
  const overlay = document.getElementById("drawer-overlay");
  const drawer = document.getElementById("detail-drawer");
  if (overlay) overlay.classList.remove("open");
  if (drawer) drawer.classList.remove("open");
}

// ============================================================
// Data Fetching & Orchestration
// ============================================================

async function fetchAndRenderTrends() {
  state.isLoading = true;
  renderSkeletons();

  try {
    const data = await api.getTrends({
      source: state.activeSource,
      sourceCategory: state.sourceCategory,
      recency: state.recency,
      category: state.category,
      sort: state.sort,
      page: state.page,
      perPage: state.perPage
    });

    state.items = data.items;
    state.total = data.total;
    state.totalPages = data.total_pages;

    renderTrendsGrid();
    renderPagination();
  } catch (err) {
    const grid = document.getElementById("trends-grid");
    if (grid) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1; border-color: var(--negative);">
          <div class="empty-icon">⚠️</div>
          <h3>Failed to Load Feed</h3>
          <p>${escapeHTML(err.message || "Could not connect to backend.")}</p>
        </div>
      `;
    }
  } finally {
    state.isLoading = false;
  }
}

async function loadInitialData() {
  try {
    const [sourcesData, categoriesData] = await Promise.all([
      api.getSources(),
      api.getCategories()
    ]);

    state.sources = sourcesData.sources || [];
    state.categories = categoriesData.categories || [];

    renderSourceTabs();
    renderCategoryFilter();
    await fetchAndRenderTrends();
  } catch (err) {
    console.error("Initial load failed:", err);
  }
}

// ============================================================
// Event Listeners & Bootstrapping
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  initNetworkCanvas();

  // Recency Pills
  const recencyContainer = document.getElementById("recency-pills");
  if (recencyContainer) {
    recencyContainer.querySelectorAll(".recency-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        recencyContainer.querySelectorAll(".recency-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        state.recency = btn.getAttribute("data-hours");
        state.page = 1;
        fetchAndRenderTrends();
      });
    });
  }

  // Category Filter Select
  const categorySelect = document.getElementById("category-filter");
  if (categorySelect) {
    categorySelect.addEventListener("change", (e) => {
      state.category = e.target.value;
      state.page = 1;
      fetchAndRenderTrends();
    });
  }

  // Sort Filter Select
  const sortSelect = document.getElementById("sort-filter");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      state.sort = e.target.value;
      state.page = 1;
      fetchAndRenderTrends();
    });
  }

  // Manual Refresh Button
  const refreshBtn = document.getElementById("manual-refresh-btn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
      refreshBtn.innerText = "Refreshing...";
      await api.triggerPipelineRun();
      await fetchAndRenderTrends();
      refreshBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
        </svg>
        Refresh
      `;
    });
  }

  // Drawer Close Button, Overlay & ESC Key
  const closeBtn = document.getElementById("drawer-close-btn");
  const overlay = document.getElementById("drawer-overlay");
  if (closeBtn) closeBtn.addEventListener("click", closeDetailDrawer);
  if (overlay) overlay.addEventListener("click", closeDetailDrawer);

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDetailDrawer();
    }
  });

  // Initial Load
  loadInitialData();
});
