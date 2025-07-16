import { useParams } from 'react-router-dom';

const QuarterlyChart = () => {
  const { ticker } = useParams();

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Quarterly Prediction: {ticker}</h2>
      <img
        src={`http://localhost:8000/quarterly-predict-plot/${ticker}`}
        alt={`Quarterly forecast for ${ticker}`}
        className="w-full border rounded shadow"
      />
    </div>
  );
};

export default QuarterlyChart;