function redirectAfterDelay(url, delay) {
  document.getElementById('loading-spinner').style.display = 'block';

  setTimeout(function () {
    document.getElementById('loading-spinner').style.display = 'none';
    window.location.href = url;
  }, delay);
}

function copyToClipboard(button) {
  var container = button.closest(".individual-account-container");
  var copyText = container.querySelector(".copyToClipboard");
  var accountNumber = copyText.dataset.accountNumber;

  var tempInput = document.createElement("input");
  tempInput.value = accountNumber;
  document.body.appendChild(tempInput);
  tempInput.select();
  tempInput.setSelectionRange(0, 99999);
  document.execCommand("copy");
  document.body.removeChild(tempInput);
}
