/**
 * EVENTHUB - CORE APPLICATION SCRIPT
 * Connects frontend directly to FastAPI backend & SQLite database.
 */

/* ==========================================================================
   STATE & CONSTANTS
   ========================================================================== */

const API_BASE = "";

let currentUser = null;
let authToken = localStorage.getItem("eventhub_token") || null;
let cachedEvents = [];

/* ==========================================================================
   API CLIENT
   ========================================================================== */

async function apiRequest(endpoint, options = {}) {
    const headers = options.headers || {};

    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Unauthorized - clear token and reset
            if (authToken) {
                showToast("Session expired. Please sign in again.", "error");
                logout(false);
            }
        }

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const errorMsg = data && data.detail ? data.detail : `Request failed (${response.status})`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        throw err;
    }
}

/* ==========================================================================
   DOM ELEMENTS
   ========================================================================== */

const pageTitle = document.getElementById("pageTitle");
const sidebar = document.getElementById("sidebar");
const mobileOverlay = document.getElementById("mobileOverlay");
const menuToggle = document.getElementById("menuToggle");
const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
const toastContainer = document.getElementById("toastContainer");

// Auth Elements
const headerAuthBox = document.getElementById("headerAuthBox");
const sidebarUsername = document.getElementById("sidebarUsername");
const sidebarUserRole = document.getElementById("sidebarUserRole");
const sidebarAvatar = document.getElementById("sidebarAvatar");
const userRoleBadge = document.getElementById("userRoleBadge");

// Modals
const eventModal = document.getElementById("eventModal");
const eventModalForm = document.getElementById("eventModalForm");
const eventModalTitle = document.getElementById("eventModalTitle");
const eventModalId = document.getElementById("eventModalId");
const eventModalTitleInput = document.getElementById("eventModalTitleInput");
const eventModalDateInput = document.getElementById("eventModalDateInput");
const eventModalLocationInput = document.getElementById("eventModalLocationInput");
const eventModalDescInput = document.getElementById("eventModalDescInput");

/* ==========================================================================
   HELPERS
   ========================================================================== */

function escapeHTML(str) {
    if (str === null || str === undefined) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
        const [year, month, day] = dateStr.split("-");
        const dateObj = new Date(year, month - 1, day);
        return dateObj.toLocaleDateString("en-US", {
            weekday: "short",
            month: "short",
            day: "numeric",
            year: "numeric"
        });
    } catch {
        return dateStr;
    }
}

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHTML(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(8px)";
        toast.style.transition = "all 0.2s ease";
        setTimeout(() => toast.remove(), 250);
    }, 3200);
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/* ==========================================================================
   NAVIGATION & UI STATE
   ========================================================================== */

function showSection(sectionId, title) {
    document.querySelectorAll(".content-section").forEach(sec => {
        sec.classList.remove("active");
    });

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add("active");
    }

    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.section === sectionId);
    });

    if (title) {
        pageTitle.textContent = title;
    }

    closeMobileSidebar();
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Trigger section-specific loads
    switch (sectionId) {
        case "dashboard":
            loadDashboard();
            break;
        case "upcoming-events":
            loadUpcomingEvents();
            break;
        case "past-events":
            loadPastEvents();
            break;
        case "event-registration":
            loadRegistrationEvents();
            break;
        case "my-registrations":
            loadMyRegistrations();
            break;
        case "events-management":
            loadManageEvents();
            break;
        case "participant-registrations":
            loadAllRegistrations();
            break;
        case "user-management":
            loadUsers();
            break;
        case "reports-section":
            loadReports();
            break;
    }
}

