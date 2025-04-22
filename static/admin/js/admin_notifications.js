(function($) {
    let lastUpdate = new Date();
    
    function updateNotifications() {
        $.get('/ajax/admin-notifications/', function(data) {
            const count = data.count;
            const notifications = data.notifications;
            
            // Update badge count
            $('.notification-badge').text(count || '');
            
            // Update dropdown content
            const container = $('.notification-dropdown-content');
            container.empty();
            
            if (notifications.length === 0) {
                container.append('<div class="no-notifications">No pending notifications</div>');
                return;
            }
            
            // Group notifications by type
            const grouped = {};
            notifications.forEach(notif => {
                if (!grouped[notif.type]) grouped[notif.type] = [];
                grouped[notif.type].push(notif);
            });
            
            // Render grouped notifications
            Object.entries(grouped).forEach(([type, items]) => {
                container.append(`<div class="notification-group-header">${type}</div>`);
                items.forEach(notif => {
                    container.append(`
                        <a href="${notif.url}" class="notification-item">
                            <div class="notification-message">${notif.message}</div>
                            <div class="notification-time">${notif.time}</div>
                        </a>
                    `);
                });
            });
        });
    }

    // Initialize notifications
    $(document).ready(function() {
        // Add notification icon to header
        const headerRight = $('.navbar-nav.ml-auto');
        headerRight.prepend(`
            <li class="nav-item dropdown">
                <a class="nav-link" data-toggle="dropdown" href="#" role="button">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge badge badge-danger navbar-badge"></span>
                </a>
                <div class="dropdown-menu dropdown-menu-right notification-dropdown-content">
                </div>
            </li>
        `);

        // Initial update
        updateNotifications();
        
        // Poll for updates every 30 seconds
        setInterval(updateNotifications, 30000);
    });
})(jQuery);
