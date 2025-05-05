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
        let html = `<div class="visitor-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id=visitors_list-${newname}-lastname name=visitors_list-${newname}-lastname class="form-control lnp-input" type="text" placeholder="ФАМИЛИЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" required id=visitors_list-${newname}-name name=visitors_list-${newname}-name placeholder="ИМЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" id=visitors_list-${newname}-patronymic name=visitors_list-${newname}-patronymic placeholder="ОТЧЕСТВО" style="font-weight: 600;" /><button class="btn btn-primary border-0 remove-visitor-subform" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`;
        $('#visitors_list_container').append(html);

        setListener();
    });

    $('#visitors_list_container').on('click', '.remove-visitor-subform', function() {
        $(this).closest('.visitor-subform').remove();
        // createSelect();
        updateOptionsList();
    });
});