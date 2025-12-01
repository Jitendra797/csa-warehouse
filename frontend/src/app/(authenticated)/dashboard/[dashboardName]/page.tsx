"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import StreamlitDashboard from "@/components/streamlit-dashboard";
import { fetchDashboards, getDashboardUrl, type DashboardInfo } from "@/lib/dashboard-api";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import { Loader2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function DashboardViewPage() {
  const params = useParams();
  const dashboardName = params?.dashboardName as string;
  const [dashboard, setDashboard] = useState<DashboardInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { data: session } = useSession();

  useEffect(() => {
    const loadDashboard = async () => {
      if (!dashboardName) {
        setError("Dashboard name is required");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch all dashboards to find the one matching the name
        const response = await fetchDashboards(session?.user?.apiToken);
        const dashboards = response.dashboards || [];

        // Find dashboard by matching the name from the URL
        // URL might be kisanmitra but mount_path might be /dashboard/kisan_mitra
        const foundDashboard = dashboards.find((d) => {
          const mountPathName = d.mount_path.replace("/dashboard/", "").toLowerCase().replace(/_/g, "");
          const urlName = dashboardName.toLowerCase().replace(/_/g, "");
          const dashboardNameNormalized = d.name.toLowerCase().replace(/\s+|_/g, "");
          
          return (
            mountPathName === urlName ||
            dashboardNameNormalized === urlName ||
            d.mount_path.toLowerCase() === `/dashboard/${dashboardName.toLowerCase()}`
          );
        });

        if (foundDashboard) {
          setDashboard(foundDashboard);
        } else {
          setError(`Dashboard "${dashboardName}" not found`);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard:", err);
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [dashboardName, session?.user?.apiToken]);

  if (loading) {
    return (
      <ContentLayout title="Loading Dashboard...">
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </ContentLayout>
    );
  }

  if (error || !dashboard) {
    return (
      <ContentLayout title="Dashboard Error">
        <div className="container mx-auto p-6">
          <Alert variant="destructive">
            <AlertDescription>
              {error || "Dashboard not found"}
            </AlertDescription>
          </Alert>
        </div>
      </ContentLayout>
    );
  }

  const dashboardUrl = getDashboardUrl(dashboard.mount_path);

  return (
    <div className="h-screen w-full">
      <StreamlitDashboard
        src={dashboardUrl}
        title={dashboard.name}
        height="100vh"
      />
    </div>
  );
}

