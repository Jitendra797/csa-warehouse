"use client";
import { Input } from "@/components/ui/input";
import { Search, Loader2 } from "lucide-react";
import { DatasetCard } from "./datasetcard";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { getUserDatasets } from "@/lib/hey-api/client/sdk.gen";

export interface DatasetCardInfo {
  dataset_id: string;
  dataset_name: string;
  description: string;
  pulled_from_pipeline: boolean;
  updated_at: string;
  user_emails: string[];
  user_names: string[];
}

export default function Manage() {
  const [datasets, setDatasets] = useState<DatasetCardInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { data: session } = useSession();

  useEffect(() => {
    const fetchDatasets = async () => {
      if (!session?.user?.apiToken) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const response = await getUserDatasets({
          headers: {
            Authorization: `Bearer ${session.user.apiToken}`,
          },
        });
        if (response.data) {
          const responseData = response.data;
          const datasetsInfo: DatasetCardInfo[] = responseData.data;
          setDatasets(datasetsInfo);
        } else {
          throw new Error("Failed to fetch datasets");
        }
      } catch (err) {
        console.error("Error fetching datasets:", err);
        setError("Failed to load datasets. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchDatasets();
  }, [session?.user?.apiToken]);

  return (
    <ContentLayout title="Manage">
      <div className="h-full flex flex-col p-6">
        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search datasets..."
            className="pl-9"
          />
        </div>
        {loading && (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.dataset_id}
              dataset_id={dataset.dataset_id}
              dataset_name={dataset.dataset_name}
              description={dataset.description || "No description"}
              user_emails={dataset.user_emails}
              user_names={dataset.user_names}
              updated_at={dataset.updated_at}
              pulled_from_pipeline={dataset.pulled_from_pipeline}
            />
          ))}
        </div>
        {datasets.length === 0 && !loading && !error && (
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">No datasets found.</div>
          </div>
        )}
      </div>
    </ContentLayout>
  );
}
