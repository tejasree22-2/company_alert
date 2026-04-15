document.getElementById("loginBtn").addEventListener("click", () => {
  window.location.href = "/login-page";
});

document.getElementById("footerSubscribeBtn").addEventListener("click", () => {
  window.location.href = "/login-page";
});

document.getElementById("mySubsBtn").addEventListener("click", async () => {
  try {
    const res = await fetch("/check-auth");
    if (res.status !== 200) {
      window.location.href = "/login-page";
      return;
    }
    window.location.href = "/subscribe-page";
  } catch {
    window.location.href = "/login-page";
  }
});

document.querySelectorAll(".card").forEach(card => {
  card.addEventListener("click", () => {
    const category = card.dataset.category;
    localStorage.setItem("selected_category", category);
    window.location.href = "/login-page";
  });
});
