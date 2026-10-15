/**
 * SocialPulse API Client
 */

const API_BASE = "/api/v1";

async function request(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `API error (${res.status})`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${url}:`, err);
    throw err;
  }
}

export const api = {
  // Trends
  async getTrends({ source, sourceCategory, recency = "24h", regionScope, category, sort = "recency", page = 1, perPage = 30 } = {}) {
    const params = new URLSearchParams();
    if (source && source !== "all") {
      if (Array.isArray(source)) {
        source.forEach(s => params.append("source", s));
      } else {
        params.append("source", source);
      }
    }
    if (sourceCategory && sourceCategory !== "all") {
      params.append("source_category", sourceCategory);
    }
    if (recency) params.append("recency", recency);
    if (regionScope) params.append("region_scope", regionScope);
    if (category) params.append("category", category);
    if (sort) params.append("sort", sort);
    if (page) params.append("page", String(page));
    if (perPage) params.append("per_page", String(perPage));

    return request(`${API_BASE}/trends?${params.toString()}`);
  },

  async getTrendById(id) {
    return request(`${API_BASE}/trends/${id}`);
  },

  // Sources
  async getSources() {
    return request(`${API_BASE}/sources`);
  },

  async getSourceStatus(slug) {
    return request(`${API_BASE}/sources/${slug}/status`);
  },

  // Categories
  async getCategories() {
    return request(`${API_BASE}/categories`);
  },

  // Pipeline
  async getPipelineStatus() {
    return request(`${API_BASE}/pipeline/status`);
  },

  async triggerPipelineRun(slug = null) {
    const url = slug ? `${API_BASE}/pipeline/run/${slug}` : `${API_BASE}/pipeline/run`;
    return request(url, { method: "POST" });
  },

  async triggerAIProcessing(limit = 50) {
    return request(`${API_BASE}/pipeline/process-ai?limit=${limit}`, { method: "POST" });
  },

  // Health
  async getHealth() {
    return request("/health");
  }
};
