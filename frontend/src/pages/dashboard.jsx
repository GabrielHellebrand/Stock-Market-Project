import { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

// Inside .map
<Link to={`/stocks/${stock.ticker}`}>
  <div key={stock.ticker} className="bg-white p-4 rounded shadow hover:bg-gray-50 transition">
    <h3 className="font-bold">{stock.name} ({stock.ticker})</h3>
    <p>Price: ${stock.price.toFixed(2)}</p>
    <p>PE Ratio: {stock.pe_ratio}</p>
  </div>
</Link>

const Dashboard = () => {
  const [stocks, setStocks] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/stocks')
      .then(res => {
        setStocks(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch stock data:', err);
        setLoading(false);
      });
  }, []);

  const filteredStocks = stocks.filter(stock =>
    stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.ticker.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="p-6">
      <h2 className="text-xl font-semibold mb-4">Stock Overview</h2>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by ticker or company name..."
          className="w-full sm:w-1/2 px-4 py-2 border border-gray-300 rounded shadow-sm"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {loading ? (
        <p>Loading stock data...</p>
      ) : filteredStocks.length === 0 ? (
        <p>No matching stocks found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {filteredStocks.map(stock => (
            <div key={stock.ticker} className="bg-white p-4 rounded shadow">
              <h3 className="font-bold">{stock.name} ({stock.ticker})</h3>
              <p>Price: ${stock.price.toFixed(2)}</p>
              <p>PE Ratio: {stock.pe_ratio}</p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
};
useEffect(() => {
  api.get('/predict-sp500?limit=10')
    .then(res => setPredictions(res.data))
    .catch(err => console.error(err));
}, []);

export default Dashboard;
