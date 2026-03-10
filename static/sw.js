self.addEventListener("push", function(event) {
    const data = event.data.json();

    self.registration.showNotification(data.title, {
        body: data.body,
        icon: "/static/icon.png"
    });
});

self.addEventListener("notificationclick", function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow("/")
    );
});