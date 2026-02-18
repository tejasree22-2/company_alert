const registerForm = document.getElementById("registerForm");
const msg = document.getElementById("msg");

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  const res = await fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();

  msg.innerText = data.message;
  msg.style.color = res.status === 201 ? "green" : "red";

  // ✅ Redirect to login after successful register
  if (res.status === 201) {
    setTimeout(() => {
      window.location.href = "/login-page";
    }, 1200);
  }
});
