/**
 * SocialPulse Frontend Utilities
 */

export function timeAgo(dateString) {
  if (!dateString) return "Live trend";
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "1 day ago";
  return `${days}d ago`;
}

export function formatNumber(num) {
  if (num === null || num === undefined) return null;
  const n = Number(num);
  if (isNaN(n)) return null;

  if (n >= 1_000_000) {
    const formatted = (n / 1_000_000).toFixed(1);
    return formatted.endsWith(".0") ? formatted.slice(0, -2) + "M" : formatted + "M";
  }
  if (n >= 1_000) {
    const formatted = (n / 1_000).toFixed(1);
    return formatted.endsWith(".0") ? formatted.slice(0, -2) + "K" : formatted + "K";
  }
  return n.toLocaleString();
}

export function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function truncate(str, maxLength = 140) {
  if (!str) return "";
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength).trim() + "...";
}
