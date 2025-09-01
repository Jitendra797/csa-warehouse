"use client";

import { ContentLayout } from "@/components/admin-panel/content-layout";
import { DataTable } from "@/components/TableView/data-table";
import {
  DatasetDetail,
  DatasetInfoResponse,
} from "@/lib/hey-api/client/types.gen";
import { useEffect, useState, useCallback } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { Loader2, AlertCircle, Badge } from "lucide-react";
import { useParams } from "next/navigation";
import { getDatasetInfoDatasetsDatasetIdGet } from "@/lib/hey-api/client/sdk.gen";

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
            <div className="space-y-6">
              {/* Dataset Name */}
              <div>
                <h2 className="text-2xl font-bold">
                  {datasetData.dataset_name}
                </h2>
              </div>

              {/* Description - Max 2 lines */}
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">Description</h3>
                <p className="text-base leading-relaxed line-clamp-2">
                  {datasetData.description}
                </p>
              </div>

              {/* Dataset Type, Created By, and Update Time in a row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Dataset Type */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Dataset Type</h3>
                  <p className="text-base">{datasetData.dataset_type}</p>
                </div>

                {/* User Information */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">
                    {datasetData.pulled_from_pipeline
                      ? "Pipeline Run By"
                      : "Dataset Uploaded By"}
                  </h3>
                  <div className="space-y-1">
                    <p className="text-base text-muted-foreground">
                      {username}
                    </p>
                  </div>
                </div>

                {/* Last Updated Information */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">
                    {datasetData.pulled_from_pipeline
                      ? "Pipeline Last Run"
                      : "Dataset Updated At"}
                  </h3>
                  <p className="text-base">
                    {new Date(datasetData.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Tags */}
              <div className="space-y-2">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-lg font-semibold">Tags:</span>
                  {datasetData.tags && datasetData.tags.length > 0 ? (
                    datasetData.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors bg-secondary text-secondary-foreground hover:bg-secondary/80"
                      >
                        {tag}
                      </span>
                    ))
                  ) : (
                    <span className="text-base text-muted-foreground">-</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex-1">
              <DataTable
                columns={columns}
                data={datasetData.rows ?? []}
                isLoading={loading}
              />
            </div>
          </>
        )}
      </div>
    </ContentLayout>
  );
}