function updateNavigationVisibility() {
    const isAdmin = currentUser && currentUser.role === "admin";
    const isLoggedIn = currentUser !== null;

    // Show or hide admin navigation items
    document.querySelectorAll(".admin-only").forEach(el => {
        el.style.display = isAdmin ? "" : "none";
    });

    // Admin category label
    const adminLabel = document.getElementById("adminNavCategory");
    if (adminLabel) adminLabel.style.display = isAdmin ? "" : "none";

    // Dashboard button in sidebar (only admins)
    const navDash = document.getElementById("navDashboard");
    if (navDash) navDash.style.display = isAdmin ? "" : "none";

    // My Registrations button (logged-in users)
    const navMyReg = document.getElementById("navMyRegistrations");
    if (navMyReg) navMyReg.style.display = isLoggedIn ? "" : "none";

    // User Role Badge
    if (userRoleBadge) {
        if (!isLoggedIn) {
            userRoleBadge.textContent = "Guest";
            userRoleBadge.style.background = "#e2e8f0";
            userRoleBadge.style.color = "#475569";
        } else if (isAdmin) {
            userRoleBadge.textContent = "Administrator";
            userRoleBadge.style.background = "#ede9fe";
            userRoleBadge.style.color = "#6d28d9";
        } else {
            userRoleBadge.textContent = "Student User";
            userRoleBadge.style.background = "#e0f2fe";
            userRoleBadge.style.color = "#0369a1";
        }
    }

    // Sidebar footer
    if (isLoggedIn) {
        sidebarUsername.textContent = currentUser.username;
        sidebarUserRole.textContent = currentUser.role === "admin" ? "Administrator" : "Standard User";
        sidebarAvatar.textContent = currentUser.username.substring(0, 2).toUpperCase();
    } else {
        sidebarUsername.textContent = "Guest Visitor";
        sidebarUserRole.textContent = "Sign in to register";
        sidebarAvatar.textContent = "GU";
    }

    // Top Header Auth box
    if (headerAuthBox) {
        if (isLoggedIn) {
            headerAuthBox.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="text-align: right; line-height: 1.2;">
                        <strong style="display: block; font-size: 0.9rem;">${escapeHTML(currentUser.username)}</strong>
                        <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: capitalize;">${escapeHTML(currentUser.role)}</span>
                    </div>
                    <button class="btn btn-secondary btn-sm" id="signOutBtn" title="Sign Out">
                        Sign Out
                    </button>
                </div>
            `;
            document.getElementById("signOutBtn")?.addEventListener("click", () => logout(true));
        } else {
            headerAuthBox.innerHTML = `
                <button class="btn btn-primary btn-sm" id="headerSignInBtn">
                    Sign In / Register
                </button>
            `;
            document.getElementById("headerSignInBtn")?.addEventListener("click", () => {
                showSection("auth-section", "Account Portal");
            });
        }
    }
}

// Sidebar Drawer Toggle
if (menuToggle) {
    menuToggle.addEventListener("click", () => {
        sidebar.classList.add("open");
        mobileOverlay.classList.add("show");
    });
}

if (sidebarCloseBtn) {
    sidebarCloseBtn.addEventListener("click", closeMobileSidebar);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener("click", closeMobileSidebar);
}

function closeMobileSidebar() {
    sidebar?.classList.remove("open");
    mobileOverlay?.classList.remove("show");
}

// Global data-switch and nav click handlers
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        showSection(btn.dataset.section, btn.querySelector("span:last-child")?.textContent);
    });
});

document.addEventListener("click", e => {
    const switchBtn = e.target.closest("[data-switch]");
    if (switchBtn) {
        const target = switchBtn.dataset.switch;
        const matchingNav = document.querySelector(`.nav-btn[data-section="${target}"]`);
        const title = matchingNav ? matchingNav.querySelector("span:last-child")?.textContent : "";
        showSection(target, title);
    }
});

/* ==========================================================================
   AUTHENTICATION LOGIC
   ========================================================================== */

async function checkAuthSession() {
    if (!authToken) {
        currentUser = null;
        updateNavigationVisibility();
        showSection("upcoming-events", "Upcoming Events");
        return;
    }

    try {
        const user = await apiRequest("/api/auth/me");
        currentUser = user;
        updateNavigationVisibility();
        if (currentUser.role === "admin") {
            showSection("dashboard", "Admin Dashboard");
        } else {
            showSection("upcoming-events", "Upcoming Events");
        }
    } catch {
        logout(false);
    }
}

function logout(showNotice = true) {
    authToken = null;
    currentUser = null;
    localStorage.removeItem("eventhub_token");
    updateNavigationVisibility();
    showSection("upcoming-events", "Upcoming Events");
    if (showNotice) {
        showToast("You have been signed out successfully.", "info");
    }
}

// Auth Tab Switching
const tabLoginBtn = document.getElementById("tabLoginBtn");
const tabRegisterBtn = document.getElementById("tabRegisterBtn");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const loginErrorMsg = document.getElementById("loginErrorMsg");
const registerErrorMsg = document.getElementById("registerErrorMsg");

tabLoginBtn?.addEventListener("click", () => {
    tabLoginBtn.classList.add("active");
    tabRegisterBtn.classList.remove("active");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    loginErrorMsg.classList.remove("show");
});

tabRegisterBtn?.addEventListener("click", () => {
    tabRegisterBtn.classList.add("active");
    tabLoginBtn.classList.remove("active");
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    registerErrorMsg.classList.remove("show");
});

// Login Submission
loginForm?.addEventListener("submit", async e => {
    e.preventDefault();
    loginErrorMsg.classList.remove("show");

    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;
    const submitBtn = document.getElementById("loginSubmitBtn");

    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";

    try {
        const data = await apiRequest("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem("eventhub_token", authToken);

        loginForm.reset();
        updateNavigationVisibility();

        showToast(`Welcome back, ${currentUser.username}!`, "success");

        if (currentUser.role === "admin") {
            showSection("dashboard", "Admin Dashboard");
        } else {
            showSection("upcoming-events", "Upcoming Events");
        }
    } catch (err) {
        loginErrorMsg.textContent = err.message;
        loginErrorMsg.classList.add("show");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Sign In to EventHub";
    }
});

// Register Submission
registerForm?.addEventListener("submit", async e => {
    e.preventDefault();
    registerErrorMsg.classList.remove("show");

    const username = document.getElementById("registerUsername").value.trim();
    const password = document.getElementById("registerPassword").value;
    const submitBtn = document.getElementById("registerSubmitBtn");

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating Account...";

    try {
        const data = await apiRequest("/api/auth/register", {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem("eventhub_token", authToken);

        registerForm.reset();
        updateNavigationVisibility();

        showToast(`Account created! Welcome, ${currentUser.username}!`, "success");
        showSection("upcoming-events", "Upcoming Events");
    } catch (err) {
        registerErrorMsg.textContent = err.message;
        registerErrorMsg.classList.add("show");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Free Account";
    }
});

/* ==========================================================================
   DASHBOARD SECTION
   ========================================================================== */

async function loadDashboard() {
    try {
        const [stats, upcomingEvents] = await Promise.all([
            apiRequest("/api/dashboard/stats"),
            apiRequest("/api/events?filter=upcoming")
        ]);

        document.getElementById("statUpcoming").textContent = stats.upcoming_events || 0;
        document.getElementById("statPast").textContent = stats.past_events || 0;
        document.getElementById("statRegistrations").textContent = stats.total_registrations || 0;
        document.getElementById("statUsers").textContent = stats.total_users || 0;

        const container = document.getElementById("dashUpcomingList");
        if (!upcomingEvents || upcomingEvents.length === 0) {
            container.innerHTML = `<div class="empty-state">No upcoming events scheduled.</div>`;
            return;
        }

        container.innerHTML = upcomingEvents.slice(0, 4).map(event => `
            <div class="dash-event-item">
                <div class="dash-event-info">
                    <strong>${escapeHTML(event.title)}</strong>
                    <span>📅 ${formatDate(event.date)} &bull; 📍 ${escapeHTML(event.location || "Campus Venue")}</span>
                </div>
                <span class="table-badge emerald">Upcoming</span>
            </div>
        `).join("");
    } catch (err) {
        showToast("Error loading dashboard metrics: " + err.message, "error");
    }
}

document.getElementById("dashCreateEventBtn")?.addEventListener("click", () => {
    openEventModal();
});

/* ==========================================================================
   UPCOMING EVENTS SECTION
   ========================================================================== */

const upcomingSearchInput = document.getElementById("upcomingSearchInput");
const upcomingClearSearch = document.getElementById("upcomingClearSearch");

async function loadUpcomingEvents(search = "") {
    const grid = document.getElementById("upcomingEventsGrid");
    grid.innerHTML = `<div class="loading-spinner">Loading upcoming events...</div>`;

    try {
        const query = search ? `&search=${encodeURIComponent(search)}` : "";
        const events = await apiRequest(`/api/events?filter=upcoming${query}`);

        if (events.length === 0) {
            grid.innerHTML = `
                <div class="card-panel" style="grid-column: 1 / -1; padding: 40px; text-align: center;">
                    <div class="empty-icon">📅</div>
                    <h3>No upcoming events found</h3>
                    <p class="subtext">There are currently no scheduled future events matching your search.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = events.map(event => `
            <article class="event-card">
                <div class="event-card-header">
                    <span class="event-badge upcoming">Available</span>
                    <span class="event-date-chip">📅 ${formatDate(event.date)}</span>
                </div>
                <div class="event-card-body">
                    <h3>${escapeHTML(event.title)}</h3>
                    <p class="event-description">${escapeHTML(event.description || "No description provided for this event.")}</p>
                    
                    <div class="event-meta-info">
                        <div class="event-meta-item">
                            <span>📍</span> <span>${escapeHTML(event.location || "Tech Campus Venue")}</span>
                        </div>
                    </div>

                    <div class="event-card-footer">
                        <span class="attendee-count">👥 ${event.participant_count} Registered</span>
                        <button class="btn btn-primary btn-sm register-card-btn" data-event-id="${event.id}">
                            Register Online ›
                        </button>
                    </div>
                </div>
            </article>
        `).join("");

        grid.querySelectorAll(".register-card-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const eventId = btn.dataset.eventId;
                showSection("event-registration", "Event Registration");
                setTimeout(() => selectEventForRegistration(eventId), 50);
            });
        });
    } catch (err) {
        grid.innerHTML = `<div class="card-panel" style="grid-column: 1 / -1; padding: 30px; color: var(--danger);">Failed to load events: ${escapeHTML(err.message)}</div>`;
    }
}

