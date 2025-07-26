import { Outlet } from 'react-router-dom';
import Header from './components/Header';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <Outlet />
    </div>
  );
}
export default App;