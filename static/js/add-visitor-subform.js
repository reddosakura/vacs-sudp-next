$(document).ready(function() {
    $('.add-visitor-subform').click(function() {
        const message = document.getElementById("visitor-message");
        if (message){
            message.remove();
        }
        let allVisitorsFieldWrapper = document.getElementById('visitors_list_container');
        let allVisitors = allVisitorsFieldWrapper.getElementsByTagName('input');
        let visitorsInputIds = []
        for(let i = 0; i < allVisitors.length; i++) {
            visitorsInputIds.push(parseInt(allVisitors[i].name.split('-')[1]));
        }

        let newname = `${allVisitors.length / 4}`;
        if (allVisitors.length > 0){
            let visitorsInputIds = []
            for (let j = 0; j < allVisitors.length; j++) {
                visitorsInputIds.push(parseInt(allVisitors[j].id.split('-')[1]))
            }
            newname = Math.max(...visitorsInputIds.filter((number) => !isNaN(number))) + 1;
        }
        // let html = `<div class="visitor-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 p-0 rounded-4 d-flex"><div class="w-100 p-1"><div class="form-floating "><input oninput="createSelect()" id=visitors_list-${newname}-lastname name=visitors_list-${newname}-lastname class="form-control fs-5 regular-input lastname" placeholder="Фамилия" required><label class="text-truncate mw-100" for="lastname">ФАМИЛИЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input oninput="createSelect()" id=visitors_list-${newname}-name name=visitors_list-${newname}-name class="form-control fs-5 regular-input name" placeholder="Имя" required><label class="text-truncate mw-100" for="name">ИМЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input oninput="createSelect()" id=visitors_list-${newname}-patronymic name=visitors_list-${newname}-patronymic class="form-control fs-5 regular-input patronymic" placeholder="Отчество" ><label class="text-truncate mw-100" for="patronymic">ОТЧЕСТВО</label></div></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="rounded-4 remove-visitor-subform fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`;
        let html = `<div class="visitor-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id=visitors_list-${newname}-lastname name=visitors_list-${newname}-lastname class="form-control" type="text" placeholder="ФАМИЛИЯ" style="font-weight: 600;" /><input class="form-control" type="text" required id=visitors_list-${newname}-name name=visitors_list-${newname}-name placeholder="ИМЯ" style="font-weight: 600;" /><input class="form-control" type="text" id=visitors_list-${newname}-patronymic name=visitors_list-${newname}-patronymic placeholder="ОТЧЕСТВО" style="font-weight: 600;" /><button class="btn btn-primary border-0 remove-visitor-subform" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`;
        $('#visitors_list_container').append(html);
    });

    $('#visitors_list_container').on('click', '.remove-visitor-subform', function() {
        $(this).closest('.visitor-subform').remove();
        // createSelect();
    });
});