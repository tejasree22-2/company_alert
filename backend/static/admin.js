async function checkAuth() {
  try {
    const res = await fetch("/check-auth");
    if (res.status !== 200) {
      window.location.href = "/login-page";
      return null;
    }
    const data = await res.json();
    if (data.role !== "admin") {
      window.location.href = "/";
      return null;
    }
    return data;
  } catch {
    window.location.href = "/login-page";
    return null;
  }
}

(async () => {
  const user = await checkAuth();
  if (!user) return;
  console.log("Admin logged in:", user.email);
})();

document.getElementById("homeBtn").addEventListener("click", () => {
  window.location.href = "/";
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("/logout");
  window.location.href = "/login-page";
});

const companyForm = document.getElementById("companyForm");
const msg = document.getElementById("msg");

companyForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const company_name = document.getElementById("company_name").value.trim();
  const address = document.getElementById("address").value.trim();
  const city = document.getElementById("city").value.trim();
  const category = document.getElementById("category").value;
  const opening_date = document.getElementById("opening_date").value;

  const res = await fetch("/add-company", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      company_name,
      address,
      city,
      category,
      opening_date
    }),
    credentials: "include"
  });

  const data = await res.json();

  msg.innerText = data.message;
  msg.style.color = res.status === 201 ? "green" : "red";

  if (res.status === 201) {
    companyForm.reset();
  }
});
