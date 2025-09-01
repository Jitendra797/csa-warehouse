"use client";

import { ContentLayout } from "@/components/admin-panel/content-layout";
import { DataTable } from "@/components/TableView/data-table";
import { useEffect, useState, useCallback } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { Loader2, AlertCircle, Badge } from "lucide-react";
import { useParams } from "next/navigation";
import { getDatasetInfoDatasetsDatasetIdGet } from "@/lib/hey-api/client/sdk.gen";
import {
  DatasetDetail,
  DatasetInfoResponse,
} from "@/lib/hey-api/client/types.gen";

export default function DatasetDetails() {
  const params = useParams();
  const dataset_id = params.dataset_id as string;
  const [username, setUsername] = useState<string>("");
  const [datasetData, setDatasetData] = useState<DatasetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasetRows = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await getDatasetInfoDatasetsDatasetIdGet({
        path: {
          dataset_id: dataset_id,
        },
      });

      if (response.data) {
        const responseData: DatasetInfoResponse = response.data;
        const datasetDetail: DatasetDetail = responseData.data;
        const usernameslength = datasetDetail.user_id.length;
        const username = datasetDetail.user_id[usernameslength - 1];
        setUsername(username);
        setDatasetData(datasetDetail);
      } else {
        throw new Error("Failed to fetch dataset rows");
      }
    } catch (err) {
      console.error("Error fetching dataset rows:", err);
      setError("Failed to load dataset. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [dataset_id]);

  useEffect(() => {
    if (dataset_id) {
      fetchDatasetRows();
    }
  }, [dataset_id, fetchDatasetRows]);

  // Generate columns dynamically based on the first row of data
  const generateColumns = (
    data: Record<string, unknown>[],
  ): ColumnDef<Record<string, unknown>>[] => {
    if (!data || data.length === 0) return [];

    const firstRow = data[0];
    return Object.keys(firstRow).map((key) => ({
      accessorKey: key,
      header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " "),
      cell: ({ row }) => {
        const value = row.getValue(key);
        if (value === null || value === undefined) {
          return <span className="text-muted-foreground">-</span>;
        }
        if (typeof value === "boolean") {
          return <Badge>{value ? "Yes" : "No"}</Badge>;
        }
        if (typeof value === "number") {
          return <span className="font-mono">{value}</span>;
        }
        return <span>{String(value)}</span>;
      },
    }));
  };

  const columns = datasetData?.rows ? generateColumns(datasetData.rows) : [];

  if (loading) {
    return (
      <ContentLayout title="Dataset Details">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </ContentLayout>
    );
  }

  if (error) {
    return (
      <ContentLayout title="Dataset Details">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      </ContentLayout>
    );
  }

  return (
    <ContentLayout title="Dataset Details">
      <div className="h-full flex flex-col p-6 space-y-6">
        {datasetData && (
          <>
            <div>
              <h2 className="text-2xl font-semibold mb-2">
                {datasetData.dataset_name}
              </h2>
              <p className="text-sm text-muted-foreground mb-1">
                {datasetData.description
                  ? datasetData.description
                  : "No description"}
              </p>
              <p className="text-sm text-foreground">
                {datasetData.pulled_from_pipeline ? (
                  <>
                    <span className="font-semibold">Pipeline Run By:</span>{" "}
                    {username}
                  </>
                ) : (
                  <>
                    <span className="font-semibold">Dataset Created By:</span>{" "}
                    {username}
                  </>
                )}
              </p>
              <p className="text-sm text-foreground">
                {datasetData.pulled_from_pipeline ? (
                  <>
                    <span className="font-semibold">Pipeline Run on:</span>{" "}
                    {new Date(datasetData.updated_at).toLocaleString()}
                  </>
                ) : (
                  <>
                    <span className="font-semibold">Last Updated on:</span>{" "}
                    {new Date(datasetData.updated_at).toLocaleString()}
                  </>
                )}
              </p>
            </div>
            <div className="flex-1">
              <div className="text-xs">
                <DataTable
                  columns={columns}
                  data={datasetData.rows ?? []}
                  isLoading={loading}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </ContentLayout>
  );
}
