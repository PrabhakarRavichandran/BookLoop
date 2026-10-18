// ============================================================
// BOOKLOOP - Campus Second-Hand Book Marketplace
// app.js  -  Shared Application Logic (MySQL backend edition)
// ============================================================

// ─────────────────────────────────────────────────────────────
// CONFIG  - auto-detect the server origin so it works on any port
// ─────────────────────────────────────────────────────────────
var API = window.location.origin + "/api";

// ─────────────────────────────────────────────────────────────
// IN-MEMORY CACHE  (populated once per page load)
// ─────────────────────────────────────────────────────────────
var _cache = {
  books:          null,   // Array<Book>
  offers:         null,   // Array<Offer>
  wishlist:       null,   // Array<bookId>
  currentUser:    null,   // User | null
  _sessionConfirmed: false, // true once /api/auth/me has been called this page load
};

// ─────────────────────────────────────────────────────────────
// LOW-LEVEL FETCH WRAPPER
// ─────────────────────────────────────────────────────────────
/**
 * Thin wrapper around fetch that:
 *  - always sends/receives JSON
 *  - includes session cookies (credentials:"include")
 *  - throws on non-ok responses
 */
async function apiFetch(path, options) {
  var opts = Object.assign({ credentials: "include", headers: { "Content-Type": "application/json" } }, options || {});
  var res  = await fetch(API + path, opts);
  var json = await res.json();
  if (!json.success) throw new Error(json.message || "API error");
  return json;
}

// ─────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────

var _SESSION_KEY = "bl_user";

/**
 * Always validates the session with the server once per page load.
 * Uses a _sessionConfirmed flag so we only call /api/auth/me once.
 * sessionStorage is used only to preserve the user object across
 * navigations for display purposes — NOT to skip server validation.
 */
async function fetchCurrentUser() {
  // Already confirmed this page load — return cached result.
  if (_cache._sessionConfirmed) return _cache.currentUser;

  try {
    var r = await apiFetch("/auth/me");
    _cache.currentUser     = r.data;
    _cache._sessionConfirmed = true;
    sessionStorage.setItem(_SESSION_KEY, JSON.stringify(r.data));
  } catch (e) {
    _cache.currentUser     = null;
    _cache._sessionConfirmed = true;
    sessionStorage.removeItem(_SESSION_KEY);
  }
  return _cache.currentUser;
}

/** Synchronous getter — returns whatever is cached. */
function getCurrentUser() {
  // Prefer in-memory cache; fall back to sessionStorage for nav-bar render
  if (_cache.currentUser) return _cache.currentUser;
  var raw = sessionStorage.getItem(_SESSION_KEY);
  if (raw) { try { return JSON.parse(raw); } catch (_) {} }
  return null;
}

function isLoggedIn() {
  return !!_cache.currentUser;
}

/**
 * Hide body immediately, validate auth with server, then either
 * reveal the page or redirect to login. Use on every protected page.
 */
async function requireAuth() {
  // Hide the page until we confirm auth — prevents the flash
  document.documentElement.style.visibility = "hidden";

  var user = await fetchCurrentUser();
  if (!user) {
    window.location.href = "login.html";
    return null;
  }

  // Auth confirmed — show the page
  document.documentElement.style.visibility = "";
  return user;
}

async function login(email, password) {
  try {
    var r = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: email, password: password }),
    });
    _cache.currentUser       = r.data;
    _cache._sessionConfirmed = true;  // server just confirmed — no need to call /auth/me again
    sessionStorage.setItem(_SESSION_KEY, JSON.stringify(r.data));
    return { success: true, user: r.data };
  } catch (e) {
    return { success: false, message: e.message };
  }
}

async function register(userData) {
  try {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
    // Registration does NOT log the user in — they must log in manually.
    return { success: true };
  } catch (e) {
    return { success: false, message: e.message };
  }
}

