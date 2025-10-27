"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { usePipelineStatusCheck } from "@/components/hooks/check-pipeline-status";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { runPipeline, getPipelineStatus } from "@/lib/hey-api/client/sdk.gen";
import { useSession } from "next-auth/react";

export interface PipelineItem {
  _id: string;
  pipeline_name: string;
  is_enabled: boolean;
  pipeline_status: PipelineStatus;
}

export type PipelineStatus = "running" | "completed" | "error" | "null";

export interface RunPipelineRequest {
  pipeline_id: string;
  pipeline_name: string;
}

export interface RunPipelineResponse {
  status: string;
  execution_id: string;
  executed_at: string;
}

export function Pipeline({
  _id,
  pipeline_name,
  is_enabled,
  pipeline_status,
}: PipelineItem) {
  console.log(is_enabled);
  const [currentStatus, setCurrentStatus] =
    useState<PipelineStatus>(pipeline_status);
  const [currentExecId, setCurrentExecId] = useState<string | null>(null);
  const { data: session } = useSession();

  const runPipelineRequest: RunPipelineRequest = {
    pipeline_id: _id,
    pipeline_name: pipeline_name,
  };

  const runPipelineFunction = async () => {
    const response = await runPipeline({
      body: runPipelineRequest,
      headers: {
        Authorization: `Bearer ${session?.user?.apiToken}`,
        "Content-Type": "application/json",
      },
    });
    if (response.data) {
      const responseData: RunPipelineResponse = response.data;
      setCurrentExecId(responseData.execution_id);
      setCurrentStatus(responseData.status as PipelineStatus);
    }
  };

  const checkPipelineStatus = async () => {
    if (!currentExecId) return;

    try {
      const response = await getPipelineStatus({
        query: {
          pipeline_id: _id,
          execution_id: currentExecId,
        },
        headers: {
          Authorization: `Bearer ${session?.user?.apiToken}`,
          "Content-Type": "application/json",
        },
      });

      if (response.data) {
        const responseData: PipelineStatus = response.data;

        setCurrentStatus(responseData);
      }
    } catch (error) {
      console.error("Error checking pipeline status:", error);
    }
  };

  usePipelineStatusCheck(
    currentStatus as PipelineStatus,
    checkPipelineStatus,
    _id,
    currentExecId,
  );

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">Pipeline: {pipeline_name}</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={runPipelineFunction}
            disabled={currentStatus === "running"}
          >
            Run Pipeline
          </Button>

          {currentStatus === "running" && (
            <Button variant="secondary" size="sm" disabled>
              <div className="flex items-center gap-2">
                <Loader2 className="animate-spin h-4 w-4" />
                Running
              </div>
            </Button>
          )}

          {currentStatus === "completed" && (
            <Button variant="secondary" size="sm" disabled>
              <div className="flex items-center gap-2">
                <CheckCircle className="text-green-500 h-4 w-4" />
                Completed
              </div>
            </Button>
          )}

          {currentStatus === "error" && (
            <Button variant="secondary" size="sm" disabled>
              <div className="flex items-center gap-2">
                <AlertCircle className="text-red-500 h-4 w-4" />
                Error
              </div>
            </Button>
          )}

          {currentStatus === null && (
            <Button variant="secondary" size="sm" disabled>
              Status
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
