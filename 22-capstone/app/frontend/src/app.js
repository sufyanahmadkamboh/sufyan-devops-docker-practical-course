// Talks to the API through the same origin: the reverse proxy routes /api/ to the API container.
const list = document.getElementById("orders");
const health = document.getElementById("health");

async function refresh() {
  try {
    const h = await fetch("/api/health").then((r) => r.json());
    health.textContent = `${h.status}${h.version ? " (" + h.version + ")" : ""}`;
    const orders = await fetch("/api/orders").then((r) => r.json());
    list.replaceChildren(...orders.map((o) => {
      const li = document.createElement("li");
      li.textContent = `#${o.id} ${o.item}`;
      return li;
    }));
  } catch (err) {
    health.textContent = "unreachable";
  }
}

document.getElementById("order").addEventListener("submit", async (event) => {
  event.preventDefault();
  const item = document.getElementById("item");
  await fetch("/api/orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item: item.value }),
  });
  item.value = "";
  refresh();
});

refresh();
