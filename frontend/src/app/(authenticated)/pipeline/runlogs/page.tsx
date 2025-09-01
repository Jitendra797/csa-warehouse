"use client";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import { getPipelinesPipelinesGet } from "@/lib/hey-api/client/sdk.gen";
import { useEffect, useState } from "react";
import { Pipeline } from "./pipe-item";
import {
  PipelineItem,
  ResponseGetPipelines,
} from "@/lib/hey-api/client/types.gen";

export default function RunLogs() {
  const [pipelines, setPipelines] = useState<PipelineItem[]>([]);

  const fetchPipelines = async () => {
    const response = await getPipelinesPipelinesGet();
    if (response.data) {
      const responseData: ResponseGetPipelines = response.data;
      const pipelines: PipelineItem[] = responseData.data;
      setPipelines(pipelines);
    }
  };

  useEffect(() => {
    fetchPipelines();
  }, []);

  return (
    <ContentLayout title="Pipelines">
      <div className="h-full flex flex-col p-6">
        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input type="search" placeholder="Search ..." className="pl-9" />
        </div>
        <h4 className="text-lg font-semibold mb-4">Technical Commands</h4>
        <div className="space-y-4">
          {pipelines.map((pipeline) => (
            <Pipeline
              key={pipeline._id}
              _id={pipeline._id}
              pipeline_name={pipeline.pipeline_name}
              history={pipeline.history}
            />
          ))}
        </div>
      </div>
    </ContentLayout>
  );
}