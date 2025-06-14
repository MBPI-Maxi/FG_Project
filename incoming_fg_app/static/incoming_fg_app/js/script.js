document.addEventListener("DOMContentLoaded", () => {
  alertMessageDuration();
  showBox();
});

function alertMessageDuration() {
  const alertSuccessPrompt = document.querySelector(".alert-success-prompt");

  if (alertSuccessPrompt) {
    setTimeout(() => {
      alertSuccessPrompt.classList.add("d-none");
    }, 60000); // 1 minute
  }
}

function showBox() {
  const lotNumberElement = document.querySelector("input[name='t_lotnumberwhole']");
  const emptyLotNumberCtn = document.getElementById("lot-number-whole-calculation");

  lotNumberElement.addEventListener("blur", () => {
    emptyLotNumberCtn.textContent = "";

    let value = lotNumberElement.value.trim();

    try {
      if (value !== "") {
        const splitData = value.split("-");

        if (splitData.length === 2 && splitData[0] && splitData[1]) {
          const leftNum = splitData[0].slice(0, 4);
          const rightNum = splitData[1].slice(0, 4);

          emptyLotNumberCtn.classList.remove("text-danger");

          const lotDifference = Number(rightNum) - Number(leftNum) + 1;
          const element = document.createElement("span");
          element.textContent = `Lot difference: ${lotDifference}`;
          
          emptyLotNumberCtn.appendChild(element);

          if (isNaN(lotDifference)) {
            emptyLotNumberCtn.classList.add("text-danger");
          }

        } else {
          emptyLotNumberCtn.classList.add("text-danger");
          emptyLotNumberCtn.textContent = "Invalid lot number format (e.g., 1234-1235).";
        }
      }
    } catch (error) {
      return;
    }
  });
}
