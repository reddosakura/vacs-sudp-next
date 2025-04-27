const $search = document.getElementById('search');
const $search_on_territory = document.getElementById('search-field-onterritory');

$search.addEventListener('input', (event) => {

    const searchText = event.target.value;

    const cards = document.querySelectorAll(".card-monitoring");

    var instance = new Mark(document.querySelector("#monitoringMain"));

    var modalinstance = new Mark(document.querySelector(".modal-body"))

    instance.unmark();
    instance.mark(searchText, {
      "each": function(element) {
        setTimeout(function() {
          $(element).addClass("animate");
        }, 200);
      },
      "exclude": [
          "p",
          ".decor"
      ],
      "separateWordSearch": false
    });

    modalinstance.unmark();
    modalinstance.mark(searchText, {
      "each": function(element) {
        setTimeout(function() {
          $(element).addClass("animate");
        }, 200);
      },
      "exclude": [
          "input",
      ],
      "separateWordSearch": false
    });

    document.cookie = `search_value=${searchText}; SameSite=Lax;`;

    for (let i = 0; i < cards.length; i++) {
        const cells_lnp = Array.from(cards[i].querySelectorAll(".cell-lnp")).map(elem => elem.textContent).join("\n");
        const cells_cars = Array.from(cards[i].querySelectorAll(".cell-cars")).map(elem => elem.textContent).join("\n");
        const cell_contract = cards[i].querySelector(".cell-contract");
        const cell_organisation = cards[i].querySelector(".cell-organisation");

        console.log(cells_cars)

        if (!cells_lnp.includes(searchText.toUpperCase())
            && !cells_cars.toUpperCase().includes(searchText.toUpperCase())
            && !cell_contract.textContent.toUpperCase().includes(searchText.toUpperCase())
            && !cell_organisation.textContent.toUpperCase().includes(searchText.toUpperCase())
          ){
            cards[i].classList.add("visually-hidden")
        } else {
            cards[i].classList.remove("visually-hidden")
        }
    }
});

$search_on_territory.addEventListener('input', (event) => {
    const searchText = event.target.value;

    const cards = document.querySelectorAll(".card-on-terrtory");

    var instance = new Mark(document.querySelector("#on-territory-list"));


    instance.unmark();
    instance.mark(searchText, {
      "each": function(element) {
        setTimeout(function() {
          $(element).addClass("animate");
        }, 200);
      },
      "exclude": [
          "input"
      ],
      "separateWordSearch": false
    });


    for (let i = 0; i < cards.length; i++) {
        const cells_cars = Array.from(cards[i].querySelectorAll(".card-content-car")).map(elem => elem.textContent).join("\n");

        console.log(cells_cars)

        if (!cells_cars.toUpperCase().includes(searchText.toUpperCase())){
            cards[i].classList.add("visually-hidden")
        } else {
            cards[i].classList.remove("visually-hidden")
        }
    }
});