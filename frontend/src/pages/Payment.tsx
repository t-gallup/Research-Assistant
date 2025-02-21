import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuth } from 'firebase/auth';
import { Check } from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '../components/Alert';
import Navbar from '../components/Navbar';

const plans = [
  {
    name: 'Standard',
    price: '$0',
    description: 'For individual users and small projects',
    features: [
      '1,000 requests per day',
      'Basic API access',
      'Standard support',
      'Core features'
    ],
    dailyLimit: 1000,
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'For power users and teams',
    features: [
      '5,000 requests per day',
      'Advanced API access',
      'Priority support',
      'All features included',
      'Team collaboration'
    ],
    dailyLimit: 5000,
    recommended: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For large organizations',
    features: [
      'Unlimited requests',
      'Custom API solutions',
      'Dedicated support',
      'Custom features',
      'SLA guarantee',
      'Account manager'
    ],
    dailyLimit: null,
  }
];

const PaymentPage = () => {
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);

  const handleUpgrade = async (planName: string) => {
    try {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('No user logged in');
      }

      const idToken = await user.getIdToken();
      
      // Call your backend API to handle the upgrade
      const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/upgrade`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plan: planName })
      });

      if (!response.ok) {
        throw new Error('Failed to upgrade plan');
      }

      // Redirect to usage page after successful upgrade
      navigate('/usage');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-blue-900">
      <Navbar />
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-300 mb-2">Upgrade Your Plan</h1>
          <p className="text-gray-400">Choose the plan that best fits your needs</p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6 grid-cols-1 md:grid-cols-3">
          {plans.map((plan) => (
            <Card 
              key={plan.name}
              className={`relative ${
                plan.recommended 
                  ? 'border-2 border-orange-500 bg-gray-800' 
                  : 'border border-gray-700 bg-gray-800'
              }`}
            >
              {plan.recommended && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm">
                    Recommended
                  </span>
                </div>
              )}
              
              <CardHeader>
                <CardTitle className="text-xl text-gray-200">{plan.name}</CardTitle>
                <CardDescription className="text-gray-400">{plan.description}</CardDescription>
              </CardHeader>
              
              <CardContent>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-200">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className="text-gray-400">/month</span>}
                </div>
                
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-gray-300">
                      <Check className="h-5 w-5 text-green-500 mr-2" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
              
              <CardFooter>
                <button
                  onClick={() => handleUpgrade(plan.name.toLowerCase())}
                  className={`w-full py-2 px-4 rounded-lg font-medium transition-colors
                    ${plan.recommended
                      ? 'bg-orange-500 hover:bg-orange-600 text-white'
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                    }`}
                >
                  {plan.price === 'Custom' ? 'Contact Sales' : 'Upgrade Now'}
                </button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;