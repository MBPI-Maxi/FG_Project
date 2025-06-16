document.addEventListener("DOMContentLoaded", () => {
  alertMessageDuration();
  showBox();
  lotNumberToggleEvent();
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

        } 
        
        else if (/^\d{4}[A-Z]{2}$/.test(value)) {
          const element = document.createElement("span");
          
          emptyLotNumberCtn.classList.remove("text-danger");
          
          element.textContent = "Single lot detected. Lot difference: 1";
          
          emptyLotNumberCtn.appendChild(element);
        }
        
        else {
          emptyLotNumberCtn.classList.add("text-danger");
          emptyLotNumberCtn.textContent = "Invalid lot number format. Should be either '8888AA-9999AA' or '8888AA'";
        }
      }
    } catch (error) {
      return;
    }
  });
}

function lotNumberToggleEvent() {
  const lotToggle = document.getElementById("lot-toggle");
  const lotInput = document.getElementById("id_t_lotnumberwhole");
  
  lotToggle.addEventListener("change", () => {    
    
    if (lotToggle.checked) {
      lotInput.placeholder = "8888AA"
      lotInput.title = "Format: 8888AA"
    } else {
      lotInput.placeholder = "8888AA-9999AA"
      lotInput.title = "Format: 8888AA-9999AA"
    }

  })
}