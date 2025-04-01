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

        // let html = `<div class="car-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newname}-carmodel" name="cars_list-${newname}-carmodel" class="form-control fs-5 regular-input" placeholder="МОДЕЛЬ" required><label class="text-truncate mw-100" for="cars_list-${newname}-model">МОДЕЛЬ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newname}-govern_num" name="cars_list-${newname}-govern_num" class="form-control fs-5 regular-input govern_num" placeholder="ГОС. НОМЕР" required><label class="text-truncate mw-100" for="cars_list-${newname}-govern_num">ГОС. НОМЕР<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><select id="cars_list-${newname}-visitor" name="cars_list-${newname}-visitor" class="form-select driver-select text-center fw-bold input-bg regular-input text-s h-100"><option value="-1">Выберите водителя</option></select></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="remove-car-subform rounded-4 fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`;
        let html = `<div class="car-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id="cars_list-${newname}-govern_num" name="cars_list-${newname}-govern_num" class="form-control" type="text" placeholder="ГОС. НОМЕР" style="font-weight: 600;" /><input class="form-control" id="cars_list-${newname}-carmodel" required name="cars_list-${newname}-carmodel" type="text" placeholder="МОДЕЛЬ" style="font-weight: 600;" /><button class="remove-car-subform btn btn-primary border-0" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`;
        $('#cars_list_container').append(html);
        // createSelect();

    });


    $('#cars_list_container').on('click', '.remove-car-subform', function() {
        $(this).closest('.car-subform').remove();
        // createSelect();
    });
});