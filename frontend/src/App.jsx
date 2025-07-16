import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Header from './components/Header';
import { Outlet } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <Dashboard />
      <Outlet />
      <useState />
    </div>
  );
}

export default App;