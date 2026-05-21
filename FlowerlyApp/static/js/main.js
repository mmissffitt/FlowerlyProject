/* ============================================
   FLOWERLY — ОБЩИЙ JAVASCRIPT
   ============================================ */

// --- CSRF-токен для AJAX-запросов ---
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

// --- Автоматическое скрытие алертов ---
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
});

// --- Подтверждение удаления ---
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить этот элемент?');
}

// --- Scroll to top button ---
document.addEventListener('DOMContentLoaded', function() {
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-top-btn';
    scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    });

    scrollBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

// --- Автоматическая отправка формы при изменении select ---
document.addEventListener('DOMContentLoaded', function() {
    const autoSubmitSelects = document.querySelectorAll('select[onchange="this.form.submit()"]');
    autoSubmitSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });
});

// --- Избранное (toggle favorite) ---
function toggleFavorite(bouquetId) {
    fetch(`/favorite/toggle/${bouquetId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const allFavBtns = document.querySelectorAll(`[onclick="toggleFavorite(${bouquetId})"]`);
            allFavBtns.forEach(btn => {
                const icon = btn.querySelector('i');
                if (icon) {
                    if (data.is_favorite) {
                        icon.className = 'bi bi-heart-fill';
                    } else {
                        icon.className = 'bi bi-heart';
                    }
                }
            });
        }
    });
}

// --- Форматирование чисел ---
function formatPrice(price) {
    return parseFloat(price).toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }) + ' ₽';
}

// --- Дебаунс для поиска ---
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// --- Плавная прокрутка к элементу ---
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// --- Обработка ошибок fetch ---
function handleFetchError(error) {
    console.error('Ошибка запроса:', error);
    alert('Произошла ошибка. Пожалуйста, попробуйте позже.');
}

// --- Инициализация всех tooltips Bootstrap ---
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// --- Инициализация всех popovers Bootstrap ---
document.addEventListener('DOMContentLoaded', function() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// --- Валидация форм на клиенте ---
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// --- Предпросмотр загружаемого изображения ---
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// --- Таймер обратного отсчёта (для акций) ---
function startCountdown(elementId, endDate) {
    const element = document.getElementById(elementId);
    if (!element) return;

    function updateTimer() {
        const now = new Date().getTime();
        const distance = new Date(endDate).getTime() - now;

        if (distance < 0) {
            element.innerHTML = 'Акция завершена';
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        element.innerHTML = `${days}д ${hours}ч ${minutes}м ${seconds}с`;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

// --- Копирование текста в буфер обмена ---
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Скопировано в буфер обмена!');
    }).catch(function() {
        alert('Не удалось скопировать');
    });
}

// --- Маска для телефона ---
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 0 && value[0] !== '7' && value[0] !== '8') {
                value = '7' + value;
            }
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
            
            let formatted = '+7 ';
            if (value.length > 1) formatted += '(' + value.slice(1, 4);
            if (value.length >= 4) formatted += ') ' + value.slice(4, 7);
            if (value.length >= 7) formatted += '-' + value.slice(7, 9);
            if (value.length >= 9) formatted += '-' + value.slice(9, 11);
            
            this.value = formatted;
        });
    });
});

// --- Добавление товара в корзину (заглушка) ---
function addToCart(bouquetId) {
    alert('Функция добавления в корзину через API будет реализована позже. Пока используйте кнопку на странице букета.');
}