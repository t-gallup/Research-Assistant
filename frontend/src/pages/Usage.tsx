import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const UsagePage = () => {
  // In a real implementation, this would come from your backend
  const [usageData, setUsageData] = useState([
    { date: '2024-02-14', requests: 150 },
    { date: '2024-02-15', requests: 230 },
    { date: '2024-02-16', requests: 180 },
    { date: '2024-02-17', requests: 290 },
    { date: '2024-02-18', requests: 320 },
    { date: '2024-02-19', requests: 270 },
    { date: '2024-02-20', requests: 200 },
  ]);

  const [quotaInfo, setQuotaInfo] = useState({
    totalRequests: 10000,
    usedRequests: 1640,
    remainingRequests: 8360,
  });

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6 text-gray-300">API Usage Dashboard</h1>
      
      <div className="grid gap-6 grid-cols-1 md:grid-cols-3 mb-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Total Requests</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.totalRequests.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Used Requests</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.usedRequests.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Remaining Requests</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.remainingRequests.toLocaleString()}</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-gray-400 text-lg mb-4">Daily Usage</h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => new Date(date).toLocaleDateString()}
                stroke="#9CA3AF"
              />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
                formatter={(value) => [value, 'Requests']}
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: '#E5E7EB'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="requests" 
                stroke="#F97316"
                strokeWidth={2}
                dot={{ fill: '#F97316' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default UsagePage;