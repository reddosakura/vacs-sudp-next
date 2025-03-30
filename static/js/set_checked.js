let passage_button = document.getElementById("type-0");
let camera_button = document.getElementById("type-1");

if (window.location.toString().includes("/monitoring")){
    passage_button.checked = true;
    camera_button.checked = false;
} else {
    camera_button.checked = true;
    passage_button.checked = false;
}
