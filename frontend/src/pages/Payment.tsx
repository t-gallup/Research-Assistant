import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAuth } from "firebase/auth";
import { Check } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/Card";
import { Alert, AlertDescription } from "../components/Alert";
import Navbar from "../components/Navbar";

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "For individual users and small projects",
    features: ["25 requests per day"],
    dailyLimit: 50,
  },
  {
    name: "Plus",
    price: "$9.99",
    description: "For power users",
    features: ["500 requests per day"],
    dailyLimit: 1000,
    recommended: true,
  },
  {
    name: "Pro",
    price: "$29.99",
    description: "For unlimited acess",
    features: ["Unlimited requests"],
    dailyLimit: null,
  },
];
const Payment = () => {
  const [userTier, setUserTier] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        const auth = getAuth();
        const user = auth.currentUser;

        if (!user) {
          throw new Error("No user logged in");
        }

        const idToken = await user.getIdToken();
        const usageResponse = await fetch(
          `${process.env.REACT_APP_API_URL || ""}/api/usage/stats`,
          {
            headers: {
              Authorization: `Bearer ${idToken}`,
              Accept: "application/json",
            },
          }
        );

        if (!usageResponse.ok) {
          const errorText = await usageResponse.text();
          console.error("API Error usageResponse:", errorText);
          throw new Error(
            `Failed to fetch usage data: ${usageResponse.status} ${usageResponse.statusText}`
          );
        }

        const data = await usageResponse.json();
        console.log("Received usage data:", data.tier);
        setUserTier(data.tier); // Update state with the user's tier
      } catch (err) {
        console.error("Error fetching usage data:", err);
        setError(err instanceof Error ? err.message : "An error occurred");
      }
    };

    fetchUsageData();
  }, []); // Empty dependency array to run once on mount

  const navigate = useNavigate();

  const handleUpgrade = async (planName: string) => {
    try {
      const auth = getAuth();
      const user = auth.currentUser;

      if (!user) {
        throw new Error("No user logged in");
      }
      console.log(user);

      const idToken = await user.getIdToken();

      // Call your backend API to handle the upgrade
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || ""}/api/upgrade`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ plan: planName }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to upgrade plan");
      }

      // Redirect to usage page after successful upgrade
      navigate("/usage");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-blue-900">
      <Navbar />
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-300 mb-2">
            Upgrade Your Plan
          </h1>
          <p className="text-gray-400">
            Choose the plan that best fits your needs
          </p>
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
                  ? "border-2 border-orange-500 bg-gray-800"
                  : "border border-gray-700 bg-gray-800"
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
                <CardTitle className="text-xl text-gray-200">
                  {plan.name}
                </CardTitle>
                <CardDescription className="text-gray-400">
                  {plan.description}
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-200">
                    {plan.price}
                  </span>
                  {plan.price !== "Custom" && (
                    <span className="text-gray-400">/month</span>
                  )}
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
                {plan.name.toLowerCase() === userTier
                ? <Card className={"text-white w-full py-2 px-4 rounded-lg font-medium transition-colors"}>
                  Your Plan
                  </Card>
                : <button
                    onClick={() => handleUpgrade(plan.name.toLowerCase())}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors
                      ${
                        plan.recommended
                          ? "bg-orange-500 hover:bg-orange-600 text-white"
                          : "bg-gray-700 hover:bg-gray-600 text-gray-200"
                      }`}
                  >Upgrade Now</button>}
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Payment;
