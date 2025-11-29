//admin
// Get all sidebar links and page sections
const sidebarLinks = document.querySelectorAll('.sidebar ul li a');
const pageSections = document.querySelectorAll('.page-section');

// Add click event to each sidebar link
sidebarLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Remove active class from all links
    sidebarLinks.forEach(l => l.classList.remove('active'));
    
    // Add active class to clicked link
    this.classList.add('active');
    
    // Get the target section id from href
    const targetId = this.getAttribute('href').substring(1);
    
    // Hide all sections
    pageSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the target section
    document.getElementById(targetId).classList.add('active');
  });
});

//patient
// Get all sidebar links and page sections
// const sidebarLinks = document.querySelectorAll('.sidebar ul li a');
// const pageSections = document.querySelectorAll('.page-section');

// Add click event to each sidebar link
sidebarLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Remove active class from all links
    sidebarLinks.forEach(l => l.classList.remove('active'));
    
    // Add active class to clicked link
    this.classList.add('active');
    
    // Get the target section id from href
    const targetId = this.getAttribute('href').substring(1);
    
    // Hide all sections
    pageSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Show the target section
    document.getElementById(targetId).classList.add('active');
  });
});

// ====================== API ONLY ======================
const DOCTOR_ID = 1;                      // real doctor empid
const API_BASE  = "";                     // same origin (Flask)
const URLS = {
  stats:        `${API_BASE}/api/doctor/${DOCTOR_ID}/stats`,
  appointments: `${API_BASE}/api/doctor/${DOCTOR_ID}/appointments`,
  calendar:     (y, m) => `${API_BASE}/api/doctor/${DOCTOR_ID}/calendar?year=${y}&month=${m}`,
};

// ====================== HELPERS ======================
async function loadJSON(url) {
  const r = await fetch(url, { headers: { "Accept": "application/json" } });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return await r.json();
}

function fmtDateTime(iso) {
  const d = new Date(iso);
  const opts = { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" };
  return d.toLocaleString(undefined, opts);
}

function findMetricH2(labelText) {
  const cards = document.querySelectorAll(".card .card-body");
  for (const body of cards) {
    const h5 = body.querySelector("h5");
    const h2 = body.querySelector("h2");
    if (h5 && h2 && h5.textContent.trim().toLowerCase() === labelText.toLowerCase()) {
      return h2;
    }
  }
  return null;
}

// Date range helpers
function startOfDayLocal(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0); }
function endOfDayLocal(d)   { return new Date(d.getFullYear(), d.getMonth(), d.getDate()+1, 0, 0, 0, 0); }
function inRange(dt, start, end) { return dt >= start && dt < end; }

// ====================== RENDERERS ======================
function renderStats(stats) {
  const map = { "Today": "today", "This Week": "week", "This Month": "month", "Total Patients": "patients" };
  for (const [label, key] of Object.entries(map)) {
    const el = findMetricH2(label);
    if (el) el.textContent = stats?.[key] ?? "0";
  }
}

function renderAppointments(list) {
  const table = document.querySelector(".content table") || document.querySelector("table");
  if (!table) return;

  const rows = table.querySelectorAll("tr");
  const header = rows[0];
  table.innerHTML = "";
  if (header) table.appendChild(header);

  (list || []).forEach(a => {
    const tr = document.createElement("tr");
    const statusLabel = (a.status || "").charAt(0).toUpperCase() + (a.status || "").slice(1);
    tr.innerHTML = `
      <td>${fmtDateTime(a.datetime)}</td>
      <td>${a.patient_name}</td>
      <td>${a.patient_phone}</td>
      <td>${a.reason}</td>
      <td>${statusLabel}</td>
    `;
    table.appendChild(tr);
  });
}

function renderCalendarGrid(calEl, y, m, statusMap) {
  calEl.innerHTML = "";
  ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].forEach(h => {
    const hd = document.createElement("div");
    hd.className = "calendar-header";
    hd.textContent = h;
    calEl.appendChild(hd);
  });

  const first = new Date(y, m - 1, 1);
  const firstDow = first.getDay();
  for (let i = 0; i < firstDow; i++) {
    const d = document.createElement("div");
    d.className = "calendar-day day-empty";
    calEl.appendChild(d);
  }

  const daysInMonth = new Date(y, m, 0).getDate();
  const today = new Date();
  for (let day = 1; day <= daysInMonth; day++) {
    const dt = new Date(y, m - 1, day);
    const status = statusMap?.[day] || "available";
    const div = document.createElement("div");
    div.className = `calendar-day ${
      status === "booked" ? "day-booked" :
      status === "partial" ? "day-partial" : "day-available"
    }`;
    if (dt.toDateString() === today.toDateString()) div.classList.add("day-today");
    div.textContent = String(day);
    calEl.appendChild(div);
  }
}

function monthLabel(y, m) {
  return new Date(y, m - 1, 1).toLocaleString(undefined, { month: "long", year: "numeric" });
}

function wireCalendarNavigation() {
  const cal = document.querySelector(".calendar");
  if (!cal) return;

  const toolbar = cal.previousElementSibling;
  if (!toolbar) return;
  const titleEl = toolbar.querySelector("h3");
  const [prevBtn, nextBtn] = toolbar.querySelectorAll("button");

  const now = new Date();
  const state = { y: now.getFullYear(), m: now.getMonth() + 1 };

  async function refresh() {
    titleEl && (titleEl.textContent = monthLabel(state.y, state.m));
    const map = await loadJSON(URLS.calendar(state.y, state.m));
    renderCalendarGrid(cal, state.y, state.m, map);
  }

  prevBtn?.addEventListener("click", async () => {
    state.m -= 1;
    if (state.m === 0) { state.m = 12; state.y -= 1; }
    await refresh();
  });

  nextBtn?.addEventListener("click", async () => {
    state.m += 1;
    if (state.m === 13) { state.m = 1; state.y += 1; }
    await refresh();
  });

  refresh();
}

// ====================== BOOT ======================
document.addEventListener("DOMContentLoaded", async () => {
  // Stats
  const stats = await loadJSON(URLS.stats);
  renderStats(stats);

  // Today-only appointments
  const now = new Date();
  const start = startOfDayLocal(now);
  const end   = endOfDayLocal(now);
  const params = `?start=${encodeURIComponent(start.toISOString())}&end=${encodeURIComponent(end.toISOString())}`;
  let appts = await loadJSON(URLS.appointments + params);
  appts = (appts || []).filter(a => inRange(new Date(a.datetime), start, end));
  renderAppointments(appts);

  // Calendar
  wireCalendarNavigation();
});