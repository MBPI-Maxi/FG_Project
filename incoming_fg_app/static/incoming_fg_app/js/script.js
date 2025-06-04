document.addEventListener("DOMContentLoaded", () => {
  messagePrompt();
  applyFilters();
});

function messagePrompt() {
  const messageBox = document.querySelector(".django-message");

  if (!messageBox) return;

  const message = messageBox.dataset.message;
  const redirectUrl = messageBox.dataset.redirect;

  const modal = document.getElementById("messageModal");
  const modalText = document.getElementById("messageModalText");
  const cancelBtn = document.getElementById("cancelBtn");
  const stayBtn = document.getElementById("stayBtn");
  const form = document.getElementById("endorsement-t1-form");

  // Set modal message
  modalText.innerText = message;

  // Show modal with accessibility compliance
  modal.classList.add("show");
  modal.style.display = "block";
  modal.removeAttribute("aria-hidden");
  document.body.classList.add("modal-open");

  // Optional: Focus the modal button
  setTimeout(() => {
    stayBtn.focus();
  }, 100);

  // Go to list
  cancelBtn.onclick = () => {
    window.location.href = redirectUrl;
  };

  // Add another (reset form)
  stayBtn.onclick = () => {
    document.activeElement.blur();

    // Hide modal
    modal.classList.remove("show");
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");

    if (form) {
      // Reset all input, textarea, and select values
      form.reset();
      form.querySelectorAll("input, textarea, select").forEach(input => {
        if (input.type !== "hidden") {
          input.classList.remove("is-invalid");
          input.value = "";
        }
      });

      // Remove any validation messages
      form.querySelectorAll(".invalid-feedback").forEach(el => el.remove());
    }
  };
}

function applyFilters() {
  const searchInput = document.querySelector("searchInputEndorsement");
  const tableRows = document.querySelectorAll("table tbody tr");

  searchInput.addEventListener("input", () => {
    const query = this.value.toLowerCase();

    tableRows.forEach(row => {
      const text = row.innerText.toLowerCase();
      row.style.display = text.includes(query) ? "" : "none";
    })
  });
}
