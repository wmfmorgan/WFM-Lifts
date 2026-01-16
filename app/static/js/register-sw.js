// static/js/register-sw.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => {

      })
      .catch(err => {

      });
  });
}