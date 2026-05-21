/* ============================================
   FLOWERLY — КОНСТРУКТОР БУКЕТОВ
   ============================================ */

// --- Вспомогательная функция CSRF ---
function getCSRF() {
    return getCookie('csrftoken');
}

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

// --- Модальное окно ЦВЕТКА ---
function openFlowerModal(id, name, price, imageUrl) {
    document.getElementById('currentFlowerId').value = id;
    document.getElementById('currentQuantity').value = 1;
    document.getElementById('quantityDisplay').textContent = '1';
    document.getElementById('flowerModalName').textContent = name;
    document.getElementById('flowerModalPrice').textContent = parseFloat(price).toLocaleString('ru-RU') + ' ₽/шт';
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
            location.reload();
        } else {
            alert('Ошибка при добавлении цветка');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка. Попробуйте позже.');
    });
}

// --- Модальное окно ДЕКОРА ---
function openDecorModal(id, name, price, imageUrl) {
    document.getElementById('currentDecorId').value = id;
    document.getElementById('currentDecorQuantity').value = 1;
    document.getElementById('decorQuantityDisplay').textContent = '1';
    document.getElementById('decorModalName').textContent = name;
    document.getElementById('decorModalPrice').textContent = parseFloat(price).toLocaleString('ru-RU') + ' ₽/шт';
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
            location.reload();
        } else {
            alert('Ошибка при добавлении декора');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка. Попробуйте позже.');
    });
}

// --- Удаление позиций из конструктора ---
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
            location.reload();
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
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
            location.reload();
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

// --- Клавиатурные сокращения ---
document.addEventListener('keydown', function(e) {
    // Escape — закрыть модальное окно
    if (e.key === 'Escape') {
        const flowerModal = bootstrap.Modal.getInstance(document.getElementById('flowerModal'));
        const decorModal = bootstrap.Modal.getInstance(document.getElementById('decorModal'));
        if (flowerModal) flowerModal.hide();
        if (decorModal) decorModal.hide();
    }
    
    // Enter — добавить в модальном окне
    if (e.key === 'Enter') {
        const flowerModal = bootstrap.Modal.getInstance(document.getElementById('flowerModal'));
        const decorModal = bootstrap.Modal.getInstance(document.getElementById('decorModal'));
        
        if (document.getElementById('flowerModal').classList.contains('show')) {
            e.preventDefault();
            addFlowerToBouquet();
        }
        if (document.getElementById('decorModal').classList.contains('show')) {
            e.preventDefault();
            addDecorToBouquet();
        }
    }
});