async function logout() {
  try { await apiFetch("/auth/logout", { method: "POST" }); } catch (_) {}
  _cache.currentUser = null;
  sessionStorage.removeItem(_SESSION_KEY);
  window.location.href = "login.html";
}

// ─────────────────────────────────────────────────────────────
// BOOKS
// ─────────────────────────────────────────────────────────────

async function getBooks() {
  if (_cache.books) return _cache.books;
  var r      = await apiFetch("/books");
  _cache.books = r.data;
  return _cache.books;
}

async function getBookById(id) {
  // Try cache first
  if (_cache.books) {
    var found = _cache.books.find(function(b) { return b.id == id; });
    if (found) return found;
  }
  try {
    var r = await apiFetch("/books/" + id);
    return r.data;
  } catch (e) {
    return null;
  }
}

async function addBook(bookData) {
  var r = await apiFetch("/books", {
    method: "POST",
    body: JSON.stringify(bookData),
  });
  _cache.books = null;   // invalidate
  return r.data;
}

async function updateBookStatus(bookId, newStatus) {
  await apiFetch("/books/" + bookId + "/status", {
    method: "PATCH",
    body: JSON.stringify({ status: newStatus }),
  });
  _cache.books = null;
}

async function markAsSold(bookId) {
  await updateBookStatus(bookId, "SOLD");
  showToast("Book marked as SOLD.", "success");
}

// ─────────────────────────────────────────────────────────────
// SEARCH & FILTER  (client-side, same API as before)
// ─────────────────────────────────────────────────────────────

function filterBooks(books, filterType) {
  if (!filterType || filterType === "All") return books;
  if (["Sell", "Exchange", "Donate"].includes(filterType))
    return books.filter(function(b) { return b.type === filterType; });
  if (["AVAILABLE", "RESERVED", "SOLD"].includes(filterType))
    return books.filter(function(b) { return b.status === filterType; });
  return books;
}

function filterBySemester(books, sem) {
  if (!sem || sem === "All") return books;
  return books.filter(function(b) { return b.semester === sem; });
}

// ─────────────────────────────────────────────────────────────
// OFFERS
// ─────────────────────────────────────────────────────────────

async function getOffers() {
  if (_cache.offers) return _cache.offers;
  var r        = await apiFetch("/offers");
  _cache.offers = r.data;
  return _cache.offers;
}

async function makeOffer(bookId, bookTitle, offerPrice, message) {
  var r = await apiFetch("/offers", {
    method: "POST",
    body: JSON.stringify({ bookId: bookId, offerPrice: parseInt(offerPrice), message: message }),
  });
  _cache.offers = null;
  _cache.books  = null;
  showToast("Offer sent successfully!", "success");
  return r.data;
}

async function acceptOffer(offerId) {
  var r = await apiFetch("/offers/" + offerId + "/accept", { method: "PATCH" });
  _cache.offers = null;
  _cache.books  = null;
  showToast("Offer accepted. Book is now RESERVED.", "success");
  return r.data || {};
}

async function rejectOffer(offerId) {
  await apiFetch("/offers/" + offerId + "/reject", { method: "PATCH" });
  _cache.offers = null;
  showToast("Offer rejected.", "info");
}

// ─────────────────────────────────────────────────────────────
// HANDOVER
// ─────────────────────────────────────────────────────────────

async function sellerConfirmHandover(offerId) {
  var r = await apiFetch("/offers/" + offerId + "/seller-confirm", { method: "POST" });
  _cache.offers = null; _cache.books = null;
  return r.data;
}

async function buyerConfirmHandover(offerId, code) {
  var r = await apiFetch("/offers/" + offerId + "/buyer-confirm", {
    method: "POST",
    body: JSON.stringify({ code: code }),
  });
  _cache.offers = null; _cache.books = null;
  return r.data;
}

// ─────────────────────────────────────────────────────────────
// WANTED BOOKS
// ─────────────────────────────────────────────────────────────

