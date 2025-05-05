function createDriverList() {
    let visitorsSubForms = document.querySelectorAll(".visitor-subform")
    let driversList = document.createElement("select")
    driversList.add(new Option("ВЫБЕРИТЕ ВОДИТЕЛЯ", ""));
    for(let i = 0; i < visitorsSubForms.length; i++) {
        let inputs = visitorsSubForms[i].querySelectorAll("input")
        if (inputs[0].value || inputs[1].value || inputs[2].value){
            driversList.add(new Option(`${inputs[0].value} ${inputs[1].value} ${inputs[2].value}`, `${i}`))
        }
    }
    return driversList.options;
}

function getContents(selector) {
    let contents = []
    Array.from(selector.options).forEach(function (option) {
        contents.push(option.text);
    })
    return contents
}

function updateOptionsList() {
    let driverSelectors = document.querySelectorAll(".driver-selector")
    for (let i = 0; i < driverSelectors.length; i++) {
        let selected = driverSelectors[i].options[driverSelectors[i].selectedIndex]
        console.log(driverSelectors[i].options[selected])

        driverSelectors[i].options.length = 0;
        Array.from(createDriverList()).forEach(function (option) {
            driverSelectors[i].add(option);
        })

        Array.from(driverSelectors[i].options).forEach(function (option) {
            if(selected) {
                if ((option.text === selected.text)) {
                    driverSelectors[i].value = option.value
                }

                if (!getContents(driverSelectors[i]).includes(selected.text)) {
                    driverSelectors[i].value = ""
                }
            } else {
                driverSelectors[i].value = ""
            }
        })
    }
}

function setListener() {
    Array.from(document.getElementsByClassName("lnp-input")).forEach(function(element) {
      element.addEventListener('input', updateOptionsList);
    });
}
