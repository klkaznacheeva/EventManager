// firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyCSSN_vZI2u7tMyUcDxNCxZA7TtiDOWErQ",
    authDomain: "eventmanager-b7f5c.firebaseapp.com",
    projectId: "eventmanager-b7f5c",
    storageBucket: "eventmanager-b7f5c.firebasestorage.app",
    messagingSenderId: "126978082457",
    appId: "1:126978082457:web:899c11bbdb9f2b6a3b1a08"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log('Фоновый пуш:', payload);
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: '/icon.png'
    });
});