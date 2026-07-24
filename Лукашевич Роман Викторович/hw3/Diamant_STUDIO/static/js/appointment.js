console.log("appointment.js загружен");

// Находим элементы формы по точным ID, которые вы указали в widgets формы Django
const master = document.getElementById("id_master") || document.getElementById("master");
const service = document.getElementById("id_service") || document.getElementById("service");
const date = document.getElementById("id_appointment_date") || document.getElementById("id_date") || document.getElementById("appointment_date");
const time = document.getElementById("id_appointment_time") || document.getElementById("id_time") || document.getElementById("appointment_time");

console.log("Найденные элементы формы:", { master, service, date, time });

// Читаем параметры из URL-строки браузера (?service_id=... или ?master_id=...)
const urlParams = new URLSearchParams(window.location.search);
const urlServiceId = urlParams.get('service_id') || urlParams.get('service');
const urlMasterId = urlParams.get('master_id') || urlParams.get('master');

// =========================
// Динамическая фильтрация услуг
// =========================
async function loadServices() {
    if (!service) return;
    
    console.log("loadServices вызвана. Текущий мастер ID:", master ? master.value : "нет");

    // Приоритет выбора услуги: текущее значение в поле или значение из URL
    const targetServiceId = service.value || urlServiceId;

    service.innerHTML = "";

    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "---------";
    service.appendChild(emptyOption);

    // Строим URL запроса услуг
    let fetchUrl = '/appointment/master-services/';
    const currentMasterId = (master ? master.value : "") || urlMasterId;
    if (currentMasterId) {
        fetchUrl += `?master=${currentMasterId}`;
    }

    try {
        const response = await fetch(fetchUrl);
        const services = await response.json();
        console.log("Загруженные услуги с бэкенда:", services);

        services.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = item.name;

            // Если ID совпадает с целевым, делаем элемент выбранным
            if (item.id == targetServiceId) {
                option.selected = true;
                console.log(`Услуга ID ${item.id} успешно выбрана!`);
            }

            service.appendChild(option);
        });
    } catch (error) {
        console.error("Ошибка при загрузке услуг:", error);
    }

    // После обновления списка услуг всегда обновляем доступное время
    loadSlots();
}

// =========================
// Загрузка свободного времени
// =========================
async function loadSlots() {
    if (!time || !master || !service || !date) return;

    time.innerHTML = "";

    if (!master.value || !service.value || !date.value) {
        console.log("Пропуск loadSlots: заполнены не все поля");
        return;
    }

    try {
        const response = await fetch(`/appointment/available-slots/?master=${master.value}&service=${service.value}&date=${date.value}`);
        const slots = await response.json();
        console.log("Загруженные слоты времени:", slots);

        slots.forEach(slot => {
            const option = document.createElement("option");
            option.value = slot;
            option.textContent = slot;
            time.appendChild(option);
        });
    } catch (error) {
        console.error("Ошибка при загрузке слотов времени:", error);
    }
}

// =========================
// Навешивание событий
// =========================
if (master) master.addEventListener("change", loadServices);
if (service) service.addEventListener("change", loadSlots);
if (date) date.addEventListener("change", loadSlots);

// =========================
// Инициализация при старте страницы
// =========================
function initializeForm() {
    console.log("Инициализация формы...");
    
    // Подставляем мастера из URL, если он пришел с главной страницы и поле еще пустое
    if (master && urlMasterId && !master.value) {
        master.value = urlMasterId;
    }

    // Запускаем первичную загрузку услуг, чтобы отработал выбор из URL параметров
    loadServices();
}

// Запуск после построения DOM
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeForm);
} else {
    initializeForm();
}