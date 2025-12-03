// static/js/register-sw.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => {
        console.log('Service Worker registered! Scope:', reg.scope);
      })
      .catch(err => {
        console.log('Service Worker registration failed:', err);
      });
  });
}