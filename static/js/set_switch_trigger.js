function switchCheck() {
    var switch_check = document.getElementById("switch_check");
    if (switch_check.checked === false){
        window.location = '/processing/consider'
    } else {
        window.location = '/processing/approval'
    }
}


function switchCheckArchive() {
    var switch_check = document.getElementById("switch_check");
    if (switch_check.checked === false){
        window.location = '/requests'
        switch_check.setAttribute("checked", "")
    } else {
        window.location = '/requests?show_archive=true'
    }
}