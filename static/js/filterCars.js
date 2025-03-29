function filterCars() {
    let selector = document.querySelector(".car-filter").value
    let filteredArea = document.querySelectorAll(".car-filter-area")

    console.log(selector);
    for (let i = 0; i < filteredArea.length; i++) {
        if (selector === '1') {
            if (filteredArea[i].querySelector(".status").textContent === 'ВЫЕЗД'){
                filteredArea[i].classList.add("visually-hidden");
            } else {
                filteredArea[i].classList.remove("visually-hidden");
            }
        } else if(selector === '2') {
            if (filteredArea[i].querySelector(".status").textContent === 'ВЪЕЗД'){
                filteredArea[i].classList.add("visually-hidden");
            } else {
                filteredArea[i].classList.remove("visually-hidden");
            }
        } else {
            filteredArea[i].classList.remove("visually-hidden");
        }
    }
}

function filterSpecCars() {

    let selector_status = document.querySelector(".spec-filter-status").value;
    let selector_type = document.querySelector(".spec-filter-type").value;
    let filteredArea = document.querySelectorAll(".spec-filter-area");

    for (let i = 0; i < filteredArea.length; i++) {
        filteredArea[i].classList.remove("visually-hidden");

        if ((selector_type !== '0')) {
            if ((filteredArea[i].querySelector(".type").textContent !== selector_type)){
                console.log("TYPE FILTER");
                filteredArea[i].classList.add("visually-hidden");
            }
        }

        if ((selector_status !== '0')) {
            console.log("STATUS FILTER");
            if ((filteredArea[i].querySelector(".status").textContent !== selector_status)){
                console.log("STATUS FILTERED");
                filteredArea[i].classList.add("visually-hidden");
            }
        }

        if ((selector_type === '0') && (selector_status === '0')) {
            filteredArea[i].classList.remove("visually-hidden");
        }
    }
}