const apiBase = "/api/items";

const form = document.querySelector("#itemForm");
const formTitle = document.querySelector("#formTitle");
const itemId = document.querySelector("#itemId");
const saveButton = document.querySelector("#saveButton");
const cancelButton = document.querySelector("#cancelButton");
const refreshButton = document.querySelector("#refreshButton");
const searchInput = document.querySelector("#searchInput");
const lowStockOnly = document.querySelector("#lowStockOnly");
const itemsBody = document.querySelector("#itemsBody");
const message = document.querySelector("#message");

let items = [];

function showMessage(text) {
  message.textContent = text;
  message.hidden = !text;
}

function getFormPayload() {
  return {
    sku: form.sku.value.trim(),
    name: form.name.value.trim(),
    category: form.category.value.trim(),
    quantity: Number(form.quantity.value),
    reorder_level: Number(form.reorder_level.value),
    location: form.location.value.trim(),
    notes: form.notes.value.trim() || null,
  };
}

function resetForm() {
  form.reset();
  itemId.value = "";
  formTitle.textContent = "Add Item";
  saveButton.textContent = "Save";
}

function statusBadge(item) {
  const label = item.low_stock ? "Low stock" : "OK";
  const className = item.low_stock ? "low" : "ok";
  return `<span class="status ${className}">${label}</span>`;
}

function renderItems() {
  if (!items.length) {
    itemsBody.innerHTML = `
      <tr>
        <td colspan="8">No inventory items found.</td>
      </tr>
    `;
    return;
  }

  itemsBody.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${item.sku}</td>
          <td>${item.name}</td>
          <td>${item.category}</td>
          <td>${item.quantity}</td>
          <td>${item.reorder_level}</td>
          <td>${item.location}</td>
          <td>${statusBadge(item)}</td>
          <td>
            <div class="row-actions">
              <button type="button" data-action="edit" data-id="${item.id}">Edit</button>
              <button type="button" class="secondary" data-action="delete" data-id="${item.id}">Delete</button>
            </div>
          </td>
        </tr>
      `
    )
    .join("");
}

async function loadItems() {
  const params = new URLSearchParams();
  const search = searchInput.value.trim();

  if (search) {
    params.set("search", search);
  }

  if (lowStockOnly.checked) {
    params.set("low_stock", "true");
  }

  const response = await fetch(`${apiBase}?${params.toString()}`);
  if (!response.ok) {
    showMessage("Could not load inventory items.");
    return;
  }

  items = await response.json();
  renderItems();
  showMessage("");
}

async function saveItem(event) {
  event.preventDefault();
  const payload = getFormPayload();
  const editing = Boolean(itemId.value);

  const response = await fetch(editing ? `${apiBase}/${itemId.value}` : apiBase, {
    method: editing ? "PATCH" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    showMessage(error.detail || "Could not save item.");
    return;
  }

  resetForm();
  await loadItems();
}

function startEdit(id) {
  const item = items.find((entry) => entry.id === id);
  if (!item) {
    return;
  }

  itemId.value = item.id;
  form.sku.value = item.sku;
  form.name.value = item.name;
  form.category.value = item.category;
  form.quantity.value = item.quantity;
  form.reorder_level.value = item.reorder_level;
  form.location.value = item.location;
  form.notes.value = item.notes || "";
  formTitle.textContent = "Edit Item";
  saveButton.textContent = "Update";
}

async function deleteItem(id) {
  const response = await fetch(`${apiBase}/${id}`, { method: "DELETE" });
  if (!response.ok) {
    showMessage("Could not delete item.");
    return;
  }

  await loadItems();
}

form.addEventListener("submit", saveItem);
cancelButton.addEventListener("click", resetForm);
refreshButton.addEventListener("click", loadItems);
searchInput.addEventListener("input", loadItems);
lowStockOnly.addEventListener("change", loadItems);

itemsBody.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }

  const id = Number(button.dataset.id);
  if (button.dataset.action === "edit") {
    startEdit(id);
  }

  if (button.dataset.action === "delete") {
    deleteItem(id);
  }
});

loadItems();
