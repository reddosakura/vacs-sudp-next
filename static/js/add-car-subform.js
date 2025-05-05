$(document).ready(function() {
    $('.add-car-subform').click(function() {
        const message = document.getElementById("car-message");
        if (message){
            message.remove();
        }
        let allCarsFieldWrapper = document.getElementById('cars_list_container');
        let allCars = allCarsFieldWrapper.getElementsByTagName('input');
        let carsInputIds = []
        for(let i = 0; i < allCars.length; i++) {
            carsInputIds.push(parseInt(allCars[i].name.split('-')[1]));
        }
        let newname = `${allCars.length / 3}`;
        if (allCars.length > 0){
            let visitorsInputIds = []
            for (let j = 0; j < allCars.length; j++) {
                visitorsInputIds.push(parseInt(allCars[j].id.split('-')[1]))
            }
            newname = Math.max(...visitorsInputIds.filter((number) => !isNaN(number))) + 1;
        }

        let html = `<div class="car-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id="cars_list-${newname}-govern_num" name="cars_list-${newname}-govern_num" class="form-control" type="text" placeholder="ГОС. НОМЕР" style="font-weight: 600;" /><input class="form-control" id="cars_list-${newname}-car_model" required name="cars_list-${newname}-car_model" type="text" placeholder="МОДЕЛЬ" style="font-weight: 600;" /><select class="form-select driver-selector" id="cars_list-${newname}-visitor" name="cars_list-${newname}-visitor"></select><button class="remove-car-subform btn btn-primary border-0" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`;
        $('#cars_list_container').append(html);
        // createSelect();
        updateOptionsList();

    });


    $('#cars_list_container').on('click', '.remove-car-subform', function() {
        $(this).closest('.car-subform').remove();
        // createSelect();
        updateOptionsList()
    });
});