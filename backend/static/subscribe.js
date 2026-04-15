async function checkAuth() {
  try {
    const res = await fetch("/check-auth");
    if (res.status !== 200) {
      window.location.href = "/login-page";
      return null;
    }
    return await res.json();
  } catch {
    window.location.href = "/login-page";
    return null;
  }
}

let userData = null;

(async () => {
  userData = await checkAuth();
  if (!userData) return;
})();

document.getElementById("homeBtn").addEventListener("click", () => {
  window.location.href = "/";
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("/logout");
  window.location.href = "/login-page";
});

const subscribeBtn = document.getElementById("subscribeBtn");
const subMsg = document.getElementById("subMsg");
const listDiv = document.getElementById("subscriptionsList");

async function loadSubscriptions() {
  const res = await fetch("/get-subscriptions", {
    method: "GET",
    credentials: "include"
  });

  if (res.status === 401) {
    window.location.href = "/login-page";
    return;
  }

  const data = await res.json();

  listDiv.innerHTML = "";

  if (!data.subscriptions || data.subscriptions.length === 0) {
    listDiv.innerHTML = "<p style='color:#666'>No subscriptions yet.</p>";
    return;
  }

  data.subscriptions.forEach(sub => {
    const div = document.createElement("div");
    div.className = "sub-item";

    div.innerHTML = `
      <h3>📍 ${sub.city} → 🏷 ${sub.category} 
        ${sub.is_paused ? "<span style='color:red'>(Paused)</span>" : "<span style='color:green'>(Active)</span>"}
      </h3>

      <div class="sub-actions">
        ${
          sub.is_paused
            ? `<button class="btn-unpause" onclick="pauseSub(${sub.id}, false)">Unpause</button>`
            : `<button class="btn-pause" onclick="pauseSub(${sub.id}, true)">Pause</button>`
        }
        <button class="btn-edit" onclick="editSub(${sub.id}, '${sub.city}', '${sub.category}')">Edit</button>
        <button class="btn-delete" onclick="deleteSub(${sub.id})">Unsubscribe</button>
      </div>
    `;

    listDiv.appendChild(div);
  });
}

subscribeBtn.addEventListener("click", async () => {
  const city = document.getElementById("city").value.trim();
  const category = document.getElementById("category").value;

  if (!city) {
    subMsg.innerText = "City is required!";
    subMsg.style.color = "red";
    return;
  }

  const res = await fetch("/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ city, category }),
    credentials: "include"
  });

  const data = await res.json();
  subMsg.innerText = data.message;
  subMsg.style.color = res.status === 201 ? "green" : "red";

  if (res.status === 201) {
    document.getElementById("city").value = "";
    loadSubscriptions();
  }
});

async function pauseSub(subscription_id, pause) {
  const res = await fetch("/pause-subscription", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subscription_id, pause }),
    credentials: "include"
  });

  await res.json();
  loadSubscriptions();
}

async function deleteSub(subscription_id) {
  if (!confirm("Are you sure you want to unsubscribe?")) return;

  const res = await fetch("/unsubscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subscription_id }),
    credentials: "include"
  });

  await res.json();
  loadSubscriptions();
}

async function editSub(subscription_id, oldCity, oldCategory) {
  const newCity = prompt("Enter new city:", oldCity);
  if (!newCity) return;

  const newCategory = prompt("Enter new category:", oldCategory);
  if (!newCategory) return;

  const res = await fetch("/edit-subscription", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subscription_id,
      city: newCity,
      category: newCategory
    }),
    credentials: "include"
  });

  await res.json();
  loadSubscriptions();
}

window.pauseSub = pauseSub;
window.deleteSub = deleteSub;
window.editSub = editSub;

loadSubscriptions();
