import { useEffect, useRef } from "react";

export type PipelineStatus = "running" | "completed" | "error" | "null";

export const usePipelineStatusCheck = (
  pipelineStatus: PipelineStatus,
  checkPipelineStatus: () => Promise<void>,
  pipelineId: string,
  execId: string | null,
) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (pipelineStatus === "running") {
      checkPipelineStatus();
      intervalRef.current = setInterval(() => {
        checkPipelineStatus();
      }, 30 * 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [pipelineStatus, checkPipelineStatus, pipelineId, execId]);
};
