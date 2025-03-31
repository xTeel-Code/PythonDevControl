document.addEventListener('DOMContentLoaded', function() {
    // Settings
    let settings = {
        updateInterval: 5,
        theme: 'light'
    };

    // Load settings from localStorage
    const savedSettings = localStorage.getItem('devHomeSettings');
    if (savedSettings) {
        settings = JSON.parse(savedSettings);
        document.getElementById('updateInterval').value = settings.updateInterval;
        document.getElementById('theme').value = settings.theme;
        applyTheme(settings.theme);
    }

    // Theme handling
    function applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('devHomeSettings', JSON.stringify(settings));
    }

    // System monitoring
    function updateSystemStats() {
        fetch('/api/system-stats')
            .then(response => response.json())
            .then(data => {
                // Update CPU usage
                document.getElementById('cpuUsage').style.width = `${data.cpu}%`;
                document.getElementById('cpuUsageText').textContent = `${data.cpu}%`;

                // Update Memory usage
                document.getElementById('memoryUsage').style.width = `${data.memory}%`;
                document.getElementById('memoryUsageText').textContent = `${data.memory}%`;

                // Update Disk usage
                document.getElementById('diskUsage').style.width = `${data.disk}%`;
                document.getElementById('diskUsageText').textContent = `${data.disk}%`;
            })
            .catch(error => console.error('Error fetching system stats:', error));
    }

    // Process list
    function updateProcessList() {
        fetch('/api/processes')
            .then(response => response.json())
            .then(data => {
                const processList = document.getElementById('processList');
                processList.innerHTML = '';
                
                data.processes.forEach(process => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${process.name}</td>
                        <td>${process.cpu}%</td>
                        <td>${process.memory}</td>
                        <td><span class="badge bg-${process.status === 'running' ? 'success' : 'warning'}">${process.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="terminateProcess(${process.pid})">
                                <i class="fas fa-times"></i>
                            </button>
                        </td>
                    `;
                    processList.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching processes:', error));
    }

    // Event listeners
    document.getElementById('saveSettings').addEventListener('click', function() {
        settings.updateInterval = parseInt(document.getElementById('updateInterval').value);
        settings.theme = document.getElementById('theme').value;
        applyTheme(settings.theme);
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
    });

    document.getElementById('gitStatus').addEventListener('click', function() {
        fetch('/api/git-status')
            .then(response => response.json())
            .then(data => {
                alert(`Git Status:\n${data.status}`);
            })
            .catch(error => console.error('Error fetching git status:', error));
    });

    document.getElementById('terminal').addEventListener('click', function() {
        // Open terminal in a new window
        window.open('/terminal', '_blank');
    });

    document.getElementById('logs').addEventListener('click', function() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                alert(`System Logs:\n${data.logs}`);
            })
            .catch(error => console.error('Error fetching logs:', error));
    });

    // Initial updates
    updateSystemStats();
    updateProcessList();

    // Set up periodic updates
    setInterval(updateSystemStats, settings.updateInterval * 1000);
    setInterval(updateProcessList, settings.updateInterval * 1000);
}); 