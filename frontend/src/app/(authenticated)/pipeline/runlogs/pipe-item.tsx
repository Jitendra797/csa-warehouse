'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { getPipelineStatusPipelineStatusPost, runPipelineRunPipelinePost } from '@/lib/hey-api/client/sdk.gen'
import { RunPipelineRequest, PipelineStatusRequest, RunPipelineResponse, PipelineStatusResponse } from '@/lib/hey-api/client/types.gen'
import { useSession } from 'next-auth/react'
import { usePipelineStatusCheck } from '@/components/hooks/check-pipeline-status'
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

export interface HistoryItem {
  'exec-id': string
  status: string
  executed_at: string
  'user-email': string
}

export interface PipelineItemProps {
  dataset_id: string
  dataset_name: string
  history: HistoryItem[]
}

export function PipelineItem({ dataset_id, dataset_name, history }: PipelineItemProps) {
  const { data: session } = useSession()
  const [pipelineStatus, setPipelineStatus] = useState<'completed' | 'running' | 'error' | null>(null)

  // Get the most recent status from history
  const getLatestStatus = () => {
    if (history.length === 0) return null
    const latest = history[history.length - 1]
    return latest.status as 'completed' | 'running' | 'error' | null
  }

  const runPipeline = async () => {
    try {
      const runRequest: RunPipelineRequest = {
        pipeline_id: dataset_id,
        username: session?.user?.name || '',
        user_email: session?.user?.email || '',
      }

      // Submit the task
      const response = await runPipelineRunPipelinePost({
        body: runRequest
      })

      if (response.data) {
        const responseData: RunPipelineResponse = response.data
        setPipelineStatus(responseData.status)
      }
    } catch (error) {
      console.error('Failed to run pipeline:', error)
      setPipelineStatus('error')
    }
  }

  const checkPipelineStatus = async () => {
    try {
      const requestBody: PipelineStatusRequest = {
        pipeline_id: dataset_id,
        user_email: session?.user?.email || '',
      }
      const response = await getPipelineStatusPipelineStatusPost({
        body: requestBody
      })
      if (response.data) {
        const responseData: PipelineStatusResponse = response.data
        setPipelineStatus(responseData.status)
      }
    } catch (error) {
      console.error('Failed to check pipeline status:', error)
    }
  }

  // Use the custom hook to automatically check pipeline status after 30 seconds
  usePipelineStatusCheck(pipelineStatus, checkPipelineStatus, dataset_id)

  // Determine current status - prioritize live status over history
  const currentStatus = pipelineStatus || getLatestStatus()

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">Pipeline: {dataset_name}</h2>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Run Pipeline Button - always visible */}
            <Button
              variant="outline"
              size="sm"
              onClick={runPipeline}
              disabled={currentStatus === 'running'}
            >
              Run Pipeline
            </Button>
            
            {/* Status Button - always visible */}
            {currentStatus === 'running' && (
              <Button
                variant="secondary"
                size="sm"
                disabled
              >
                <div className="flex items-center gap-2">
                  <Loader2 className="animate-spin h-4 w-4" />
                  Running
                </div>
              </Button>
            )}
            
            {currentStatus === 'completed' && (
              <Button
                variant="secondary"
                size="sm"
                disabled
              >
                <div className="flex items-center gap-2">
                  <CheckCircle className="text-green-500 h-4 w-4" />
                  Completed
                </div>
              </Button>
            )}
            
            {currentStatus === 'error' && (
              <Button
                variant="secondary"
                size="sm"
                disabled
              >
                <div className="flex items-center gap-2">
                  <AlertCircle className="text-red-500 h-4 w-4" />
                  Error
                </div>
              </Button>
            )}

            {currentStatus === null && (
              <Button
                variant="secondary"
                size="sm"
                disabled
              >
                Status
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

