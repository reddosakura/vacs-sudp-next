let sidebar = document.getElementById("sidebar");

sidebar.addEventListener("mouseover", (event) => {
    let allText = document.querySelectorAll(".text");
    for (let i = 0; i < allText.length; i++) {
        allText[i].classList.remove("visually-hidden");
    }

})

sidebar.addEventListener("mouseleave", (event) => {
    let allText = document.querySelectorAll(".text");
    for (let i = 0; i < allText.length; i++) {
        allText[i].classList.add("visually-hidden");
    }
    
})
