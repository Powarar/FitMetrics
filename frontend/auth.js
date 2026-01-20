const API_BASE_URL = 'http://localhost:8000/api/v1';

// ЛОГИН
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('login-error');
    
    errorEl.textContent = '';
    errorEl.style.display = 'none';
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Неверный логин или пароль');
        }
        
        const data = await response.json();
        localStorage.setItem('authToken', data.access_token);
        
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.style.display = 'block';
    }
    
    return false;
}

// РЕГИСТРАЦИЯ
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const errorEl = document.getElementById('register-error');
    
    errorEl.textContent = '';
    errorEl.style.display = 'none';
    
    if (password !== confirmPassword) {
        errorEl.textContent = 'Пароли не совпадают';
        errorEl.style.display = 'block';
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка регистрации');
        }
        
        // Автологин после регистрации
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const loginData = await loginResponse.json();
        localStorage.setItem('authToken', loginData.access_token);
        
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.style.display = 'block';
    }
    
    return false;
}

window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    const path = window.location.pathname;
    

    if (token && (path.includes('index.html') || path.includes('register.html') || path === '/' || path === '/frontend/')) {
        window.location.href = 'dashboard.html';
    }
});
