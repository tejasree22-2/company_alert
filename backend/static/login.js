const loginForm = document.getElementById("loginForm");
const msg = document.getElementById("msg");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  msg.innerText = "";
  msg.style.color = "red";

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    msg.innerText = data.message;
    msg.style.color = res.status === 200 ? "green" : "red";

    // ✅ login success
    if (res.status === 200) {
      localStorage.setItem("user_email", email);
      setTimeout(() => window.location.href = "/subscribe-page", 800);
      return;
    }

    // ✅ user not found -> register page
    if (res.status === 404) {
      setTimeout(() => window.location.href = "/register-page", 900);
      return;
    }

  } catch (err) {
    msg.innerText = "❌ Something went wrong. Please try again.";
    msg.style.color = "red";
    console.error(err);
  }
});

