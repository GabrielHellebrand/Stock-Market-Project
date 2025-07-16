import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import StockChart from '../components/StockChart';

const StockDetail = () => {
  const { ticker } = useParams();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/stock-history/${ticker}`)
      .then(res => {
        setHistory(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [ticker]);

  return (
    <main className="p-6">
      <h2 className="text-2xl font-bold mb-4">Stock Detail: {ticker}</h2>
      {loading ? <p>Loading chart...</p> : <StockChart data={history} />}
    </main>
  );
};
const [prediction, setPrediction] = useState(null);

const handlePredict = () => {
  api.get(`/predict/${ticker}`)
    .then(res => setPrediction(res.data))
    .catch(err => console.error(err));
};

// In JSX
<button
  onClick={handlePredict}
  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
>
  Predict Tomorrow's Price
</button>

{prediction && (
  <div className="mt-4 bg-green-100 p-4 rounded shadow">
    <h4 className="font-semibold">Prediction</h4>
    <p>Last Close: ${prediction.last_close}</p>
    <p>Predicted Next Close: ${prediction.predicted_next_close}</p>
  </div>
)}
<Link
  to={`/quarterly-chart/${ticker}`}
  className="inline-block mt-4 text-blue-600 hover:underline"
>
  View 60-Day Forecast Chart
</Link>
export default StockDetail;