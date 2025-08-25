'use client'

import { ContentLayout } from "@/components/admin-panel/content-layout"
import { DataTable } from "@/components/TableView/data-table"
import { getDatasetByIdEndpointGetDatasetByIdPost } from "@/lib/hey-api/client/sdk.gen"
import { GetDatasetByIdRequest, GetDatasetByIdDetailedResponse } from "@/lib/hey-api/client/types.gen"
import { useEffect, useState, useCallback } from "react"
import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle } from "lucide-react"
import { useParams } from "next/navigation"

export default function DatasetDetails() {
    const params = useParams()
    const dataset_id = params.dataset_id as string
    const [datasetData, setDatasetData] = useState<GetDatasetByIdDetailedResponse | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchDatasetRows = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)
            
            const request: GetDatasetByIdRequest = {
                dataset_id: dataset_id,
                page_number: 0,
                limit: 10
            }
            
            const response = await getDatasetByIdEndpointGetDatasetByIdPost({
                body: request
            })
            
            if (response.data) {
                const responseData: GetDatasetByIdDetailedResponse = response.data
                setDatasetData(responseData)
            } else {
                throw new Error('Failed to fetch dataset rows')
            }
        } catch (err) {
            console.error('Error fetching dataset rows:', err)
            setError('Failed to load dataset. Please try again later.')
        } finally {
            setLoading(false)
        }
    }, [dataset_id])

    useEffect(() => {
        if (dataset_id) {
            fetchDatasetRows()
        }
    }, [dataset_id, fetchDatasetRows])

    // Generate columns dynamically based on the first row of data
    const generateColumns = (data: Record<string, unknown>[]): ColumnDef<Record<string, unknown>>[] => {
        if (!data || data.length === 0) return []
        
        const firstRow = data[0]
        return Object.keys(firstRow).map((key) => ({
            accessorKey: key,
            header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
            cell: ({ row }) => {
                const value = row.getValue(key)
                if (value === null || value === undefined) {
                    return <span className="text-muted-foreground">-</span>
                }
                if (typeof value === 'boolean') {
                    return (
                        <Badge variant={value ? "default" : "secondary"}>
                            {value ? "Yes" : "No"}
                        </Badge>
                    )
                }
                if (typeof value === 'number') {
                    return <span className="font-mono">{value}</span>
                }
                return <span>{String(value)}</span>
            }
        }))
    }

    const columns = datasetData?.data ? generateColumns(datasetData.data) : []

    if (loading) {
        return (
            <ContentLayout title="Dataset Details">
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            </ContentLayout>
        )
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
        )
    }

    return (
        <ContentLayout title="Dataset Details">
            <div className="h-full flex flex-col p-6 space-y-6">
                {datasetData && (
                    <>
                        <div className="space-y-6">
                            {/* Dataset Name */}
                            <div>
                                <h2 className="text-2xl font-bold">{datasetData.dataset_information.dataset_name}</h2>
                            </div>

                            {/* Description - Max 2 lines */}
                            <div className="space-y-2">
                                <h3 className="text-lg font-semibold">Description</h3>
                                <p className="text-base leading-relaxed line-clamp-2">
                                    {datasetData.dataset_information.description || "No description available"}
                                </p>
                            </div>

                            {/* Dataset Type, Created By, and Update Time in a row */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {/* Dataset Type */}
                                <div className="space-y-2">
                                    <h3 className="text-lg font-semibold">Dataset Type</h3>
                                    <p className="text-base">
                                        {datasetData.dataset_information.dataset_type || "Not specified"}
                                    </p>
                                </div>

                                {/* User Information */}
                                <div className="space-y-2">
                                    <h3 className="text-lg font-semibold">{datasetData.dataset_information.pulled_from_pipeline ? "Pipeline Run By" : "Dataset Uploaded By"}</h3>
                                    <div className="space-y-1">
                                        <p className="text-base text-muted-foreground">{datasetData.dataset_information.user_email}</p>
                                    </div>
                                </div>

                                {/* Last Updated Information */}
                                <div className="space-y-2">
                                    <h3 className="text-lg font-semibold">
                                        {datasetData.dataset_information.pulled_from_pipeline ? "Pipeline Last Run" : "Dataset Updated At"}
                                    </h3>
                                    <p className="text-base">
                                        {new Date(datasetData.dataset_information.updated_at).toLocaleString()}
                                    </p>
                                </div>
                            </div>

                            {/* Tags */}
                            <div className="space-y-2">
                                <div className="flex items-center gap-3 flex-wrap">
                                    <span className="text-lg font-semibold">Tags:</span>
                                    {datasetData.dataset_information.tags && datasetData.dataset_information.tags.length > 0 ? (
                                        datasetData.dataset_information.tags.map((tag, index) => (
                                            <Badge key={index} variant="secondary" className="text-sm px-3 py-1">
                                                {tag}
                                            </Badge>
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
                                data={datasetData.data}
                                isLoading={loading}
                            />
                        </div>
                    </>
                )}
            </div>
        </ContentLayout>
    )
}
