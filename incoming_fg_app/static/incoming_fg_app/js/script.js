document.addEventListener("DOMContentLoaded", () => {
  alertMessageDuration();
});

function alertMessageDuration() {
  const alertSuccessPrompt = document.querySelector(".alert-success-prompt");

  if (alertSuccessPrompt) {
    setTimeout(() => {
      alertSuccessPrompt.classList.add("d-none");
    }, 60000); // 1 minute
  }
}

