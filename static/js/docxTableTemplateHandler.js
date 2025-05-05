    document.getElementById('docxFileInput').addEventListener('change', function (event) {
  const file = event.target.files[0]
  console.log(' - Получение файла')
  if (file) {
    const reader = new FileReader()
    console.log(' - Чтение файла')
    reader.onload = function (e) {
      mammoth.convertToHtml({ arrayBuffer: e.target.result })
        .then(result => {
          console.log(' - Инициализация парсера')
          const contents = result.value
          const parser = new DOMParser()
          const docxDocument = parser.parseFromString(contents, 'text/html')
          const tables = docxDocument.querySelectorAll('table')

          const allVisitorsFieldWrapper = document.getElementById('visitors_list_container')
          console.log(' - Получение контейнера посетителей')
          const allVisitors = allVisitorsFieldWrapper.getElementsByTagName('input')

          let newName = `${allVisitors.length / 4}`

          console.log(' - Создание индексов')
          if (allVisitors.length > 0) {
            const visitorsInputIds = []
            for (let j = 0; j < allVisitors.length; j++) {
              visitorsInputIds.push(parseInt(allVisitors[j].id.split('-')[1]))
            }
            newName = Math.max(...visitorsInputIds.filter((number) => !isNaN(number))) + 1
          }

          for (let i = 0; i < tables.length; i++) {
            const tableBody = tables[i].querySelector('tbody')
            const tableHeader = tableBody.firstChild.textContent.replace(' ', '')

            if (tableHeader === 'ФамилияИмяОтчество') {
              console.log(' - Обнаружена таблица с посетителями')
              const rows = Array.from(tableBody.rows).splice(1)
              console.log(' - Выгрузка данных')
              for (let j = 0; j < rows.length; j++) {
                const cells = rows[j].cells
                const lastname = cells[0].textContent
                const name = cells[1].textContent
                const patronymic = cells[2].textContent
                const html = `<div class="visitor-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id=visitors_list-${newName}-lastname value="${lastname}" name=visitors_list-${newName}-lastname class="form-control lnp-input" type="text" placeholder="ФАМИЛИЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" required id=visitors_list-${newName}-name value="${name}" name=visitors_list-${newName}-name placeholder="ИМЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" id=visitors_list-${newName}-patronymic value="${patronymic}" name=visitors_list-${newName}-patronymic placeholder="ОТЧЕСТВО" style="font-weight: 600;" /><button class="btn btn-primary border-0 remove-visitor-subform" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`
                $('#visitors_list_container').append(html)
                newName++
              }
              console.log(' - Выгрузка завершена')
            } else if (tableHeader === 'ФамилияИмяОтчествоМаркаавтомобиляНомер автомобиля') {
              console.log(' - Обнаружена таблица с посетителями и автотранспортом')
              const rows = Array.from(tableBody.rows).splice(1)
              console.log(' - Выгрузка данных')
              for (let j = 0; j < rows.length; j++) {
                const cells = rows[j].cells
                const lastname = cells[0].textContent
                const name = cells[1].textContent
                const patronymic = cells[2].textContent

                const carModel = cells[3].textContent
                const governNum = cells[4].textContent

                const htmlV = `<div class="visitor-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id=visitors_list-${newName}-lastname value="${lastname}" name=visitors_list-${newName}-lastname class="form-control lnp-input" type="text" placeholder="ФАМИЛИЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" required id=visitors_list-${newName}-name value="${name}" name=visitors_list-${newName}-name placeholder="ИМЯ" style="font-weight: 600;" /><input class="form-control lnp-input" type="text" id=visitors_list-${newName}-patronymic value="${patronymic}" name=visitors_list-${newName}-patronymic placeholder="ОТЧЕСТВО" style="font-weight: 600;" /><button class="btn btn-primary border-0 remove-visitor-subform" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`
                $('#visitors_list_container').append(htmlV)

                const html = `<div class="car-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id="cars_list-${newName}-govern_num" value="${governNum}" name="cars_list-${newName}-govern_num" class="form-control" type="text" placeholder="ГОС. НОМЕР" style="font-weight: 600;" /><input required class="form-control" id="cars_list-${newName}-car_model" value="${carModel}" name="cars_list-${newName}-car_model" type="text" placeholder="МОДЕЛЬ" style="font-weight: 600;" /><select class="form-select driver-selector" id="cars_list-${newName}-visitor" name="cars_list-${newName}-visitor"></select><button class="remove-car-subform btn btn-primary border-0" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`
                $('#cars_list_container').append(html)
                newName++
              }
              console.log(' - Выгрузка завершена')
            } else if (tableHeader === 'МаркаавтомобиляНомер автомобиля') {
              console.log(' - Обнаружена таблица с посетителями и автотранспортом')
              const rows = Array.from(tableBody.rows).splice(1)
              console.log(' - Выгрузка данных')
              for (let j = 0; j < rows.length; j++) {
                const cells = rows[j].cells
                const carModel = cells[0].textContent
                const governNum = cells[1].textContent

                const html = `<div class="car-subform border-2 shadow d-flex p-3 gap-2 rounded-3"><input required id="cars_list-${newName}-govern_num" value="${governNum}" name="cars_list-${newName}-govern_num" class="form-control" type="text" placeholder="ГОС. НОМЕР" style="font-weight: 600;" /><input required class="form-control" id="cars_list-${newName}-car_model" value="${carModel}" name="cars_list-${newName}-car_model" type="text" placeholder="МОДЕЛЬ" style="font-weight: 600;" /><select class="form-select driver-selector" id="cars_list-${newName}-visitor" name="cars_list-${newName}-visitor"></select><button class="remove-car-subform btn btn-primary border-0" type="button" style="background: #FF9A9A;font-size: calc((1vw + 1vh) * 0.6);">УДАЛИТЬ</button></div>`
                $('#cars_list_container').append(html)
                newName++
              }
              console.log(' - Выгрузка завершена');
              setListener();
              updateOptionsList();
            }
            document.getElementById('docxFileInput').value = null
          }
        })
    }
    reader.readAsArrayBuffer(file)
  }
})

