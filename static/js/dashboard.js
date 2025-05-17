/**
 * Dashboard initialization and refresh functionality
 */
function initDashboard(refreshInterval) {
    // Set up the clock
    updateClock();
    setInterval(updateClock, 1000);

    // Set up the refresh countdown
    startCountdown(refreshInterval);

    // Set up manual refresh button
    document.getElementById('refresh-btn').addEventListener('click', function() {
        refreshData();
    });

    // Set up automatic refresh
    setInterval(refreshData, refreshInterval * 1000);

    // Calculate in-process orders on initial load
    calculateOrdersStatus();
}

/**
 * Update the current time display
 */
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeString;
}

/**
 * Start the countdown timer for next refresh
 */
function startCountdown(refreshInterval) {
    let timeLeft = refreshInterval;
    const countdownElement = document.getElementById('refresh-countdown');
    
    function updateCountdown() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        countdownElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            timeLeft = refreshInterval;
        } else {
            timeLeft--;
        }
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

/**
 * Refresh the dashboard data from the server
 */
function refreshData() {
    const alertElement = document.getElementById('connection-alert');
    const alertMessageElement = document.getElementById('connection-message');
    
    // Show loading state
    document.getElementById('refresh-btn').innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Actualizando...';
    document.getElementById('refresh-btn').disabled = true;
    
    fetch('/api/orders')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide any error messages
                alertElement.classList.add('d-none');
                
                // Update last updated time
                document.getElementById('last-updated').textContent = data.last_updated;
                
                // Update orders table
                updateOrdersTable(data.orders);
                
                // Update summary counters
                document.getElementById('total-orders').textContent = data.orders.length;
                calculateOrdersStatus();
                
                console.log('Dashboard data refreshed successfully');
            } else {
                throw new Error(data.error || 'Error desconocido al actualizar datos');
            }
        })
        .catch(error => {
            console.error('Error refreshing data:', error);
            alertElement.classList.remove('d-none');
            alertMessageElement.textContent = `Error al actualizar datos: ${error.message}`;
        })
        .finally(() => {
            // Reset loading state
            document.getElementById('refresh-btn').innerHTML = '<i class="fas fa-sync-alt me-1"></i> Actualizar Ahora';
            document.getElementById('refresh-btn').disabled = false;
        });
}

/**
 * Update the orders table with new data
 */
function updateOrdersTable(orders) {
    const tableBody = document.querySelector('#orders-table tbody');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (orders.length === 0) {
        // No orders, show empty state
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="6" class="text-center py-4">
                <div class="py-5">
                    <i class="fas fa-clipboard-check fa-3x mb-3 text-muted"></i>
                    <p class="mb-0">No hay pedidos pendientes</p>
                </div>
            </td>
        `;
        tableBody.appendChild(emptyRow);
    } else {
        // Create a row for each order
        orders.forEach(order => {
            const row = document.createElement('tr');
            
            // Format the date (if it's a Date object)
            let formattedDate;
            if (typeof order.fecha === 'object' && order.fecha !== null) {
                // It's a date object
                formattedDate = `${order.fecha.getDate().toString().padStart(2, '0')}/${(order.fecha.getMonth() + 1).toString().padStart(2, '0')}`;
            } else if (typeof order.fecha === 'string' && order.fecha.includes('-')) {
                // It's a date string
                const dateParts = new Date(order.fecha);
                formattedDate = `${dateParts.getDate().toString().padStart(2, '0')}/${(dateParts.getMonth() + 1).toString().padStart(2, '0')}`;
            } else {
                // Use as is
                formattedDate = order.fecha;
            }
            
            // Determine status indicator
            let statusHTML;
            if (order.estatus === 'Pendiente') {
                statusHTML = '<span class="status-indicator yellow">●</span> ' + order.estatus;
            } else if (order.estatus === 'En proceso') {
                statusHTML = '<span class="status-indicator orange">●</span> ' + order.estatus;
            } else if (order.estatus === 'Terminado') {
                statusHTML = '<span class="status-indicator green">✓</span> ' + order.estatus;
            } else {
                statusHTML = '<span class="status-indicator">●</span> ' + order.estatus;
            }
            
            row.innerHTML = `
                <td><strong>${order.pedido}</strong></td>
                <td>${order.cliente}</td>
                <td>${formattedDate}</td>
                <td>${order.hora}</td>
                <td>${order.vendedora}</td>
                <td>${statusHTML}</td>
            `;
            
            tableBody.appendChild(row);
        });
    }
}

/**
 * Calculate and update the number of orders by status
 */
function calculateOrdersStatus() {
    const tableRows = document.querySelectorAll('#orders-table tbody tr');
    let inProcessCount = 0;
    
    tableRows.forEach(row => {
        // Check if this is not the empty state row
        if (!row.querySelector('td[colspan="6"]')) {
            // Get the status cell (last column)
            const statusCell = row.querySelector('td:last-child');
            const statusText = statusCell.textContent.trim();
            
            // Count orders with "En proceso" status
            if (statusText.includes('En proceso')) {
                inProcessCount++;
            }
        }
    });
    
    // Update the in-process orders counter
    document.getElementById('process-orders').textContent = inProcessCount;
}
