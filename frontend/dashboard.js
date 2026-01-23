const API_BASE_URL = '/api/v1';
let authToken = localStorage.getItem('authToken');
let currentPeriod = 7;
let charts = {};

// Проверка токена
window.addEventListener('DOMContentLoaded', () => {
    if (!authToken) {
        window.location.href = 'index.html';
        return;
    }
    
    loadDashboardData();
});

// API запросы
async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        logout();
        throw new Error('Сессия истекла');
    }
    
    if (!response.ok) {
        throw new Error('Ошибка запроса');
    }
    
    return response.json();
}

// Загрузка данных
async function loadDashboardData() {
    try {
        await Promise.all([
            loadMetricsSummary(),
            loadTimeline(),
            loadWorkouts()
        ]);
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
}

async function loadMetricsSummary() {
    const data = await apiRequest(`/metrics/summary?days=${currentPeriod}`);
    
    document.getElementById('total-volume').textContent = 
        `${Math.round(data.total_volume)} кг`;
    document.getElementById('workouts-count').textContent = 
        data.workouts_count;
    document.getElementById('avg-volume').textContent = 
        `${Math.round(data.avg_volume)} кг`;
}

async function loadTimeline() {
    const data = await apiRequest(`/metrics/timeline?days=${currentPeriod}`);
    
    if (!data || data.length === 0) {
        console.warn('Нет данных для графиков');
        return;
    }
    
    const labels = data.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const volumes = data.map(item => item.total_volume);
    const workoutsCounts = data.map(item => item.workouts_count);
    const avgWeights = data.map(item => item.avg_weight || 0);
    const totalSets = data.map(item => item.total_sets);
    
    // Volume Chart
    updateChart('volumeChart', {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Объем (кг)',
                data: volumes,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: getChartOptions('кг')
    });
    
    // Workouts Chart
    updateChart('workoutsChart', {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Тренировок',
                data: workoutsCounts,
                backgroundColor: 'rgba(247, 147, 251, 0.2)',
                borderColor: 'rgba(247, 147, 251, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: 'rgba(247, 147, 251, 1)'
            }]
        },
        options: getChartOptions('')
    });
    
    // Weight Chart
    updateChart('avgWeightChart', {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Средний вес (кг)',
                data: avgWeights,
                backgroundColor: 'rgba(79, 172, 254, 0.2)',
                borderColor: 'rgba(79, 172, 254, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: 'rgba(79, 172, 254, 1)'
            }]
        },
        options: getChartOptions('кг')
    });
    
    // Sets Chart
    updateChart('setsChart', {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Подходов',
                data: totalSets,
                backgroundColor: 'rgba(118, 75, 162, 0.8)',
                borderColor: 'rgba(118, 75, 162, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: getChartOptions('')
    });
}

async function loadWorkouts() {
    const data = await apiRequest('/workouts?limit=10&offset=0');
    const container = document.getElementById('workouts-list');
    
    if (data.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 40px 0;">Пока нет тренировок. Добавьте первую!</p>';
        return;
    }
    
    container.innerHTML = data.map(workout => `
        <div class="workout-item">
            <div class="workout-icon">
                ${workout.exercise.muscle_group.charAt(0).toUpperCase()}
            </div>
            <div class="workout-details">
                <h4>${workout.exercise.name}</h4>
                <div class="workout-meta">
                    <span>🏋️ ${workout.sets} × ${workout.reps}</span>
                    <span>⚖️ ${workout.weight} кг</span>
                    <span>💪 ${workout.exercise.muscle_group}</span>
                </div>
            </div>
            <div class="workout-stats">
                <div class="workout-volume">${Math.round(workout.total_volume)} кг</div>
                <div class="workout-date">${new Date(workout.performed_at).toLocaleString('ru-RU')}</div>
            </div>
        </div>
    `).join('');
}

// Charts
function updateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(ctx, config);
}

function getChartOptions(unit) {
    return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                borderRadius: 8
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: 'rgba(0, 0, 0, 0.05)' }
            },
            x: {
                grid: { display: false }
            }
        }
    };
}

// Фильтры
function setTimePeriod(days) {
    currentPeriod = days;
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadMetricsSummary();
    loadTimeline();
}

// Modal
function showAddWorkoutModal() {
    document.getElementById('add-workout-modal').classList.add('active');
}

function closeAddWorkoutModal() {
    document.getElementById('add-workout-modal').classList.remove('active');
    document.getElementById('add-workout-form').reset();
}

async function handleAddWorkout(event) {
    event.preventDefault();
    
    const payload = {
        exercise_name: document.getElementById('exercise-name').value,
        muscle_group: document.getElementById('muscle-group').value,
        sets: parseInt(document.getElementById('sets').value),
        reps: parseInt(document.getElementById('reps').value),
        weight: parseFloat(document.getElementById('weight').value)
    };
    
    try {
        await apiRequest('/workouts/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        closeAddWorkoutModal();
        loadDashboardData();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
    
    return false;
}

// Logout
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = 'index.html';
}

// Close modal on outside click
window.addEventListener('click', (event) => {
    const modal = document.getElementById('add-workout-modal');
    if (event.target === modal) {
        closeAddWorkoutModal();
    }
});
