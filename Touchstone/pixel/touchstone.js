/**
 * Touchstone — Open Source Marketing Attribution Pixel
 * MIT Licence — Almost Magic Tech Lab
 *
 * Usage:
 *   <script src="https://your-server:8200/pixel/touchstone.js"
 *           data-api="https://your-server:8200"></script>
 *
 * API:
 *   touchstone.track(eventType, metadata)  — send custom event
 *   touchstone.identify(email, name, company) — link anonymous to known
 */
(function () {
  "use strict";

  // Respect Do Not Track
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") {
    window.touchstone = { track: function () {}, identify: function () {} };
    return;
  }

  // Find API URL from script tag
  var scripts = document.querySelectorAll("script[data-api]");
  var apiBase = "";
  for (var i = 0; i < scripts.length; i++) {
    if (scripts[i].src && scripts[i].src.indexOf("touchstone") !== -1) {
      apiBase = scripts[i].getAttribute("data-api");
      break;
    }
  }
  if (!apiBase) {
    // Fallback: infer from script src
    var s = document.querySelector('script[src*="touchstone"]');
    if (s && s.src) {
      var url = new URL(s.src);
      apiBase = url.origin;
    }
  }
  if (!apiBase) return;

  // Strip trailing slash
  apiBase = apiBase.replace(/\/+$/, "");

  // Anonymous ID — first-party cookie, 1-year expiry
  function getAnonymousId() {
    var cookieName = "_ts_aid";
    var match = document.cookie.match(new RegExp("(^| )" + cookieName + "=([^;]+)"));
    if (match) return match[2];

    // Generate UUID v4
    var id = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });

    // Set cookie — 1 year, SameSite=Lax, first-party only
    var expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = cookieName + "=" + id + "; expires=" + expires + "; path=/; SameSite=Lax";
    return id;
  }

  var anonymousId = getAnonymousId();

  // Parse UTM parameters from URL
  function getUTMParams() {
    var params = {};
    try {
      var search = new URLSearchParams(window.location.search);
      var utmKeys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
      for (var i = 0; i < utmKeys.length; i++) {
        var val = search.get(utmKeys[i]);
        if (val) params[utmKeys[i]] = val;
      }
    } catch (e) {
      // URLSearchParams not supported — skip
    }
    return params;
  }

  // Send event to API (fire and forget — beacon or XHR)
  function sendEvent(data) {
    var payload = JSON.stringify(data);
    // Prefer sendBeacon for page unload reliability
    if (navigator.sendBeacon) {
      navigator.sendBeacon(apiBase + "/api/v1/collect", new Blob([payload], { type: "application/json" }));
    } else {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", apiBase + "/api/v1/collect", true);
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.send(payload);
    }
  }

  // Track a touchpoint
  function track(eventType, metadata) {
    var utm = getUTMParams();
    var data = {
      anonymous_id: anonymousId,
      touchpoint_type: eventType || "custom",
      page_url: window.location.href,
      referrer_url: document.referrer || null,
      source: utm.utm_source || null,
      medium: utm.utm_medium || null,
      utm_campaign: utm.utm_campaign || null,
      utm_content: utm.utm_content || null,
      utm_term: utm.utm_term || null,
      metadata: metadata || null,
      timestamp: new Date().toISOString(),
    };
    sendEvent(data);
  }

  // Identify anonymous user
  function identify(email, name, company) {
    var payload = JSON.stringify({
      anonymous_id: anonymousId,
      email: email,
      name: name || null,
      company: company || null,
    });
    var xhr = new XMLHttpRequest();
    xhr.open("POST", apiBase + "/api/v1/identify", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(payload);
  }

  // Auto-track page view on load
  track("page_view");

  // Public API
  window.touchstone = {
    track: track,
    identify: identify,
    anonymousId: anonymousId,
  };
})();
