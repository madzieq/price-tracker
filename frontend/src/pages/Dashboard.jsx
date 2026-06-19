import { useQuery } from "@tanstack/react-query";
import { productsApi } from "../api/client";

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.list(),
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <h1>Price Tracker</h1>
      <p>Products: {data?.total ?? 0}</p>
    </div>
  );
}

export default Dashboard;