import React from "react";
import StreamlitDashboard from "@/components/streamlit-dashboard";

const KisanmitraDashboardPage = () => {
  return (
    <StreamlitDashboard
      src="https://km-demo-v12.streamlit.app/?embed=true"
      title="KisanMitra Dashboard"
    />
  );
};

export default KisanmitraDashboardPage;
