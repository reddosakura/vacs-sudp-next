import { $ } from '../jquery/jquery.js'
import { mammoth } from '../lib/mammoth/mammoth.browser.min.js'

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
                const html = `<div class="visitor-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 p-0 rounded-4 d-flex"><div class="w-100 p-1"><div class="form-floating "><input id=visitors_list-${newName}-lastname name=visitors_list-${newName}-lastname class="form-control fs-5 regular-input" placeholder="Фамилия" value=${lastname} required><label class="text-truncate mw-100" for="lastname">ФАМИЛИЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id=visitors_list-${newName}-name name=visitors_list-${newName}-name class="form-control fs-5 regular-input" placeholder="Имя" value=${name} required><label class="text-truncate mw-100" for="name">ИМЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id=visitors_list-${newName}-patronymic name=visitors_list-${newName}-patronymic class="form-control fs-5 regular-input" placeholder="Отчество" value=${patronymic} ><label class="text-truncate mw-100" for="patronymic">ОТЧЕСТВО</label></div></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="rounded-4 remove-visitor-subform fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`
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

                const htmlV = `<div class="visitor-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 p-0 rounded-4 d-flex"><div class="w-100 p-1"><div class="form-floating "><input id=visitors_list-${newName}-lastname name=visitors_list-${newName}-lastname class="form-control fs-5 regular-input" placeholder="Фамилия" value=${lastname} required><label class="text-truncate mw-100" for="lastname">ФАМИЛИЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id=visitors_list-${newName}-name name=visitors_list-${newName}-name class="form-control fs-5 regular-input" placeholder="Имя" value=${name} required><label class="text-truncate mw-100" for="name">ИМЯ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id=visitors_list-${newName}-patronymic name=visitors_list-${newName}-patronymic class="form-control fs-5 regular-input" placeholder="Отчество" value=${patronymic} ><label class="text-truncate mw-100" for="patronymic">ОТЧЕСТВО</label></div></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="rounded-4 remove-visitor-subform fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`
                $('#visitors_list_container').append(htmlV)
                const html = `<div class="car-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newName}-carmodel" value="${carModel}" name="cars_list-${newName}-carmodel" class="form-control fs-5 regular-input" placeholder="МОДЕЛЬ" required><label class="text-truncate mw-100" for="cars_list-${newName}-model">МОДЕЛЬ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newName}-govern_num" value="${governNum}" name="cars_list-${newName}-govern_num" class="form-control fs-5 regular-input govern_num" placeholder="ГОС. НОМЕР" required><label class="text-truncate mw-100" for="cars_list-${newName}-govern_num">ГОС. НОМЕР<span class="text-danger">*</span></label></div></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="remove-car-subform rounded-4 fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`
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

                const html = `<div class="car-subform container text-label rounded-4 mb-2 m-0"><div class="row p-1"><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newName}-carmodel" value="${carModel}" name="cars_list-${newName}-carmodel" class="form-control fs-5 regular-input" placeholder="МОДЕЛЬ" required><label class="text-truncate mw-100" for="cars_list-${newName}-model">МОДЕЛЬ<span class="text-danger">*</span></label></div></div></div><div class="col w-25 rounded-4 d-flex p-0"><div class="w-100 p-1"><div class="form-floating"><input id="cars_list-${newName}-govern_num" value="${governNum}" name="cars_list-${newName}-govern_num" class="form-control fs-5 regular-input govern_num" placeholder="ГОС. НОМЕР" required><label class="text-truncate mw-100" for="cars_list-${newName}-govern_num">ГОС. НОМЕР<span class="text-danger">*</span></label></div></div></div><div class="col w-25 p-1"><div class="h-100 internal-btn"><input class="remove-car-subform rounded-4 fs-6 w-100 h-100 regular-btn" type="button" value="УДАЛИТЬ"></div></div></div></div>`
                $('#cars_list_container').append(html)
                newName++
              }
              console.log(' - Выгрузка завершена')
            }

            document.getElementById('docxFileInput').value = null
          }
        })
    }
    reader.readAsArrayBuffer(file)
  }
})
