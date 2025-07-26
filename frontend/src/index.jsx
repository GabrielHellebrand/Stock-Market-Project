import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Dashboard from './pages/Dashboard';
import StockDetail from './pages/StockDetail';
import QuarterlyChart from './pages/QuarterlyChart';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Dashboard />} />
          <Route path="/stocks/:ticker" element={<StockDetail />} />
          <Route path="/quarterly-chart/:ticker" element={<QuarterlyChart />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
