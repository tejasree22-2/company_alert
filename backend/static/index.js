document.getElementById("loginBtn").addEventListener("click", () => {
  window.location.href = "/login-page";
});

document.getElementById("footerSubscribeBtn").addEventListener("click", () => {
  window.location.href = "/login-page";
});

document.getElementById("mySubsBtn").addEventListener("click", () => {
  const email = localStorage.getItem("user_email");
  if (!email) {
    alert("Please login first to view your subscriptions.");
    window.location.href = "/login-page";
  } else {
    window.location.href = "/subscribe-page";
  }
});

document.querySelectorAll(".card").forEach(card => {
  card.addEventListener("click", () => {
    const category = card.dataset.category;
    localStorage.setItem("selected_category", category);
    window.location.href = "/login-page";
  });
});
