const master = document.getElementById("master");
const service = document.getElementById("service");
const date = document.getElementById("appointment_date");
const time = document.getElementById("appointment_time");

async function loadSlots() {

    if (
        !master.value ||
        !service.value ||
        !date.value
    ) {
        return;
    }

    const response = await fetch(
        `/appointment/available-slots/?master=${master.value}&service=${service.value}&date=${date.value}`
    );

    const slots = await response.json();

    time.innerHTML = "";

    slots.forEach(slot => {

        const option = document.createElement("option");

        option.value = slot;
        option.textContent = slot;

        time.appendChild(option);

    });

}

master.addEventListener("change", loadSlots);
service.addEventListener("change", loadSlots);
date.addEventListener("change", loadSlots);

document.addEventListener('DOMContentLoaded', () => {
    const apiServicesUrl = '/api/master-services/'; 
    const masterSelect = document.getElementById('id_master');     
    const servicesSelect = document.getElementById('id_services'); 

    if (!masterSelect || !servicesSelect) return;

    const checkboxContainer = document.createElement('div');
    checkboxContainer.id = 'services-checkbox-list';
    checkboxContainer.style.marginTop = '10px';
    
    servicesSelect.style.display = 'none';
    servicesSelect.parentNode.insertBefore(checkboxContainer, servicesSelect.nextSibling);

    function updateServices(masterId) {
        if (!masterId) {
            checkboxContainer.innerHTML = '<p style="color: #666; font-size: 0.9em;">Сначала выберите мастера</p>';
            return;
        }

        checkboxContainer.innerHTML = '<em>Загрузка доступных услуг...</em>';

        fetch(`${apiServicesUrl}?master=${masterId}`)
            .then(response => {
                if (!response.ok) throw new Error();
                return response.json();
            })
            .then(services => {
                checkboxContainer.innerHTML = ''; 

                if (services.length === 0) {
                    checkboxContainer.innerHTML = '<p style="color: #dd4b39; font-size: 0.9em;">У этого мастера нет доступных услуг</p>';
                    return;
                }

                services.forEach(service => {
                    const label = document.createElement('label');
                    label.style.display = 'block';
                    label.style.marginBottom = '8px';
                    label.style.cursor = 'pointer';

                    label.innerHTML = `
                        <input type="checkbox" value="${service.id}" style="margin-right: 8px; cursor: pointer;">
                        <span>${service.name}</span>
                    `;

                    const checkbox = label.querySelector('input');

                    checkbox.addEventListener('change', () => {
                        const option = servicesSelect.querySelector(`option[value="${service.id}"]`);
                        if (option) {
                            option.selected = checkbox.checked;
                            servicesSelect.dispatchEvent(new Event('change'));
                        }
                    });

                    checkboxContainer.appendChild(label);
                });
            })
            .catch(() => {
                checkboxContainer.innerHTML = '<span style="color: #dd4b39;">Не удалось загрузить список услуг.</span>';
            });
    }

    masterSelect.addEventListener('change', (e) => {
        updateServices(e.target.value);
    });

    updateServices(masterSelect.value);
});