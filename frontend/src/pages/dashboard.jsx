import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [stocks, setStocks] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/stocks").then((res) => {
      setStocks(res.data);
    });
  }, []);

  const filteredStocks = stocks.filter(
    (stock) =>
      stock.name.toLowerCase().includes(search.toLowerCase()) ||
      stock.ticker.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Stock Predictions</h1>
      <input
        type="text"
        placeholder="Search by name or ticker..."
        className="p-2 mb-4 w-full border border-gray-300 rounded"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {filteredStocks.map((stock) => (
          <Link key={stock.ticker} to={`/stock/${stock.ticker}`}>
            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-4">
                <h2 className="text-lg font-semibold">{stock.name}</h2>
                <p className="text-sm text-gray-500">{stock.ticker}</p>
                <p className="mt-2">Price: ${stock.price.toFixed(2)}</p>
                <p className="text-sm text-gray-600">
                  P/E Ratio: {stock.pe_ratio.toFixed(2)}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