async function getWanted() {
  try {
    var r = await apiFetch("/wanted");
    return r.data;
  } catch (_) { return []; }
}

async function postWanted(data) {
  var r = await apiFetch("/wanted", { method: "POST", body: JSON.stringify(data) });
  return r.data;
}

async function deleteWantedBook(id) {
  await apiFetch("/wanted/" + id, { method: "DELETE" });
}

async function fulfillWantedBook(id) {
  await apiFetch("/wanted/" + id + "/fulfill", { method: "POST" });
}


// ─────────────────────────────────────────────────────────────
// WISHLIST
// ─────────────────────────────────────────────────────────────

async function getWishlist() {
  if (_cache.wishlist) return _cache.wishlist;
  try {
    var r        = await apiFetch("/wishlist");
    _cache.wishlist = r.data;
  } catch (_) {
    _cache.wishlist = [];
  }
  return _cache.wishlist;
}

async function addToWishlist(bookId) {
  await apiFetch("/wishlist/" + bookId, { method: "POST" });
  _cache.wishlist = null;
  showToast("Added to Wishlist.", "success");
}

async function removeFromWishlist(bookId) {
  await apiFetch("/wishlist/" + bookId, { method: "DELETE" });
  _cache.wishlist = null;
  showToast("Removed from Wishlist.", "info");
}

async function toggleWishlist(bookId) {
  var list = await getWishlist();
  if (list.includes(bookId) || list.map(Number).includes(Number(bookId))) {
    await removeFromWishlist(bookId);
    return false;
  } else {
    await addToWishlist(bookId);
    return true;
  }
}

async function isInWishlist(bookId) {
  var list = await getWishlist();
  return list.map(Number).includes(Number(bookId));
}

// ─────────────────────────────────────────────────────────────
// UI HELPERS  (unchanged from original)
// ─────────────────────────────────────────────────────────────

function getBookCoverHTML(book) {
  var color = book.color || "#6366F1";
  var label = book.cover || book.title.substring(0, 3).toUpperCase();
  return '<div class="book-cover" style="background: linear-gradient(135deg, ' + color + ', ' + color + 'aa);">' +
           '<span class="book-cover-text">' + label + '</span>' +
         '</div>';
}

function getStatusBadge(status) {
  var map = { "AVAILABLE": "badge-available", "RESERVED": "badge-reserved", "SOLD": "badge-sold" };
  return '<span class="badge ' + (map[status] || '') + '">' + status + '</span>';
}

function getTypeBadge(type) {
  var map = { "Sell": "badge-sell", "Exchange": "badge-exchange", "Donate": "badge-donate" };
  return '<span class="badge ' + (map[type] || '') + '">' + type + '</span>';
}

function showToast(message, type) {
  type = type || "info";
  var existing = document.querySelector(".toast");
  if (existing) existing.remove();
  var toast = document.createElement("div");
  toast.className = "toast toast-" + type;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(function() { toast.classList.add("toast-show"); }, 10);
  setTimeout(function() {
    toast.classList.remove("toast-show");
    setTimeout(function() { toast.remove(); }, 400);
  }, 3000);
}

function getGreeting() {
  var h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function setActiveNav() {
  var page = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-link").forEach(function(link) {
    if (link.getAttribute("href") === page) link.classList.add("active");
  });
}

function renderNavUser() {
  var userDisplay = document.getElementById("navUserName");
  var user = getCurrentUser();
  if (userDisplay && user) userDisplay.textContent = user.name;
}

function initMobileNav() {
  var toggle = document.getElementById("navToggle");
  var menu   = document.getElementById("navMenu");
  if (toggle && menu) {
    toggle.addEventListener("click", function() {
      menu.classList.toggle("open");
      toggle.classList.toggle("open");
    });
  }
}

// ─────────────────────────────────────────────────────────────
// PAGE INIT  (run on every protected page)
// ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function() {
  setActiveNav();
  initMobileNav();
});
