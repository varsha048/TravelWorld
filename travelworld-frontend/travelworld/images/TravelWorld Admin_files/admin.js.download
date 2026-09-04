const BASE_URL = "http://127.0.0.1:5000/api/v1";

async function apiRequest(endpoint, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem("adminToken");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const options = { 
    method, 
    headers,
    credentials: "include"
  };
  
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${endpoint}`, options);
  const data = await res.json();

  if (!res.ok) throw new Error(data.message || "Request failed");
  return data;
}

function showDashboard() {
  document.getElementById("loginView").classList.add("hidden");
  document.getElementById("dashboardView").classList.remove("hidden");
  loadAnalytics();
  loadBookings();
  loadTours();
  loadMessages();
  loadEscapes();
}

function showLogin() {
  document.getElementById("dashboardView").classList.add("hidden");
  document.getElementById("loginView").classList.remove("hidden");
}

async function adminLogin() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const errorEl = document.getElementById("loginError");
  errorEl.textContent = "";

  try {
    const result = await apiRequest("/auth/login", "POST", { email, password });

    if (result.data.role !== "admin") {
      errorEl.textContent = "This account is not an admin.";
      return;
    }

    if (result.token) {
        localStorage.setItem("adminToken", result.token);
    }

    showDashboard();
  } catch (err) {
    errorEl.textContent = err.message;
  }
}

async function adminLogout() {
  try {
    await apiRequest("/auth/logout", "POST");
  } catch (err) {
    console.warn("Logout failed on server, but proceeding locally");
  }
  localStorage.removeItem("adminToken");
  showLogin();
}

async function loadTours() {
  try {
    const result = await apiRequest("/tours");
    renderTourTable(result.data);
  } catch (err) {
    alert(err.message);
  }
}

let adminTours = [];

function renderTourTable(tours) {
  adminTours = tours;
  document.getElementById("tourCount").textContent = tours.length;
  const body = document.getElementById("tourTableBody");
  
  body.innerHTML = tours.map((t) => {
    // Escape quotes in strings just to be safe for rendering the table cells
    const title = (t.title || "").replace(/</g, "&lt;");
    const city = (t.city || "").replace(/</g, "&lt;");
    return `
      <tr>
        <td>${title}</td>
        <td>${city}</td>
        <td>Rs.${t.price}</td>
        <td>${t.featured ? "✅" : "—"}</td>
        <td>
          <button onclick="editTourById('${t._id}')">Edit</button>
          <button class="secondary" onclick="deleteTour('${t._id}')">Delete</button>
        </td>
      </tr>
    `;
  }).join("");
}

function editTourById(id) {
  const tour = adminTours.find(t => t._id == id);
  if (tour) editTour(tour);
}

function editTour(tour) {
  document.getElementById("formTitle").textContent = "Edit Tour";
  document.getElementById("tourId").value = tour._id;
  document.getElementById("title").value = tour.title;
  document.getElementById("city").value = tour.city;
  document.getElementById("photo").value = tour.photo;
  document.getElementById("desc").value = tour.desc;
  document.getElementById("price").value = tour.price;
  document.getElementById("distance").value = tour.distance;
  document.getElementById("maxGroupSize").value = tour.maxGroupSize;
  document.getElementById("featured").checked = tour.featured;
  window.scrollTo(0, 0);
}

function resetForm() {
  document.getElementById("formTitle").textContent = "Add New Tour";
  ["tourId", "title", "city", "photo", "desc", "price", "distance", "maxGroupSize"]
    .forEach((id) => (document.getElementById(id).value = ""));
  document.getElementById("featured").checked = false;
}

async function saveTour() {
  const id = document.getElementById("tourId").value;
  const payload = {
    title: document.getElementById("title").value,
    city: document.getElementById("city").value,
    photo: document.getElementById("photo").value,
    desc: document.getElementById("desc").value,
    price: Number(document.getElementById("price").value),
    distance: Number(document.getElementById("distance").value) || 0,
    maxGroupSize: Number(document.getElementById("maxGroupSize").value) || 10,
    featured: document.getElementById("featured").checked,
  };

  try {
    if (id) {
      await apiRequest(`/tours/${id}`, "PUT", payload);
    } else {
      await apiRequest("/tours", "POST", payload);
    }
    resetForm();
    loadTours();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteTour(id) {
  if (!confirm("Delete this tour?")) return;
  try {
    await apiRequest(`/tours/${id}`, "DELETE");
    loadTours();
  } catch (err) {
    alert(err.message);
  }
}

// AUTO INIT
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("adminToken");
  if (token) showDashboard();
  else showLogin();
});

async function uploadImage() {
  const fileInput = document.getElementById("photoFile");
  if (!fileInput.files.length) return;
  
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const res = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      credentials: "include",
      body: formData
    });
    
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Upload failed");
    
    document.getElementById("photo").value = data.url;
    alert("Image uploaded successfully!");
  } catch (err) {
    alert(err.message);
  }
}

async function loadMessages() {
  try {
    const result = await apiRequest("/contact", "GET");
    const tbody = document.getElementById("messagesTableBody");
    
    if (!result.data || result.data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No inquiries yet.</td></tr>`;
      return;
    }
    
    tbody.innerHTML = result.data.map(m => `
      <tr>
        <td>${new Date(m.createdAt || m.created_at || m.date || new Date()).toLocaleString()}</td>
        <td>${m.name}</td>
        <td>${m.email}</td>
        <td>${m.message}</td>
        <td>
            <button onclick="openReplyModal('${m.email}')">Reply</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load messages", err);
  }
}

function openReplyModal(email) {
    document.getElementById("replyModal").classList.remove("hidden");
    document.getElementById("replyEmailLabel").textContent = email;
    document.getElementById("replyEmailInput").value = email;
    document.getElementById("replyTextInput").value = "";
    document.getElementById("replyStatus").textContent = "";
}

function closeReplyModal() {
    document.getElementById("replyModal").classList.add("hidden");
}

async function sendReply() {
    const email = document.getElementById("replyEmailInput").value;
    const replyText = document.getElementById("replyTextInput").value.trim();
    const statusEl = document.getElementById("replyStatus");
    
    if (!replyText) {
        statusEl.textContent = "Please type a reply.";
        statusEl.style.color = "red";
        return;
    }
    
    statusEl.textContent = "Sending email...";
    statusEl.style.color = "#666";
    
    try {
        const result = await apiRequest("/contact/reply", "POST", { email, replyText });
        if (result && result.status === "success") {
            statusEl.textContent = "Reply sent successfully!";
            statusEl.style.color = "green";
            setTimeout(closeReplyModal, 1500);
        } else {
            statusEl.textContent = result ? result.message : "Failed to send email.";
            statusEl.style.color = "red";
        }
    } catch (err) {
        statusEl.textContent = err.message;
        statusEl.style.color = "red";
    }
}

// --- ESCAPES ADMIN LOGIC ---

function switchTab(tab) {
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('sectionDashboard').classList.add('hidden');
  document.getElementById('sectionBookings').classList.add('hidden');
  document.getElementById('sectionTours').classList.add('hidden');
  document.getElementById('sectionEscapes').classList.add('hidden');
  document.getElementById('sectionInquiries').classList.add('hidden');
  
  if (tab === 'dashboard') {
    document.getElementById('tabDashboard').classList.add('active');
    document.getElementById('sectionDashboard').classList.remove('hidden');
  } else if (tab === 'bookings') {
    document.getElementById('tabBookings').classList.add('active');
    document.getElementById('sectionBookings').classList.remove('hidden');
  } else if (tab === 'tours') {
    document.getElementById('tabTours').classList.add('active');
    document.getElementById('sectionTours').classList.remove('hidden');
  } else if (tab === 'escapes') {
    document.getElementById('tabEscapes').classList.add('active');
    document.getElementById('sectionEscapes').classList.remove('hidden');
  } else if (tab === 'inquiries') {
    document.getElementById('tabInquiries').classList.add('active');
    document.getElementById('sectionInquiries').classList.remove('hidden');
  }
}

async function loadBookings() {
    try {
        const result = await apiRequest("/bookings");
        renderBookingsTable(result.data || []);
    } catch(err) {
        console.error("Failed to load bookings", err);
    }
}

function renderBookingsTable(bookings) {
    const body = document.getElementById("bookingsTableBody");
    if (!body) return;
    body.innerHTML = bookings.map(b => {
        const isEscape = b.booking_type === "escape";
        const dateStr = new Date(b.date).toLocaleString();
        const itemName = isEscape ? b.escape.title : b.tour.title;
        const total = isEscape ? b.escape.price * b.guests : (b.totalPrice || b.tour.price * b.guests);
        const typeBadge = isEscape 
            ? `<span style="background:#a855f7; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">Escape</span>`
            : `<span style="background:#3b82f6; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">Tour</span>`;
            
        const statusOptions = ["pending", "confirmed", "rejected", "cancelled"];
        const statusSelect = `
            <select onchange="updateBookingStatus('${b._id}', '${b.booking_type}', this.value)" style="padding: 4px; border-radius: 4px; text-transform: capitalize;">
                ${statusOptions.map(s => `<option value="${s}" ${b.status === s ? "selected" : ""}>${s}</option>`).join("")}
            </select>
        `;
            
        return `
            <tr>
                <td>${dateStr}</td>
                <td>${b.guestName || b.user.username}</td>
                <td>${b.guestPhone || "N/A"}</td>
                <td>${typeBadge}</td>
                <td>${itemName}</td>
                <td>${b.guests}</td>
                <td>Rs.${total}</td>
                <td>${statusSelect}</td>
            </tr>
        `;
    }).join("");
}

async function updateBookingStatus(bookingId, type, newStatus) {
    try {
        const endpoint = type === "escape" 
            ? `/escapes/bookings/${bookingId}/status`
            : `/bookings/${bookingId}/status`;
            
        await apiRequest(endpoint, "PUT", { status: newStatus });
        loadBookings();
    } catch (err) {
        alert("Failed to update status: " + err.message);
        loadBookings(); // reload to reset the dropdown
    }
}

let adminEscapes = [];

async function loadEscapes() {
  try {
    const result = await apiRequest("/escapes");
    adminEscapes = result.data || [];
    renderEscapeTable(adminEscapes);
  } catch(err) {
    console.error("Failed to load escapes", err);
  }
}

function renderEscapeTable(escapes) {
  const body = document.getElementById("escapeTableBody");
  if (!body) return;
  body.innerHTML = escapes.map(e => {
    const start = new Date(e.startDate).toLocaleDateString();
    const end = new Date(e.endDate).toLocaleDateString();
    const available = e.totalSlots - e.bookedSlots;
    return `
      <tr>
        <td>${e.title}</td>
        <td>${start} - ${end}</td>
        <td>Rs.${e.price}</td>
        <td>${available}/${e.totalSlots} left</td>
        <td>
          <button onclick="editEscapeById('${e._id}')">Edit</button>
          <button class="secondary" onclick="deleteEscape('${e._id}')">Delete</button>
        </td>
      </tr>
    `;
  }).join("");
}

function editEscapeById(id) {
  const escape = adminEscapes.find(e => e._id == id);
  if (!escape) return;
  
  document.getElementById("escFormTitle").textContent = "Edit Escape";
  document.getElementById("escId").value = escape._id;
  document.getElementById("escTitle").value = escape.title;
  document.getElementById("escCity").value = escape.city;
  document.getElementById("escPhoto").value = escape.photo;
  document.getElementById("escDesc").value = escape.desc;
  document.getElementById("escItinerary").value = escape.itinerary || "";
  document.getElementById("escPrice").value = escape.price;
  document.getElementById("escSlots").value = escape.totalSlots;
  document.getElementById("escStart").value = escape.startDate.split('T')[0];
  document.getElementById("escEnd").value = escape.endDate.split('T')[0];
  
  // scroll to top
  document.querySelector('.main-content').scrollTop = 0;
}

function resetEscapeForm() {
  document.getElementById("escFormTitle").textContent = "Add New Escape";
  document.querySelectorAll('#sectionEscapes input, #sectionEscapes textarea').forEach(e => e.value = '');
  document.getElementById("escFormMsg").textContent = "";
}

async function saveEscape() {
  const msgEl = document.getElementById("escFormMsg");
  msgEl.textContent = "Saving...";
  msgEl.style.color = "#666";
  
  const id = document.getElementById("escId").value;
  const data = {
    title: document.getElementById("escTitle").value,
    city: document.getElementById("escCity").value,
    photo: document.getElementById("escPhoto").value,
    desc: document.getElementById("escDesc").value,
    itinerary: document.getElementById("escItinerary").value,
    price: document.getElementById("escPrice").value,
    totalSlots: document.getElementById("escSlots").value || 20,
    startDate: document.getElementById("escStart").value,
    endDate: document.getElementById("escEnd").value
  };

  try {
    if (id) {
        await apiRequest(`/escapes/${id}`, "PUT", data);
        msgEl.textContent = "Escape updated successfully!";
    } else {
        await apiRequest("/escapes", "POST", data);
        msgEl.textContent = "Escape created successfully!";
    }
    
    msgEl.style.color = "green";
    loadEscapes();
    setTimeout(resetEscapeForm, 2000);
  } catch (err) {
    msgEl.textContent = err.message;
    msgEl.style.color = "red";
  }
}

async function deleteEscape(id) {
  if (!confirm("Are you sure you want to delete this escape? This will also delete all associated bookings!")) return;
  try {
    await apiRequest(`/escapes/${id}`, "DELETE");
    loadEscapes();
  } catch (err) {
    alert(err.message);
  }
}

async function exportBookings() {
  try {
    const headers = {};
    const token = localStorage.getItem("adminToken");
    if (token) headers["Authorization"] = `Bearer ${token}`;
    
    const response = await fetch(`${BASE_URL}/escapes/bookings/export`, {
      method: "GET",
      headers: headers,
      credentials: "include"
    });
    
    if (!response.ok) throw new Error("Failed to export bookings");
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "escape_bookings.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch(err) {
    alert("Error: " + err.message);
  }
}

// Initializing Dashboard securely
async function initDashboard() {
  try {
    // Use an admin-only endpoint to verify if the user is truly logged in as an admin
    await apiRequest("/contact");
    showDashboard();
  } catch (err) {
    showLogin();
  }
}

document.addEventListener("DOMContentLoaded", initDashboard);

// Analytics Logic
let revenueChartInstance = null;
let popularToursChartInstance = null;

async function loadAnalytics() {
    try {
        const res = await apiRequest("/analytics");
        if (res && res.status === "success") {
            const data = res.data;
            document.getElementById("dashRevenue").textContent = data.totalRevenue.toLocaleString();
            document.getElementById("dashBookings").textContent = data.totalBookings.toLocaleString();
            
            // Render Revenue Chart
            const revCtx = document.getElementById("revenueChart").getContext("2d");
            if (revenueChartInstance) revenueChartInstance.destroy();
            revenueChartInstance = new Chart(revCtx, {
                type: 'line',
                data: {
                    labels: data.monthlyRevenue.labels,
                    datasets: [{
                        label: 'Revenue (Rs)',
                        data: data.monthlyRevenue.data,
                        borderColor: '#f97316',
                        backgroundColor: 'rgba(249, 115, 22, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            // Render Popular Tours Chart
            const popCtx = document.getElementById("popularToursChart").getContext("2d");
            if (popularToursChartInstance) popularToursChartInstance.destroy();
            popularToursChartInstance = new Chart(popCtx, {
                type: 'bar',
                data: {
                    labels: data.popularTours.labels,
                    datasets: [{
                        label: 'Bookings',
                        data: data.popularTours.data,
                        backgroundColor: ['#f97316', '#ec4899', '#3b82f6', '#2dd4bf', '#8b5cf6'],
                        borderRadius: 6
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch(err) {
        console.error("Failed to load analytics", err);
    }
}
