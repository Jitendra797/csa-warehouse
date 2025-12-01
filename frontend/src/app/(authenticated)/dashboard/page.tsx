"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import { fetchDashboards, type DashboardInfo } from "@/lib/dashboard-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, ExternalLink, Activity } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<DashboardInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { data: session } = useSession();
  const router = useRouter();

  useEffect(() => {
    const loadDashboards = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchDashboards(session?.user?.apiToken);
        setDashboards(response.dashboards || []);
      } catch (err) {
        console.error("Failed to fetch dashboards:", err);
        setError(err instanceof Error ? err.message : "Failed to load dashboards");
      } finally {
        setLoading(false);
      }
    };

    loadDashboards();
  }, [session?.user?.apiToken]);

  const handleDashboardClick = (dashboard: DashboardInfo) => {
    // Extract dashboard name from mount_path (e.g., /dashboard/kisan_mitra -> kisan_mitra)
    // Use the mount_path directly to ensure we match what the backend expects
    const dashboardName = dashboard.mount_path.replace("/dashboard/", "");
    if (dashboardName) {
      router.push(`/dashboard/${dashboardName}`);
    }
  };

  if (loading) {
    return (
      <ContentLayout title="Dashboards">
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </ContentLayout>
    );
  }

  if (error) {
    return (
      <ContentLayout title="Dashboards">
        <div className="container mx-auto p-6">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </ContentLayout>
    );
  }

  return (
    <ContentLayout title="Dashboards">
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-2">Available Dashboards</h2>
          <p className="text-muted-foreground">
            {dashboards.length === 0
              ? "No dashboards available"
              : `${dashboards.length} dashboard${dashboards.length !== 1 ? "s" : ""} available`}
          </p>
        </div>

        {dashboards.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">
                No dashboards are currently available. Check back later or contact your administrator.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboards.map((dashboard) => (
              <Card
                key={dashboard.mount_path}
                className="cursor-pointer hover:shadow-lg transition-shadow flex flex-col"
                onClick={() => handleDashboardClick(dashboard)}
              >
                <CardHeader className="flex-shrink-0">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-lg truncate flex-1">
                      {dashboard.name}
                    </CardTitle>
                    <Badge
                      variant="outline"
                      className="capitalize flex-shrink-0"
                    >
                      <Activity className="h-3 w-3 mr-1" />
                      {dashboard.status}
                    </Badge>
                  </div>
                  <CardDescription className="mt-1">
                    Port: {dashboard.port}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col justify-between gap-3">
                  <span className="text-sm text-muted-foreground truncate">
                    {dashboard.mount_path}
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDashboardClick(dashboard);
                    }}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </ContentLayout>
  );
}
