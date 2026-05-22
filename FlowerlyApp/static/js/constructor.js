/* ============================================
   FLOWERLY — КОНСТРУКТОР БУКЕТОВ (AJAX, без перезагрузок)
   ============================================ */

// --- CSRF и куки ---
function getCSRF() { return getCookie('csrftoken'); }
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Форматирование цены ---
function formatPrice(price) {
    return parseFloat(price).toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

// --- Модальное окно ЦВЕТКА ---
function openFlowerModal(id, name, price, imageUrl) {
    document.getElementById('currentFlowerId').value = id;
    document.getElementById('currentQuantity').value = 1;
    document.getElementById('quantityDisplay').textContent = '1';
    document.getElementById('flowerModalName').textContent = name;
    document.getElementById('flowerModalPrice').textContent = formatPrice(price) + ' ₽/шт';
    document.getElementById('flowerModalImage').src = imageUrl;

    const modal = new bootstrap.Modal(document.getElementById('flowerModal'));
    modal.show();
}

function changeQuantity(delta) {
    const display = document.getElementById('quantityDisplay');
    const input = document.getElementById('currentQuantity');
    let qty = parseInt(input.value) + delta;
    if (qty < 1) qty = 1;
    if (qty > 99) qty = 99;
    input.value = qty;
    display.textContent = qty;
}

function addFlowerToBouquet() {
    const flowerId = document.getElementById('currentFlowerId').value;
    const quantity = parseInt(document.getElementById('currentQuantity').value);

    fetch('/constructor/add-flower/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify({ flower_id: flowerId, quantity: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('flowerModal')).hide();
            updateBouquetPreview(data);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// --- Модальное окно ДЕКОРА ---
function openDecorModal(id, name, price, imageUrl) {
    document.getElementById('currentDecorId').value = id;
    document.getElementById('currentDecorQuantity').value = 1;
    document.getElementById('decorQuantityDisplay').textContent = '1';
    document.getElementById('decorModalName').textContent = name;
    document.getElementById('decorModalPrice').textContent = formatPrice(price) + ' ₽/шт';
    document.getElementById('decorModalImage').src = imageUrl;

    const modal = new bootstrap.Modal(document.getElementById('decorModal'));
    modal.show();
}

function changeDecorQuantity(delta) {
    const display = document.getElementById('decorQuantityDisplay');
    const input = document.getElementById('currentDecorQuantity');
    let qty = parseInt(input.value) + delta;
    if (qty < 1) qty = 1;
    if (qty > 99) qty = 99;
    input.value = qty;
    display.textContent = qty;
}

function addDecorToBouquet() {
    const decorId = document.getElementById('currentDecorId').value;
    const quantity = parseInt(document.getElementById('currentDecorQuantity').value);

    fetch('/constructor/add-decor/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify({ decor_id: decorId, quantity: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('decorModal')).hide();
            updateBouquetPreview(data);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// --- Удаление позиций ---
function removeFlower(flowerId) {
    fetch('/constructor/remove-flower/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify({ flower_id: flowerId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBouquetPreview(data);
        }
    });
}

function removeDecor(decorId) {
    fetch('/constructor/remove-decor/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify({ decor_id: decorId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBouquetPreview(data);
        }
    });
}

// --- Обновление правой панели ---
function updateBouquetPreview(data) {
    const preview = document.getElementById('bouquet-preview');
    if (!preview) return;

    let html = '';

    // Цветы
    if (data.flowers && Object.keys(data.flowers).length > 0) {
        html += '<h6 class="fw-bold">Цветы:</h6><ul class="list-group list-group-flush mb-3" id="flower-list">';
        for (const [fid, item] of Object.entries(data.flowers)) {
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center px-0" data-id="${fid}">
                    <div>
                        <span>${item.name}</span>
                        <span class="badge bg-light text-dark ms-1">×${item.quantity}</span>
                    </div>
                    <div>
                        <span class="text-muted me-2">${item.price} ₽</span>
                        <button class="btn btn-sm text-danger" onclick="removeFlower('${fid}')">
                            <i class="bi bi-x-circle"></i>
                        </button>
                    </div>
                </li>`;
        }
        html += '</ul>';
    }

    // Декор
    if (data.decors && Object.keys(data.decors).length > 0) {
        html += '<h6 class="fw-bold">Декор:</h6><ul class="list-group list-group-flush mb-3" id="decor-list">';
        for (const [did, item] of Object.entries(data.decors)) {
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center px-0" data-id="${did}">
                    <div>
                        <span>${item.name}</span>
                        <span class="badge bg-light text-dark ms-1">×${item.quantity}</span>
                    </div>
                    <div>
                        <span class="text-muted me-2">${item.price} ₽</span>
                        <button class="btn btn-sm text-danger" onclick="removeDecor('${did}')">
                            <i class="bi bi-x-circle"></i>
                        </button>
                    </div>
                </li>`;
        }
        html += '</ul>';
    }

    if (!html) {
        html = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-flower1 display-4"></i>
                <p class="mt-2">Добавьте цветы и декор, чтобы собрать букет</p>
            </div>`;
    }

    html += '<hr>';
    html += `<div class="d-flex justify-content-between align-items-center mb-3">
        <span class="fw-bold fs-5">Итого:</span>
        <span class="fw-bold fs-4 text-danger">${formatPrice(data.total)} ₽</span>
    </div>`;
    html += preview.querySelector('form') ? preview.querySelector('form').outerHTML : '';

    preview.innerHTML = html;
}