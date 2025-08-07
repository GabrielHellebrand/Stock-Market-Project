let chart;

async function predictStock() {
  const ticker = document.getElementById("ticker").value.toUpperCase().trim();
  const resultEl = document.getElementById("result");
  const errorEl = document.getElementById("ticker-error");
  const canvas = document.getElementById("stockChart");

  if (!ticker) {
    errorEl.textContent = "Please enter a valid ticker.";
    resultEl.textContent = "";
    if (chart) chart.destroy();
    document.getElementById("predictionTableContainer").innerHTML = "";
    return;
  }

  if (!canvas || !canvas.getContext) {
    errorEl.textContent = "Chart initialization failed.";
    resultEl.textContent = "";
    return;
  }

  errorEl.textContent = "";
  resultEl.textContent = "Loading...";

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
    const response = await fetch(`http://localhost:8000/predict/${ticker}`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) throw new Error("Invalid ticker or server error");

    const data = await response.json();
    if (!data.today || !Array.isArray(data.all)) {
      throw new Error("Invalid response format from server");
    }

    const { today, all } = data;
    resultEl.textContent = `Current price for ${ticker}: $${today.toFixed(2)}`;

    const labels = all.map(item => item.label);
    const prices = all.map(item => item.price);

    updateChart(ticker, labels, prices);
    displayFutureTable(labels, prices); // Ensure this function exists
  } catch (error) {
    errorEl.textContent = `Error: ${error.message}`;
    resultEl.textContent = "";
    if (chart) chart.destroy();
    document.getElementById("predictionTableContainer").innerHTML = "";
  }
}

function updateChart(ticker, labels, data) {
  if (chart) chart.destroy();

  const ctx = document.getElementById("stockChart").getContext("2d");
  if (!ctx) throw new Error("Canvas context not found");

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `Projected Prices for ${ticker}`,
        data: data,
        borderColor: "#3498db",
        backgroundColor: "rgba(52, 152, 219, 0.1)",
        fill: true,
        tension: 0.3,
        pointBackgroundColor: "#3498db",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#3498db"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top'
        },
        title: {
          display: true,
          text: `Stock Price Projection for ${ticker}`
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: "Price ($)"
          }
        },
        x: {
          title: {
            display: true,
            text: "Timeframe"
          }
        }
      }
    }
  });
}