"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  runPipelinePipelinesRunPost,
  getPipelineStatusPipelineStatusGet,
} from "@/lib/hey-api/client/sdk.gen";
import { useSession } from "next-auth/react";
import { usePipelineStatusCheck } from "@/components/hooks/check-pipeline-status";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import {
  RunPipelineRequest,
  RunPipelineResponse,
  PipelineItem,
  PipelineStatusResponse,
} from "@/lib/hey-api/client/types.gen";

export function Pipeline({ _id, pipeline_name, history }: PipelineItem) {
  const { data: session } = useSession();
  const username = session?.user?.name || "";
  const useremail = session?.user?.email || "";
  const historylength = history.length;
  const initialStatus =
    historylength > 0 ? history[historylength - 1]?.status : null;
  const initialExecId =
    historylength > 0 ? history[historylength - 1]?.exec_id : null;
  const [currentStatus, setCurrentStatus] = useState<string | null>(
    initialStatus,
  );
  const [currentExecId, setCurrentExecId] = useState<string | null>(
    initialExecId,
  );

  const runPipelineRequest: RunPipelineRequest = {
    pipeline_id: _id,
    pipeline_name: pipeline_name,
    username: username,
    user_email: useremail,
  };

  const runPipeline = async () => {
    const response = await runPipelinePipelinesRunPost({
      body: runPipelineRequest,
    });
    if (response.data) {
      const responseData: RunPipelineResponse = response.data;
      setCurrentExecId(responseData.execution_id);
      setCurrentStatus(responseData.status);
    }
  };

  const checkPipelineStatus = async () => {
    if (!currentExecId) return;

    try {
      const response = await getPipelineStatusPipelineStatusGet({
        query: {
          dataset_id: _id,
          exec_id: currentExecId,
        },
      });

      if (response.data) {
        const responseData: PipelineStatusResponse = response.data;
        const status = responseData.status;
        setCurrentStatus(status);
      }
    } catch (error) {
      console.error("Error checking pipeline status:", error);
    }
  };

  usePipelineStatusCheck(
    currentStatus as "running" | "completed" | "error" | null,
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
            onClick={runPipeline}
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
