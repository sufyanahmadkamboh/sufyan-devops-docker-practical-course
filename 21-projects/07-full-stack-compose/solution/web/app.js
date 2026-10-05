// Same origin: Nginx forwards /api/ to the API container.
async function load() {
  const notes = await fetch("/api/notes").then((r) => r.json());
  document.getElementById("notes").replaceChildren(...notes.map((n) => {
    const li = document.createElement("li");
    li.textContent = n.text;
    return li;
  }));
}
document.getElementById("add").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("text");
  await fetch("/api/notes", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: input.value }) });
  input.value = "";
  load();
});
load();
