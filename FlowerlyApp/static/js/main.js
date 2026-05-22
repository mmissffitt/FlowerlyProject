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

// --- Обновление счётчика корзины ---
function updateCartCount() {
    fetch('/cart/count/', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        const badge = document.querySelector('.navbar .badge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = '';
            } else {
                badge.style.display = 'none';
            }
        }
    });
}

// --- Автоматическое скрытие алертов ---
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
});

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

// --- Форматирование чисел ---
function formatPrice(price) {
    return parseFloat(price).toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }) + ' ₽';
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
            if (value.length > 11) value = value.slice(0, 11);
            
            let formatted = '+7 ';
            if (value.length > 1) formatted += '(' + value.slice(1, 4);
            if (value.length >= 4) formatted += ') ' + value.slice(4, 7);
            if (value.length >= 7) formatted += '-' + value.slice(7, 9);
            if (value.length >= 9) formatted += '-' + value.slice(9, 11);
            
            this.value = formatted;
        });
    });
});