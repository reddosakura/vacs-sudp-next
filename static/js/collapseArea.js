function collapseArea() {
    let checkBox = document.querySelector(".collapse-checkbox");
    let area = document.querySelectorAll(".collapse-area")

    if (checkBox.checked === false){
        for (let i = 0; i < area.length; i++) {
          area[i].classList.add("visually-hidden");
        }
    } else {
        for (let i = 0; i < area.length; i++) {
          area[i].classList.remove("visually-hidden");
        }
    }
}