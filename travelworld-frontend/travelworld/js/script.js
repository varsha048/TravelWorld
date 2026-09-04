// VALIDATION HELPERS

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((value || "").trim());
}

function isValidPhone(value) {
  const digits = (value || "").replace(/\D/g, "");
  return digits.length >= 7 && digits.length <= 15;
}

function markInvalid(input) {
  if (input) input.classList.add("input-invalid");
}

function clearInvalid(input) {
  if (input) input.classList.remove("input-invalid");
}

function showFormError(errorEl, message) {
  if (errorEl) errorEl.textContent = message;
}

function clearFormError(errorEl) {
  if (errorEl) errorEl.textContent = "";
}

// LOAD FEATURED TOURS
// HOME PAGE

async function loadFeaturedTours() {
  const container = document.getElementById("featuredTours");

  if (!container) return;

  const result = await apiRequest(
    "/tours/search/getFeaturedTours"
  );

  if (!result) return;

  let html = "";

  result.data.forEach((tour) => {
    // Generate star rating (e.g., 4 or 5 stars based on rating, assuming 4.5 default)
    let starsHtml = "";
    const rating = Math.floor(tour.avgRating || 4.5);
    for(let i=0; i<rating; i++) {
        starsHtml += '<i class="fa-solid fa-star"></i>';
    }

    html += `
      <div class="mini-tour-card" onclick="window.location.href='tour-details.html?id=${tour._id}'">
        <img src="${tour.photo || 'images/tour-img01.jpg'}" onerror="this.onerror=null; this.src='images/tour-img01.jpg';" alt="">
        <div class="mini-tour-content">
          <h4>${tour.title}</h4>
          <div class="duration">03 Nights / 04 Days</div>
          <div class="desc">${tour.desc || tour.city}</div>
          <div class="stars">
            ${starsHtml}
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// LOAD ALL TOURS

async function loadTours() {
  const container = document.getElementById("tourGrid");

  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const magic = params.get("magic");
  let result;
  
  if (magic) {
    if (document.getElementById("magicQuery")) {
      document.getElementById("magicQuery").value = magic;
    }
    const btn = document.querySelector(".magic-btn");
    if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    
    result = await apiRequest("/tours/search/magic", "POST", { query: magic });
    
    if (btn) btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i>';
  } else {
    result = await apiRequest("/tours");
  }

  if (!result) return;


  renderTours(result.data);
}

// RENDER TOURS

function renderTours(tours) {

  const container =
    document.getElementById("tourGrid");

  if (!tours || tours.length === 0) {
    container.innerHTML = `
      <p style="grid-column: 1 / -1; text-align: center; padding: 40px 0; color: #666;">
        No tours match your search. Try a different location or fewer filters.
      </p>
    `;
    return;
  }

  const images = [
    "images/tour-img01.jpg",
    "images/tour-img02.jpg",
    "images/tour-img03.jpg",
    "images/tour-img04.jpg",
    "images/tour-img05.jpg",
    "images/tour-img06.jpg",
    "images/tour-img07.jpg",
    "images/tour-img08.jpg"
  ];

  let html = "";

  tours.forEach((tour, index) => {
    const aiBadge = tour.ai_reason ? `<div style="background: linear-gradient(135deg, #a855f7, #ec4899); color: white; padding: 6px 10px; border-radius: 4px; font-size: 13px; margin-bottom: 12px; line-height: 1.4;"><i class="fa-solid fa-wand-magic-sparkles"></i> <strong>AI Match:</strong> ${tour.ai_reason}</div>` : '';

    html += `
      <div class="tour-card">

        <img
          src="${tour.photo || images[index % images.length]}"
          onerror="this.onerror=null; this.src='${images[index % images.length]}';"
          alt="${tour.title}"
        >

        <div class="tour-content">
          ${aiBadge}
          <div class="tour-top">
            <span>📍 ${tour.city}</span>
            <div>
                <span style="cursor:pointer; margin-right: 10px; font-size: 18px; color: #ec4899;" onclick="toggleWishlist(${tour._id}, this)">♡</span>
                <span>⭐ ${tour.avgRating || 4.5}</span>
            </div>
          </div>

          <h3>${tour.title}</h3>

          <div class="price-row">

            <h4>
              Rs.${tour.price}
              <span>/person</span>
            </h4>

            <a href="tour-details.html?id=${tour._id}">
              <button>Book Now</button>
            </a>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// SEARCH TOURS

async function searchTours() {
  const magicQuery = document.getElementById("magicQuery")?.value || "";

  if (!magicQuery) return;

  const btn = document.querySelector(".magic-btn");
  if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

  // If there's no results grid on this page (e.g. the home page),
  // send the visitor to the tours page with the search applied.
  if (!document.getElementById("tourGrid")) {
    const query = new URLSearchParams({ magic: magicQuery });
    window.location.href = `tours.html?${query.toString()}`;
    return;
  }

  const result = await apiRequest("/tours/search/magic", "POST", { query: magicQuery });
  
  if (btn) btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i>';

  if (!result) return;

  renderTours(result.data);
}

// TOUR COUNT

async function getTourCount() {
  const countElement =
    document.getElementById("tourCount");

  if (!countElement) return;

  const result =
    await apiRequest(
      "/tours/search/getTourCount"
    );

  if (!result) return;

  countElement.textContent =
    result.data;
}

// TOUR DETAILS

async function loadTourDetails() {
  const titleEl = document.getElementById("tourTitle");

  if (!titleEl) return;

  const params =
    new URLSearchParams(
      window.location.search
    );

  const tourId =
    params.get("id");

  if (!tourId) return;

  const result =
    await apiRequest(
      `/tours/${tourId}`
    );

  if (!result) return;

  const tour = result.data;

  document.getElementById("tourMainImg").src = tour.photo;
  document.getElementById("tourTitle").textContent = tour.title;
  document.getElementById("tourLocation").textContent = `📍 ${tour.city}`;
  document.getElementById("tourDesc").textContent = tour.desc;
  
  if (tour.itinerary) {
      document.getElementById("tourItinerary").textContent = tour.itinerary;
  }
  
  // Render reviews
  const reviews = tour.reviews || [];
  const reviewsList = document.getElementById("reviewsList");
  document.getElementById("reviewsCountTitle").textContent = `Reviews (${reviews.length})`;
  document.getElementById("tourReviewsCountHeader").textContent = reviews.length;
  
  let totalRating = 0;
  if (reviews.length > 0) {
      reviewsList.innerHTML = reviews.map(r => {
          totalRating += r.rating;
          const stars = '⭐'.repeat(r.rating);
          const photoImg = r.photoUrl ? `<img src="${r.photoUrl}" alt="Review photo" style="max-width: 150px; border-radius: 8px; margin-top: 10px; border: 1px solid #e2e8f0;">` : '';
          return `
          <div class="review-card" style="margin-bottom:15px; padding:15px; border:1px solid #e2e8f0; border-radius:10px; background:#fff;">
              <div>
                  <h4 style="margin-bottom:5px; color:#1e293b;">${r.user.username} <span style="font-size:0.8rem; font-weight:normal; color:#64748b; margin-left:10px;">${new Date(r.createdAt).toLocaleDateString()}</span></h4>
                  <div style="margin-bottom:5px;">${stars}</div>
                  <p style="color:#475569; font-size:0.95rem; margin-top: 8px;">${r.reviewText}</p>
                  ${photoImg}
              </div>
          </div>
          `;
      }).join("");
      document.getElementById("tourRating").textContent = (totalRating / reviews.length).toFixed(1);
  } else {
      reviewsList.innerHTML = `<p>No reviews yet. Be the first to review!</p>`;
      document.getElementById("tourRating").textContent = "0.0";
  }

  // Show review form if user is logged in
  if (localStorage.getItem("user")) {
      document.getElementById("reviewForm").style.display = "flex";
  }

  document.getElementById("tourPrice").textContent = tour.price;
  document.getElementById("tourBasePrice").textContent = tour.price;
  document.getElementById("tourSubtotal").textContent = tour.price;
  document.getElementById("tourTotal").textContent = tour.price + 10;

  // Save the current tour id on the page so the booking button can use it
  document.body.dataset.tourId = tour._id;
  window.tourBasePrice = tour.price;

  // Init Map and Weather
  initMapAndWeather(tour.city);
}

async function submitReview() {
    const tourId = document.body.dataset.tourId;
    if (!tourId) return;

    const rating = document.getElementById("reviewRating").value;
    const reviewText = document.getElementById("reviewText").value;
    const photoUrl = document.getElementById("reviewPhotoUrl") ? document.getElementById("reviewPhotoUrl").value : null;

    if (!rating || !reviewText) {
        alert("Please provide a rating and a review.");
        return;
    }

    try {
        const payload = { rating: parseInt(rating), reviewText };
        if (photoUrl) {
            payload.photoUrl = photoUrl;
        }
        
        await apiRequest(`/reviews/${tourId}`, "POST", payload);
        alert("Review submitted successfully!");
        document.getElementById("reviewText").value = "";
        if (document.getElementById("reviewPhotoUrl")) {
            document.getElementById("reviewPhotoUrl").value = "";
        }
        loadTourDetails(); // refresh to show new review
    } catch (err) {
        alert(err.message || "Failed to submit review.");
    }
}

async function toggleWishlist(tourId, el) {
    const userStr = localStorage.getItem("user");
    if (!userStr) {
        alert("Please log in to add tours to your wishlist");
        return;
    }
    
    try {
        const result = await apiRequest(`/wishlist/${tourId}`, "POST");
        if (result && result.status === "success") {
            if (result.action === "added") {
                el.textContent = "♥";
            } else {
                el.textContent = "♡";
            }
        }
    } catch (err) {
        console.error("Failed to toggle wishlist", err);
    }
}

// TRIGGERED BY "BOOK NOW" ON THE TOUR DETAILS PAGE

function handleBookNow() {
  const tourId = document.body.dataset.tourId;
  const nameInput = document.getElementById("guestName");
  const phoneInput = document.getElementById("guestPhone");
  const dateInput = document.getElementById("bookingDate");
  const guestsInput = document.getElementById("guestCount");
  const errorEl = document.getElementById("bookingError");

  if (!tourId) {
    alert("Tour information is still loading, please wait a moment.");
    return;
  }

  [nameInput, phoneInput, dateInput, guestsInput].forEach(clearInvalid);
  clearFormError(errorEl);

  const name = nameInput.value.trim();
  const phone = phoneInput.value.trim();
  const date = dateInput.value;
  const guests = parseInt(guestsInput.value, 10);

  if (name.length < 2) {
    markInvalid(nameInput);
    showFormError(errorEl, "Please enter your full name");
    return;
  }

  if (!isValidPhone(phone)) {
    markInvalid(phoneInput);
    showFormError(errorEl, "Please enter a valid phone number");
    return;
  }

  if (!date) {
    markInvalid(dateInput);
    showFormError(errorEl, "Please choose a tour date");
    return;
  }

  const today = new Date().toISOString().split("T")[0];
  if (date < today) {
    markInvalid(dateInput);
    showFormError(errorEl, "The date can't be in the past");
    return;
  }

  if (!guests || guests < 1) {
    markInvalid(guestsInput);
    showFormError(errorEl, "Guests must be at least 1");
    return;
  }

  const userStr = localStorage.getItem("user");
  if (!userStr) {
    alert("Please log in to book a tour");
    window.location.href = "login.html";
    return;
  }

  // Calculate total amount
  const tourPriceStr = document.getElementById("tourPrice").textContent;
  const tourPrice = parseInt(tourPriceStr.replace(/[^0-9]/g, '')) || 0;
  const totalAmount = tourPrice * guests;
  const tourName = document.getElementById("tourTitle").textContent;

  // Store globally for payment processing
  window.pendingBooking = { tourId, name, phone, date, guests };
  
  // Show Payment Modal
  document.getElementById("paymentAmountDisplay").textContent = `Rs. ${totalAmount}`;
  document.getElementById("paymentTourName").textContent = tourName;
  document.getElementById("paymentModalOverlay").classList.add("active");
}

function closePaymentModal() {
  document.getElementById("paymentModalOverlay").classList.remove("active");
  document.getElementById("paymentError").textContent = "";
}

async function processPayment() {
    const payBtn = document.getElementById("payBtn");
    const paySpinner = document.getElementById("paySpinner");
    const errorEl = document.getElementById("paymentError");

    errorEl.textContent = "";

    // For Stripe Checkout, we don't need actual card details on our site.
    // We just trigger the checkout session.
    
    payBtn.disabled = true;
    paySpinner.style.display = "inline-block";

    try {
        const payload = {
            type: window.bookingType || "tour",
            itemId: document.body.dataset.tourId || window.bookingEscapeId,
            guestName: window.bookingGuestName || window.pendingBooking.name,
            guestPhone: window.bookingGuestPhone || window.pendingBooking.phone,
            guests: window.bookingGuests || window.pendingBooking.guests
        };
        
        const result = await apiRequest("/payments/create-checkout-session", "POST", payload);
        
        if (result.status === "success" && result.data && result.data.url) {
            // Redirect to Stripe!
            window.location.href = result.data.url;
        } else {
            throw new Error(result.message || "Failed to initiate payment");
        }
    } catch (err) {
        errorEl.textContent = err.message || "Payment failed. Please try again.";
        payBtn.disabled = false;
        paySpinner.style.display = "none";
    }
}

// REGISTER

async function registerUser(event) {
  event.preventDefault();

  const usernameInput = document.getElementById("username");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorEl = document.getElementById("registerError");

  const username = usernameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  [usernameInput, emailInput, passwordInput].forEach(clearInvalid);
  clearFormError(errorEl);

  if (username.length < 3) {
    markInvalid(usernameInput);
    showFormError(errorEl, "Username must be at least 3 characters");
    return;
  }

  if (!isValidEmail(email)) {
    markInvalid(emailInput);
    showFormError(errorEl, "Please enter a valid email address");
    return;
  }

  if (password.length < 6) {
    markInvalid(passwordInput);
    showFormError(errorEl, "Password must be at least 6 characters");
    return;
  }

  const result =
    await apiRequest(
      "/auth/register",
      "POST",
      {
        username,
        email,
        password,
      }
    );

  if (!result) return;

  alert("Registration Successful");

  window.location.href =
    "login.html";
}

// LOGIN

async function loginUser(event) {
  event.preventDefault();

  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorEl = document.getElementById("loginError");

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  [emailInput, passwordInput].forEach(clearInvalid);
  clearFormError(errorEl);

  if (!isValidEmail(email)) {
    markInvalid(emailInput);
    showFormError(errorEl, "Please enter a valid email address");
    return;
  }

  if (!password) {
    markInvalid(passwordInput);
    showFormError(errorEl, "Please enter your password");
    return;
  }

  const result =
    await apiRequest(
      "/auth/login",
      "POST",
      {
        email,
        password,
      }
    );

  if (!result) return;

  localStorage.setItem("user", JSON.stringify(result.data));
  if (result.token) {
    localStorage.setItem("token", result.token);
  }

  alert("Login Successful");

  window.location.href =
    "index.html";
}

// LOGOUT

async function logout() {
  try {
    await apiRequest("/auth/logout", "POST");
  } catch (err) {
    console.warn("Logout failed on server", err);
  }
  
  localStorage.clear();

  window.location.href =
    "login.html";
}

// CHECK LOGIN

function checkAuth() {
  const userStr = localStorage.getItem("user");
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const myBookingsLink = document.getElementById("myBookingsLink");

  if (userStr) {
    if (loginBtn)
      loginBtn.style.display =
        "none";

    if (registerBtn)
      registerBtn.style.display =
        "none";

    if (logoutBtn)
      logoutBtn.style.display =
        "inline-block";

    if (myBookingsLink)
      myBookingsLink.style.display =
        "inline-block";
  }
}

// BOOK TOUR

async function bookTour(tourId, guestDetails = {}) {
  const userStr = localStorage.getItem("user");

  if (!userStr) {
    alert("Please log in to book a tour");
    window.location.href = "login.html";
    return;
  }

  const result = await apiRequest(
    "/bookings",
    "POST",
    {
      tourId,
      guestName: guestDetails.name,
      guestPhone: guestDetails.phone,
      guests: guestDetails.guests,
    }
  );

  if (!result) return;

  localStorage.setItem(
    "booking",
    JSON.stringify(result.data)
  );

  window.location.href =
    "thankyou.html";
}

// NEWSLETTER SUBSCRIBE

async function subscribeNewsletter(event) {
  event.preventDefault();

  const emailInput = document.getElementById("newsletterEmail");
  const destInput = document.getElementById("newsletterDestination");
  const messageEl = document.getElementById("newsletterMessage");
  const btn = document.getElementById("newsletterBtn");

  clearInvalid(emailInput);
  if (destInput) clearInvalid(destInput);
  clearFormError(messageEl);

  const email = emailInput.value.trim();
  const destination = destInput ? destInput.value.trim() : "";

  if (!isValidEmail(email)) {
    markInvalid(emailInput);
    messageEl.textContent = "Please enter a valid email address.";
    return;
  }
  
  if (destInput && !destination) {
    markInvalid(destInput);
    messageEl.textContent = "Please enter a destination.";
    return;
  }

  if (btn) {
    btn.textContent = "Generating...";
    btn.disabled = true;
  }

  const result = await apiRequest("/newsletter/postcard", "POST", { email, destination });

  if (!result || result.status !== "success") {
    messageEl.textContent = result?.message || "An error occurred.";
    if (btn) {
      btn.textContent = "Subscribe & Generate";
      btn.disabled = false;
    }
    return;
  }

  const postcardTextEl = document.getElementById("newsletterPostcardText");
  const cardEl = document.getElementById("postcardCard");
  
  if (postcardTextEl && cardEl) {
    postcardTextEl.textContent = result.data.postcard;
    cardEl.classList.add("flipped");
  } else {
    messageEl.textContent = "Subscribed! Thanks for joining.";
    messageEl.style.color = "green";
  }
  
  if (btn) {
    btn.textContent = "Subscribe & Generate";
    btn.disabled = false;
  }
  emailInput.value = "";
  if (destInput) destInput.value = "";
}

function resetPostcard() {
  const cardEl = document.getElementById("postcardCard");
  if (cardEl) {
    cardEl.classList.remove("flipped");
  }
}

// CONTACT FORM

async function submitContactForm(event) {
  event.preventDefault();

  const nameInput = document.getElementById("contactName");
  const emailInput = document.getElementById("contactEmail");
  const messageInput = document.getElementById("contactMessage");
  const statusEl = document.getElementById("contactStatus");

  [nameInput, emailInput, messageInput].forEach(clearInvalid);
  clearFormError(statusEl);

  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const message = messageInput.value.trim();

  if (name.length < 2) {
    markInvalid(nameInput);
    statusEl.style.color = "#dc2626";
    statusEl.textContent = "Please enter your name";
    return;
  }

  if (!isValidEmail(email)) {
    markInvalid(emailInput);
    statusEl.style.color = "#dc2626";
    statusEl.textContent = "Please enter a valid email address";
    return;
  }

  if (message.length < 10) {
    markInvalid(messageInput);
    statusEl.style.color = "#dc2626";
    statusEl.textContent = "Message should be at least 10 characters";
    return;
  }

  const result = await apiRequest(
    "/contact",
    "POST",
    { name, email, message }
  );

  if (!result) return;

  statusEl.style.color = "green";
  statusEl.textContent = "Message sent! We'll get back to you soon.";
  document.getElementById("contactForm").reset();
}

// MY BOOKINGS

async function loadMyBookings() {
  const container = document.getElementById("bookingsList");

  if (!container) return;

  const userStr = localStorage.getItem("user");

  if (!userStr) {
    container.innerHTML = `
      <p>Please <a href="login.html">log in</a> to see your bookings.</p>
    `;
    return;
  }

  const result = await apiRequest("/bookings/my");

  if (!result) return;

  const bookings = result.data;

  if (!bookings || bookings.length === 0) {
    container.innerHTML = `
      <p>You haven't booked any tours yet. <a href="tours.html">Browse tours</a> to get started.</p>
    `;
    return;
  }

  container.innerHTML = bookings.map(booking => {
    const isEscape = booking.booking_type === "escape";
    const title = isEscape ? booking.escape.title : booking.tour.title;
    const photo = isEscape ? booking.escape.photo : booking.tour.photo;
    const location = isEscape ? booking.escape.city : booking.tour.city;
    const statusColor = booking.status === "cancelled" ? "#ef4444" : (booking.status === "confirmed" ? "#22c55e" : "#f59e0b");
    const badge = isEscape ? `<span style="background: #a855f7; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 10px;">Next Escape</span>` : "";

    return `
    <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; gap: 20px; align-items: center;">
      <img src="${photo}" alt="tour" style="width: 150px; height: 100px; border-radius: 8px; object-fit: cover;">
      <div style="flex: 1;">
        <h3 style="margin-bottom: 8px;">${title} ${badge}</h3>
        <p style="color: #666; font-size: 14px; margin-bottom: 5px;">📍 ${location}</p>
        <p style="color: #666; font-size: 14px; margin-bottom: 5px;">Guests: ${booking.guests} | Total: Rs.${booking.totalPrice || (booking.escape ? booking.escape.price * booking.guests : 0)}</p>
        <p style="font-size: 14px; font-weight: 600;">Status: <span style="color: ${statusColor}; text-transform: capitalize;">${booking.status}</span></p>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        ${!isEscape ? `<a href="tour-details.html?id=${booking.tour._id}" class="booking-view-link" style="text-align: center;">View Tour</a>` : ''}
        ${booking.ticketUrl && booking.status !== 'cancelled' ? `<a href="http://127.0.0.1:5000${booking.ticketUrl}" target="_blank" class="booking-view-link" style="background: #0ea5e9; text-align: center;"><i class="fa fa-ticket"></i> E-Ticket</a>` : ''}
        ${booking.status !== 'cancelled' ? `<button onclick="cancelBooking(${booking._id}, '${booking.booking_type}')" style="background: #ef4444; color: white; padding: 10px; border-radius: 50px; border: none; cursor: pointer; font-weight: 600;"><i class="fa fa-times"></i> Cancel Booking</button>` : ''}
      </div>
    </div>
  `}).join("");
}

async function cancelBooking(bookingId, bookingType = 'tour') {
    if (!confirm("Are you sure you want to cancel this booking? This action cannot be undone.")) return;
    
    try {
        const result = await apiRequest(`/bookings/my/${bookingId}?type=${bookingType}`, "DELETE");
        if (result && result.status === "success") {
            alert("Booking cancelled successfully.");
            loadMyBookings();
        }
    } catch (err) {
        alert(err.message || "Failed to cancel booking");
    }
}

// PAGE AUTO INIT

document.addEventListener(
  "DOMContentLoaded",
  () => {
    loadFeaturedTours();
    loadTours();
    loadTourDetails();
    getTourCount();
    checkAuth();
    loadMyBookings();
    loadNextEscapes();
  }
);

// CONTACT FORM
async function submitContactForm(event) {
    event.preventDefault();
    
    const nameInput = document.getElementById("contactName");
    const emailInput = document.getElementById("contactEmail");
    const messageInput = document.getElementById("contactMessage");
    const statusText = document.getElementById("contactStatus");
    
    if (!nameInput || !emailInput || !messageInput) return;
    
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const message = messageInput.value.trim();
    
    if (!name || !email || !message) {
        statusText.textContent = "Please fill in all fields.";
        statusText.style.color = "red";
        return;
    }
    
    statusText.textContent = "Sending...";
    statusText.style.color = "#666";
    
    try {
        const result = await apiRequest("/contact", "POST", { name, email, message });
        
        if (result && result.status === "success") {
            statusText.textContent = "Thank you! We'll get back to you soon.";
            statusText.style.color = "green";
            document.getElementById("contactForm").reset();
        } else {
            statusText.textContent = result ? result.message : "Something went wrong.";
            statusText.style.color = "red";
        }
    } catch (err) {
        statusText.textContent = err.message || "Failed to connect to the server.";
        statusText.style.color = "red";
    }
}

// NEXT ESCAPES
let allEscapes = [];

async function loadNextEscapes() {
    const grid = document.getElementById("escapesGrid");
    if (!grid) return;
    
    try {
        const result = await apiRequest("/escapes");
        if (!result || !result.data || result.data.length === 0) {
            grid.innerHTML = `<div style="text-align:center; grid-column:1/-1;">No upcoming escapes planned right now. Check back later!</div>`;
            return;
        }
        
        allEscapes = result.data;
        
        grid.innerHTML = result.data.map(escape => {
            const available = escape.totalSlots - (escape.bookedSlots || 0);
            const percent = ((escape.bookedSlots || 0) / escape.totalSlots) * 100;
            const isLow = available <= 5;
            
            const startDate = new Date(escape.startDate).toLocaleDateString("en-US", { month: "short", day: "numeric" });
            const endDate = new Date(escape.endDate).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
            
            const isSoldOut = available <= 0;
            let actionButton = `<button class="book-escape-btn" onclick="openEscapeModal('${escape._id}', ${escape.price}, '${escape.title.replace(/'/g, "\\'")}')">View Details & Book</button>`;
            
            if (isSoldOut) {
                actionButton = `<button class="book-escape-btn" style="background: #e74c3c; cursor: not-allowed;" disabled>Sold Out</button>`;
            }
            
            return `
            <div class="escape-card">
                <img src="${escape.photo}" alt="${escape.title}">
                <div class="escape-content">
                    <div class="escape-date">
                        <i class="far fa-calendar-alt"></i> ${startDate} - ${endDate}
                    </div>
                    <h3>${escape.title}</h3>
                    <p class="escape-desc">${escape.desc}</p>
                    
                    <div class="slots-container">
                        <div class="slots-label">
                            <span>Available Slots</span>
                            <span style="color: ${isLow ? '#e74c3c' : '#27ae60'}">${isSoldOut ? '0' : available} / ${escape.totalSlots}</span>
                        </div>
                        <div class="slots-bar">
                            <div class="slots-fill ${isLow ? 'low' : ''}" style="width: ${percent}%"></div>
                        </div>
                    </div>
                    
                    <div class="escape-footer">
                        <div class="escape-price">
                            Rs.${escape.price}<span> /person</span>
                        </div>
                        ${actionButton}
                    </div>
                </div>
            </div>`;
        }).join("");
    } catch (err) {
        grid.innerHTML = `<div style="color:red; text-align:center; grid-column:1/-1;">Failed to load escapes.</div>`;
    }
}

function openEscapeModal(id) {
    const escape = allEscapes.find(e => String(e._id) === String(id));
    if (!escape) return;
    
    const startDate = new Date(escape.startDate).toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const endDate = new Date(escape.endDate).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    
    document.getElementById("modalImg").src = escape.photo;
    document.getElementById("modalTitle").textContent = escape.title;
    document.getElementById("modalDate").textContent = `${startDate} - ${endDate}`;
    
    // Parse itinerary into timeline format
    let itineraryHtml = "No itinerary available.";
    if (escape.itinerary) {
        itineraryHtml = escape.itinerary.split("<br>").filter(i => i.trim() !== "").map(item => {
            const parts = item.split(":");
            if (parts.length > 1) {
                return `<div class="itinerary-item"><strong>${parts[0].trim()}</strong> ${parts.slice(1).join(":").trim()}</div>`;
            }
            return `<div class="itinerary-item">${item}</div>`;
        }).join("");
    }
    
    document.getElementById("modalItinerary").innerHTML = itineraryHtml;
    document.getElementById("modalPrice").textContent = escape.price;
    document.getElementById("modalEscapeId").value = escape._id;
    
    document.getElementById("escapeBookingForm").reset();
    document.getElementById("paymentForm").reset();
    document.getElementById("escapeStatus1").textContent = "";
    document.getElementById("escapeStatus").textContent = "";
    document.getElementById("bookingStep1").style.display = "block";
    document.getElementById("bookingStep2").style.display = "none";
    
    // Set initial total
    updateTotalCost();
    
    document.getElementById("escapeModal").style.display = "flex";
}

function closeEscapeModal() {
    document.getElementById("escapeModal").style.display = "none";
}

function updateTotalCost() {
    const priceStr = document.getElementById("modalPrice").textContent;
    const price = parseFloat(priceStr) || 0;
    const count = parseInt(document.getElementById("escapeGuestCount").value) || 1;
    const total = price * count;
    document.getElementById("modalTotalCost").textContent = total;
}

function proceedToPayment(event) {
    event.preventDefault();
    const guestName = document.getElementById("escapeGuestName").value.trim();
    const guestPhone = document.getElementById("escapeGuestPhone").value.trim();
    if (!guestName || !guestPhone) {
        alert("Please fill in all required fields (Name and Phone) before proceeding.");
        return;
    }
    const userStr = localStorage.getItem("user");
    if (!userStr) {
        alert("Please login to book an escape!");
        window.location.href = "login.html";
        return;
    }
    
    // Switch to payment step
    const total = document.getElementById("modalTotalCost").textContent;
    document.getElementById("paymentAmount").textContent = total;
    document.getElementById("bookingStep1").style.display = "none";
    document.getElementById("bookingStep2").style.display = "block";
}

function backToStep1() {
  document.getElementById("bookingStep2").style.display = "none";
  document.getElementById("bookingStep1").style.display = "block";
}

async function submitEscapeBooking(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById("escapeSubmitBtn");
    const statusText = document.getElementById("escapeStatus");
    
    const guestName = document.getElementById("escapeGuestName").value;
    const guestPhone = document.getElementById("escapeGuestPhone").value;
    const guests = parseInt(document.getElementById("escapeGuestCount").value);
    const escapeId = document.getElementById("modalEscapeId").value;
    
    if (!escapeId) {
        statusText.textContent = "Error: Invalid escape selection.";
        statusText.style.color = "red";
        return;
    }

    statusText.textContent = "Redirecting to Stripe Checkout...";
    statusText.style.color = "#666";
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.7";
    
    try {
        const payload = {
            type: "escape",
            itemId: escapeId,
            guestName: guestName,
            guestPhone: guestPhone,
            guests: guests
        };
        
        const result = await apiRequest("/payments/create-checkout-session", "POST", payload);
        
        if (result.status === "success" && result.data && result.data.url) {
            // Redirect to Stripe!
            window.location.href = result.data.url;
        } else {
            throw new Error(result.message || "Failed to initiate payment");
        }
    } catch (err) {
        statusText.textContent = err.message || "Failed to connect to the server.";
        statusText.style.color = "red";
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
    }
}

/* MAP, WEATHER, CURRENCY LOGIC */
async function initMapAndWeather(city) {
    if (!city) return;
    
    try {
        // Geocode with Nominatim (OpenStreetMap)
        const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`);
        const geoData = await geoRes.json();
        
        if (geoData && geoData.length > 0) {
            const lat = geoData[0].lat;
            const lon = geoData[0].lon;
            
            // Init Leaflet Map
            const mapEl = document.getElementById("tourMap");
            if (mapEl) {
                // Clear any existing map instance if reloading
                if (window.tourMapInstance) {
                    window.tourMapInstance.remove();
                }
                const map = L.map('tourMap').setView([lat, lon], 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }).addTo(map);
                L.marker([lat, lon]).addTo(map).bindPopup(`<b>${city}</b>`).openPopup();
                window.tourMapInstance = map;
            }
            
            // Init Weather with Open-Meteo
            const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto&forecast_days=3`);
            const weatherData = await weatherRes.json();
            
            if (weatherData && weatherData.daily) {
                const wc = document.getElementById("weatherContainer");
                if (wc) {
                    let html = '';
                    for (let i = 0; i < weatherData.daily.time.length; i++) {
                        const date = new Date(weatherData.daily.time[i]).toLocaleDateString(undefined, {weekday: 'short', month: 'short', day: 'numeric'});
                        const max = weatherData.daily.temperature_2m_max[i];
                        const min = weatherData.daily.temperature_2m_min[i];
                        const code = weatherData.daily.weathercode[i];
                        
                        // Simple weather icon logic based on WMO codes
                        let icon = '☀️';
                        if (code >= 1 && code <= 3) icon = '⛅';
                        if (code >= 45 && code <= 48) icon = '🌫️';
                        if (code >= 51 && code <= 67) icon = '🌧️';
                        if (code >= 71 && code <= 77) icon = '❄️';
                        if (code >= 95) icon = '⛈️';
                        
                        html += `
                        <div style="background: rgba(255,255,255,0.8); border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; min-width: 120px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <div style="font-weight: 600; font-size: 14px; margin-bottom: 5px;">${date}</div>
                            <div style="font-size: 32px; margin-bottom: 5px;">${icon}</div>
                            <div style="font-size: 14px; color: #475569;">${Math.round(max)}°C / ${Math.round(min)}°C</div>
                        </div>
                        `;
                    }
                    wc.innerHTML = html;
                }
            }
        } else {
            const mapEl = document.getElementById("tourMap");
            if (mapEl) mapEl.innerHTML = "<p>Location not found on map.</p>";
            const wc = document.getElementById("weatherContainer");
            if (wc) wc.innerHTML = "<p>Weather unavailable.</p>";
        }
    } catch (e) {
        console.error("Map/Weather error", e);
    }
}

function changeCurrency() {
    if (!window.tourBasePrice) return;
    const select = document.getElementById("currencySelect");
    const sym = document.getElementById("currencySymbol");
    const priceEl = document.getElementById("tourPrice");
    
    // Mock exchange rates
    const rates = {
        "INR": { rate: 1, sym: "Rs." },
        "USD": { rate: 0.012, sym: "$" },
        "EUR": { rate: 0.011, sym: "€" }
    };
    
    const curr = rates[select.value];
    if (curr) {
        sym.textContent = curr.sym;
        priceEl.textContent = Math.round(window.tourBasePrice * curr.rate);
    }
}

// --- Dark Mode Logic ---
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (!darkModeToggle) return;

    // Check localStorage
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        if (document.body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem('theme', 'light');
            darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
});

// --- Advanced Filters Logic ---
async function applyFilters() {
    const minPrice = document.getElementById('minPrice')?.value;
    const maxPrice = document.getElementById('maxPrice')?.value;
    const groupSize = document.getElementById('groupSizeFilter')?.value;
    
    let queryParams = [];
    if (minPrice) queryParams.push(`minPrice=${minPrice}`);
    if (maxPrice) queryParams.push(`maxPrice=${maxPrice}`);
    if (groupSize) queryParams.push(`maxGroupSize=${groupSize}`);
    
    const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
    
    const grid = document.getElementById('toursGrid');
    if (grid) {
        grid.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
        try {
            const res = await apiRequest(`/tours${queryString}`);
            if (res.status === 'success' && res.data.length > 0) {
                renderTours(res.data, 'toursGrid');
            } else {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 50px;">No tours found matching these filters.</div>';
            }
        } catch (e) {
            console.error('Filter error', e);
            grid.innerHTML = '<div style="grid-column: 1/-1; color: red;">Failed to load filtered tours.</div>';
        }
    }
}
