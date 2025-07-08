import { useEffect, useState } from 'react';
import { getSp500Predictions, getChartImageUrl } from '../api/financeApi';

export default function Dashboard() {
  const [stocks, setStocks] = useState<any[]>([]);

  useEffect(() => {
    getSp500Predictions(20).then((res) => {
      setStocks(res.data.predictions);
    });
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">S&P 500 Predictions</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {stocks.map((stock) => (
          <div key={stock.symbol} className="border rounded p-3 shadow">
            <h2 className="text-lg font-semibold">{stock.symbol}</h2>
            <p>Last Close: ${stock.last_close.toFixed(2)}</p>
            <p className="text-green-600">Predicted: ${stock.predicted_close_in_60_days.toFixed(2)}</p>
            <img
              src={getChartImageUrl(stock.symbol)}
              alt={`${stock.symbol} chart`}
              className="w-full mt-2"
            />
          </div>
        ))}
      </div>
    </div>
  );
}