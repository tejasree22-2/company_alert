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
    })
  });

  const data = await res.json();

  msg.innerText = data.message;
  msg.style.color = res.status === 201 ? "green" : "red";

  if (res.status === 201) {
    companyForm.reset();
  }
});
