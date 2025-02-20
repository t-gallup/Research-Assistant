import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getAuth } from 'firebase/auth';

const UsagePage = () => {
  const [usageData, setUsageData] = useState([]);
  const [quotaInfo, setQuotaInfo] = useState({
    total_limit: 0,
    used_requests: 0,
    remaining_requests: 0,
    tier: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        const auth = getAuth();
        const user = auth.currentUser;
        
        if (!user) {
          throw new Error('No user logged in');
        }

        const idToken = await user.getIdToken();
        const response = await fetch('/api/usage/stats', {
          headers: {
            'Authorization': `Bearer ${idToken}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch usage data');
        }

        const data = await response.json();
        setUsageData(data.daily_usage);
        setQuotaInfo({
          total_limit: data.total_limit,
          used_requests: data.used_requests,
          remaining_requests: data.remaining_requests,
          tier: data.tier
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsageData();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-gray-300">Loading usage data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-300">API Usage Dashboard</h1>
        <div className="text-orange-500">
          Current Tier: {quotaInfo.tier}
        </div>
      </div>
      
      <div className="grid gap-6 grid-cols-1 md:grid-cols-3 mb-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Total Limit</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.total_limit.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Used Requests</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.used_requests.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-gray-400 text-lg mb-2">Remaining Requests</h2>
          <p className="text-3xl font-bold text-gray-200">{quotaInfo.remaining_requests.toLocaleString()}</p>
          <p className="text-sm text-gray-400 mt-2">Resets daily</p>
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