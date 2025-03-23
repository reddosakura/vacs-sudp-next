function switchCheck() {
    var switch_check = document.getElementById("switch_check");
    if (switch_check.checked === false){
        window.location = '/processing/consider'
    } else {
        window.location = '/processing/approval'
    }
}