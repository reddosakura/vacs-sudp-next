document.addEventListener('DOMContentLoaded', () => {
    const visitorList = document.getElementById('visitorList');
    const vehicleList = document.getElementById('vehicleList');
    const addVisitorBtn = document.querySelector('.visitor-section .add-btn');
    const addVehicleBtn = document.querySelector('.vehicle-section .add-btn');

    // Добавление посетителя
    addVisitorBtn.addEventListener('click', () => {
        const surname = document.querySelector('.visitor-section input[placeholder="Фамилия*"]').value;
        const name = document.querySelector('.visitor-section input[placeholder="Имя*"]').value;
        const patronymic = document.querySelector('.visitor-section input[placeholder="Отчество"]').value;

        if (surname && name) {
            const visitorItem = document.createElement('div');
            visitorItem.className = 'visitor-item';
            visitorItem.innerHTML = `
                <input type="text" value="${surname}" readonly>
                <input type="text" value="${name}" readonly>
                <input type="text" value="${patronymic}" readonly>
                <button class="remove-btn">Удалить</button>
            `;
            visitorList.appendChild(visitorItem);

            // Очистка полей
            document.querySelector('.visitor-section input[placeholder="Фамилия*"]').value = '';
            document.querySelector('.visitor-section input[placeholder="Имя*"]').value = '';
            document.querySelector('.visitor-section input[placeholder="Отчество"]').value = '';

            // Добавление функционала удаления
            const removeBtn = visitorItem.querySelector('.remove-btn');
            removeBtn.addEventListener('click', () => {
                visitorItem.remove();
            });
        }
    });

    // Добавление автомобиля
    addVehicleBtn.addEventListener('click', () => {
        const model = document.querySelector('.vehicle-section input[placeholder="Модель"]').value;
        const regNumber = document.querySelector('.vehicle-section input[placeholder="Гос. номер"]').value;

        if (model && regNumber) {
            const vehicleItem = document.createElement('div');
            vehicleItem.className = 'vehicle-item';
            vehicleItem.innerHTML = `
                <input type="text" value="${model}" readonly>
                <input type="text" value="${regNumber}" readonly>
                <button class="remove-btn">Удалить</button>
            `;
            vehicleList.appendChild(vehicleItem);

            // Очистка полей
            document.querySelector('.vehicle-section input[placeholder="Модель"]').value = '';
            document.querySelector('.vehicle-section input[placeholder="Гос. номер"]').value = '';

            // Добавление функционала удаления
            const removeBtn = vehicleItem.querySelector('.remove-btn');
            removeBtn.addEventListener('click', () => {
                vehicleItem.remove();
            });
        }
    });
});