upcomingSearchInput?.addEventListener("input", debounce(e => {
    const val = e.target.value.trim();
    upcomingClearSearch.classList.toggle("show", val.length > 0);
    loadUpcomingEvents(val);
}, 250));

upcomingClearSearch?.addEventListener("click", () => {
    upcomingSearchInput.value = "";
    upcomingClearSearch.classList.remove("show");
    loadUpcomingEvents();
});

/* ==========================================================================
   PAST EVENTS SECTION
   ========================================================================== */

const pastSearchInput = document.getElementById("pastSearchInput");
const pastClearSearch = document.getElementById("pastClearSearch");

async function loadPastEvents(search = "") {
    const grid = document.getElementById("pastEventsGrid");
    grid.innerHTML = `<div class="loading-spinner">Loading past events...</div>`;

    try {
        const query = search ? `&search=${encodeURIComponent(search)}` : "";
        const events = await apiRequest(`/api/events?filter=past${query}`);

        if (events.length === 0) {
            grid.innerHTML = `
                <div class="card-panel" style="grid-column: 1 / -1; padding: 40px; text-align: center;">
                    <div class="empty-icon">⌛</div>
                    <h3>No past events found</h3>
                    <p class="subtext">There are no archived past events matching your search.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = events.map(event => `
            <article class="event-card">
                <div class="event-card-header past-header">
                    <span class="event-badge past">Completed</span>
                    <span class="event-date-chip">📅 ${formatDate(event.date)}</span>
                </div>
                <div class="event-card-body">
                    <h3>${escapeHTML(event.title)}</h3>
                    <p class="event-description">${escapeHTML(event.description || "No description provided.")}</p>
                    
                    <div class="event-meta-info">
                        <div class="event-meta-item">
                            <span>📍</span> <span>${escapeHTML(event.location || "Campus Venue")}</span>
                        </div>
                    </div>

                    <div class="event-card-footer">
                        <span class="attendee-count">👥 ${event.participant_count} Total Attendees</span>
                        <span class="table-badge slate">Concluded</span>
                    </div>
                </div>
            </article>
        `).join("");
    } catch (err) {
        grid.innerHTML = `<div class="card-panel" style="grid-column: 1 / -1; padding: 30px; color: var(--danger);">Failed to load past events: ${escapeHTML(err.message)}</div>`;
    }
}

pastSearchInput?.addEventListener("input", debounce(e => {
    const val = e.target.value.trim();
    pastClearSearch.classList.toggle("show", val.length > 0);
    loadPastEvents(val);
}, 250));

pastClearSearch?.addEventListener("click", () => {
    pastSearchInput.value = "";
    pastClearSearch.classList.remove("show");
    loadPastEvents();
});

/* ==========================================================================
   EVENT REGISTRATION SECTION
   ========================================================================== */

const regSelectEvent = document.getElementById("regSelectEvent");
const regParticipantName = document.getElementById("regParticipantName");
const registrationForm = document.getElementById("registrationForm");
const registrationPickerList = document.getElementById("registrationPickerList");

async function loadRegistrationEvents() {
    try {
        const events = await apiRequest("/api/events?filter=upcoming");
        cachedEvents = events;

        // Populate left picker list
        if (events.length === 0) {
            registrationPickerList.innerHTML = `<div class="empty-state">No upcoming events currently available for registration.</div>`;
            regSelectEvent.innerHTML = `<option value="">No events available</option>`;
            return;
        }

        registrationPickerList.innerHTML = events.map(event => `
            <div class="picker-item" data-event-id="${event.id}">
                <div class="picker-item-details">
                    <strong>${escapeHTML(event.title)}</strong>
                    <span>📅 ${formatDate(event.date)} &bull; 📍 ${escapeHTML(event.location || "Campus")}</span>
                </div>
                <span class="btn btn-secondary btn-sm select-btn">Select</span>
            </div>
        `).join("");

        // Populate dropdown
        regSelectEvent.innerHTML = `
            <option value="">-- Choose an event --</option>
            ${events.map(e => `<option value="${e.id}">${escapeHTML(e.title)} (${e.date})</option>`).join("")}
        `;

        // Pre-fill name if user is logged in
        if (currentUser && !regParticipantName.value) {
            regParticipantName.value = currentUser.username;
        }

        // Attach picker item click
        registrationPickerList.querySelectorAll(".picker-item").forEach(item => {
            item.addEventListener("click", () => {
                selectEventForRegistration(item.dataset.eventId);
            });
        });
    } catch (err) {
        showToast("Error loading registration events: " + err.message, "error");
    }
}

function selectEventForRegistration(eventId) {
    if (!eventId) return;
    regSelectEvent.value = eventId;

    registrationPickerList.querySelectorAll(".picker-item").forEach(item => {
        item.classList.toggle("selected", item.dataset.eventId === String(eventId));
    });
}

regSelectEvent?.addEventListener("change", () => {
    selectEventForRegistration(regSelectEvent.value);
});

registrationForm?.addEventListener("submit", async e => {
    e.preventDefault();

    const eventId = parseInt(regSelectEvent.value, 10);
    const participantName = regParticipantName.value.trim();
    const submitBtn = document.getElementById("regSubmitBtn");

    if (!eventId || !participantName) {
        showToast("Please select an event and provide participant name", "error");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Processing Registration...";

    try {
        const res = await apiRequest("/api/registrations", {
            method: "POST",
            body: JSON.stringify({
                event_id: eventId,
                participant_name: participantName
            })
        });

        showToast(`Registration confirmed for "${res.participant_name}"!`, "success");
        registrationForm.reset();
        if (currentUser) regParticipantName.value = currentUser.username;
        loadRegistrationEvents();

        if (currentUser) {
            // Suggest viewing in My Registrations
            setTimeout(() => {
                showSection("my-registrations", "My Registrations");
            }, 800);
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Confirm & Register Online";
    }
});

/* ==========================================================================
   MY REGISTRATIONS (USER)
   ========================================================================== */

async function loadMyRegistrations() {
    const tbody = document.getElementById("myRegistrationsTbody");
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Loading your registrations...</td></tr>`;

    try {
        const registrations = await apiRequest("/api/registrations");

        if (registrations.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <div class="empty-icon">🎟️</div>
                        You haven't registered for any events yet.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = registrations.map(reg => `
            <tr>
                <td><strong>#${reg.id}</strong></td>
                <td><strong>${escapeHTML(reg.event_title)}</strong></td>
                <td>📅 ${formatDate(reg.event_date)}</td>
                <td>${escapeHTML(reg.participant_name)}</td>
                <td>${new Date(reg.registered_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-danger btn-sm cancel-reg-btn" data-reg-id="${reg.id}">
                        Cancel
                    </button>
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".cancel-reg-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteRegistration(btn.dataset.regId));
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--danger); text-align: center; padding: 20px;">${escapeHTML(err.message)}</td></tr>`;
    }
}

async function deleteRegistration(regId) {
    if (!confirm("Are you sure you want to cancel this registration?")) return;

    try {
        await apiRequest(`/api/registrations/${regId}`, { method: "DELETE" });
        showToast("Registration cancelled successfully.", "info");
        if (currentUser?.role === "admin") {
            loadAllRegistrations();
        } else {
            loadMyRegistrations();
        }
    } catch (err) {
        showToast("Failed to cancel registration: " + err.message, "error");
    }
}

/* ==========================================================================
   MANAGE EVENTS (ADMIN CRUD)
   ========================================================================== */

const manageEventsSearchInput = document.getElementById("manageEventsSearchInput");
const openCreateEventModalBtn = document.getElementById("openCreateEventModalBtn");
const closeEventModalBtn = document.getElementById("closeEventModalBtn");
const cancelEventModalBtn = document.getElementById("cancelEventModalBtn");

async function loadManageEvents(search = "") {
    const tbody = document.getElementById("manageEventsTbody");
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Loading events...</td></tr>`;

    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const events = await apiRequest(`/api/events${query}`);

        if (events.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No events found matching your criteria.</td></tr>`;
            return;
        }

        tbody.innerHTML = events.map(event => `
            <tr>
                <td><strong>${escapeHTML(event.title)}</strong></td>
                <td>📅 ${formatDate(event.date)}</td>
                <td>📍 ${escapeHTML(event.location || "Campus")}</td>
                <td>👥 ${event.participant_count}</td>
                <td>
                    <span class="table-badge ${event.is_upcoming ? "emerald" : "slate"}">
                        ${event.is_upcoming ? "Upcoming" : "Past"}
                    </span>
                </td>
                <td class="text-right">
                    <div class="table-actions">
                        <button class="btn btn-secondary btn-sm edit-event-btn" data-event-id="${event.id}">
                            Edit
                        </button>
                        <button class="btn btn-danger btn-sm delete-event-btn" data-event-id="${event.id}">
                            Delete
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".edit-event-btn").forEach(btn => {
            btn.addEventListener("click", () => openEditEventModal(btn.dataset.eventId));
        });

        tbody.querySelectorAll(".delete-event-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteEvent(btn.dataset.eventId));
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--danger); text-align: center; padding: 20px;">${escapeHTML(err.message)}</td></tr>`;
    }
}

manageEventsSearchInput?.addEventListener("input", debounce(e => {
    loadManageEvents(e.target.value.trim());
}, 250));

function openEventModal(event = null) {
    eventModalForm.reset();
    if (event) {
        eventModalTitle.textContent = "Edit Event Details";
        eventModalId.value = event.id;
        eventModalTitleInput.value = event.title;
        eventModalDateInput.value = event.date;
        eventModalLocationInput.value = event.location || "";
        eventModalDescInput.value = event.description || "";
    } else {
        eventModalTitle.textContent = "Create New Event";
        eventModalId.value = "";
    }
    eventModal.classList.add("open");
    eventModal.setAttribute("aria-hidden", "false");
}

function closeEventModal() {
    eventModal.classList.remove("open");
    eventModal.setAttribute("aria-hidden", "true");
}

openCreateEventModalBtn?.addEventListener("click", () => openEventModal());
closeEventModalBtn?.addEventListener("click", closeEventModal);
cancelEventModalBtn?.addEventListener("click", closeEventModal);

eventModal?.addEventListener("click", e => {
    if (e.target === eventModal) closeEventModal();
});

async function openEditEventModal(eventId) {
    try {
        const event = await apiRequest(`/api/events/${eventId}`);
        openEventModal(event);
    } catch (err) {
        showToast("Error retrieving event: " + err.message, "error");
    }
}

eventModalForm?.addEventListener("submit", async e => {
    e.preventDefault();

    const id = eventModalId.value;
    const title = eventModalTitleInput.value.trim();
    const date = eventModalDateInput.value;
    const location = eventModalLocationInput.value.trim();
    const description = eventModalDescInput.value.trim();
    const saveBtn = document.getElementById("saveEventModalBtn");

    saveBtn.disabled = true;

    try {
        if (id) {
            // Edit existing event
            await apiRequest(`/api/events/${id}`, {
                method: "PUT",
                body: JSON.stringify({ title, date, location, description })
            });
            showToast("Event details updated successfully.", "success");
        } else {
            // Create event
            await apiRequest("/api/events", {
                method: "POST",
                body: JSON.stringify({ title, date, location, description })
            });
            showToast("New event created successfully.", "success");
        }

        closeEventModal();
        loadManageEvents();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        saveBtn.disabled = false;
    }
});

async function deleteEvent(eventId) {
    if (!confirm("Are you sure you want to delete this event? This will also remove all associated registrations.")) return;

    try {
        await apiRequest(`/api/events/${eventId}`, { method: "DELETE" });
        showToast("Event deleted successfully.", "info");
        loadManageEvents();
    } catch (err) {
        showToast("Failed to delete event: " + err.message, "error");
    }
}

/* ==========================================================================
   PARTICIPANT REGISTRATIONS (ADMIN)
   ========================================================================== */

const participantSearchInput = document.getElementById("participantSearchInput");

async function loadAllRegistrations(search = "") {
    const tbody = document.getElementById("allRegistrationsTbody");
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading participant registrations...</td></tr>`;

    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const registrations = await apiRequest(`/api/registrations${query}`);

        if (registrations.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No participant registrations found.</td></tr>`;
            return;
        }

        tbody.innerHTML = registrations.map(reg => `
            <tr>
                <td><strong>#${reg.id}</strong></td>
                <td><strong>${escapeHTML(reg.participant_name)}</strong></td>
                <td>${escapeHTML(reg.event_title)}</td>
                <td>📅 ${formatDate(reg.event_date)}</td>
                <td>${escapeHTML(reg.registered_by_user || "Guest / Direct")}</td>
                <td>${new Date(reg.registered_at).toLocaleDateString()}</td>
                <td class="text-right">
                    <button class="btn btn-danger btn-sm remove-reg-btn" data-reg-id="${reg.id}">
                        Remove
                    </button>
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".remove-reg-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteRegistration(btn.dataset.regId));
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" style="color: var(--danger); text-align: center; padding: 20px;">${escapeHTML(err.message)}</td></tr>`;
    }
}

participantSearchInput?.addEventListener("input", debounce(e => {
    loadAllRegistrations(e.target.value.trim());
}, 250));

/* ==========================================================================
   MANAGE USERS (ADMIN)
   ========================================================================== */

const userSearchInput = document.getElementById("userSearchInput");

async function loadUsers(search = "") {
    const tbody = document.getElementById("usersTbody");
    tbody.innerHTML = `<tr><td colspan="4" class="empty-state">Loading users directory...</td></tr>`;

    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const users = await apiRequest(`/api/users${query}`);

        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-state">No users found matching search.</td></tr>`;
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr>
                <td><strong>#${user.id}</strong></td>
                <td><strong>${escapeHTML(user.username)}</strong></td>
                <td>
                    <span class="table-badge ${user.role === "admin" ? "blue" : "emerald"}">
                        ${escapeHTML(user.role)}
                    </span>
                </td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
            </tr>
        `).join("");
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" style="color: var(--danger); text-align: center; padding: 20px;">${escapeHTML(err.message)}</td></tr>`;
    }
}

userSearchInput?.addEventListener("input", debounce(e => {
    loadUsers(e.target.value.trim());
}, 250));

/* ==========================================================================
   REPORTS SECTION (ADMIN)
   ========================================================================== */

async function loadReports() {
    const reportTbody = document.getElementById("reportEventTbody");
    const reportRecent = document.getElementById("reportRecentList");

    reportTbody.innerHTML = `<tr><td colspan="4" class="empty-state">Loading report data...</td></tr>`;
    reportRecent.innerHTML = `<div class="empty-state">Loading logs...</div>`;

    try {
        const data = await apiRequest("/api/dashboard/reports");

        // Event distribution
        if (data.event_distribution.length === 0) {
            reportTbody.innerHTML = `<tr><td colspan="4" class="empty-state">No events to report.</td></tr>`;
        } else {
            reportTbody.innerHTML = data.event_distribution.map(item => `
                <tr>
                    <td><strong>${escapeHTML(item.title)}</strong></td>
                    <td>📅 ${formatDate(item.date)}</td>
                    <td>
                        <span class="table-badge ${item.status === "Upcoming" ? "emerald" : "slate"}">
                            ${escapeHTML(item.status)}
                        </span>
                    </td>
                    <td><strong>${item.participant_count}</strong> attendees</td>
                </tr>
            `).join("");
        }

        // Recent registrations
        if (data.recent_registrations.length === 0) {
            reportRecent.innerHTML = `<div class="empty-state">No recent registrations logged.</div>`;
        } else {
            reportRecent.innerHTML = data.recent_registrations.map(item => `
                <div class="recent-reg-item">
                    <div>
                        <strong>${escapeHTML(item.participant_name)}</strong>
                        <span> registered for <em>${escapeHTML(item.event_title)}</em></span>
                    </div>
                    <span>${new Date(item.registered_at).toLocaleDateString()}</span>
                </div>
            `).join("");
        }
    } catch (err) {
        reportTbody.innerHTML = `<tr><td colspan="4" style="color: var(--danger);">${escapeHTML(err.message)}</td></tr>`;
        reportRecent.innerHTML = `<div style="color: var(--danger);">${escapeHTML(err.message)}</div>`;
    }
}

/* ==========================================================================
   INITIALIZATION
   ========================================================================== */

window.addEventListener("DOMContentLoaded", () => {
    checkAuthSession();
});
