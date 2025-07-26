function predictStock() {
  const ticker = document.getElementById("ticker").value.toUpperCase().trim();

  if (!ticker) {
    document.getElementById("result").innerText = "Please enter a valid ticker.";
    return;
  }

  // Mock prediction logic — replace with API call later
  const randomPrice = (Math.random() * 1000 + 50).toFixed(2);

  document.getElementById("result").innerText =
    `Predicted price for ${ticker}: $${randomPrice}`;
}