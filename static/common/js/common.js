function redirectAfterDelay(url, delay) {
  document.getElementById('loading-spinner').style.display = 'block';

  setTimeout(function () {
    document.getElementById('loading-spinner').style.display = 'none';
    window.location.href = url;
  }, delay);
}

