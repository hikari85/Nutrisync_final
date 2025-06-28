function renderHealthCharts(healthLogs) {
    const dates = healthLogs.map(entry => entry.date);
    const weights = healthLogs.map(entry => entry.weight);
    const waterIntake = healthLogs.map(entry => entry.water_intake);
    const sleepHours = healthLogs.map(entry => entry.sleep_hours);

    const createChart = (ctxId, label, data, color) => {
        const ctx = document.getElementById(ctxId).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: color,
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Date' } },
                    y: { title: { display: true, text: label } }
                }
            }
        });
    };

    createChart('weightChart', 'Weight (kg)', weights, 'blue');
    createChart('waterChart', 'Water Intake (L)', waterIntake, 'teal');
    createChart('sleepChart', 'Sleep Hours', sleepHours, 'purple');
}
