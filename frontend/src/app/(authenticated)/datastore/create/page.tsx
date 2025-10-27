"use client";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { zodResolver } from "@hookform/resolvers/zod";
import { CloudUpload, Paperclip } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import FileDownloadButton from "@/components/file-upload/FileDownloadButton";
import { TagInput } from "@/app/(authenticated)/datastore/create/tag-input";
import { useToast } from "@/components/hooks/use-toast";
import { useSession } from "next-auth/react";
import { SearchDatatype } from "@/app/(authenticated)/datastore/create/search-datatype";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import {
  FileInput,
  FileUploader,
  FileUploaderContent,
} from "@/components/file-upload/FileUpload";
import {
  DatasetConfigurationDialog,
  DatasetConfigFormData,
} from "@/app/(authenticated)/datastore/create/dataset-cofig-dialogue";
import { createDataset } from "@/lib/hey-api/client/sdk.gen";

export type TemporalGranularity = "year" | "month" | "day";
export type SpatialGranularity = "country" | "state" | "district" | "village" | "lat_long";

export interface CreateDatasetInformationRequest {
  dataset_id: string;
  file_id: string;
  dataset_name: string;
  description: string;
  tags: string[];
  dataset_type: string;
  permission: string;
  is_spatial: boolean;
  is_temporal: boolean;
  temporal_granularities: TemporalGranularity[];
  spatial_granularities: SpatialGranularity[];
  location_columns: string[];
  time_columns: string[];
}

export interface CreateDatasetInformationResponse {
  status: string;
  id: string;
}

// Zod schemas for each section
const datasetInformationSchema = z.object({
  name: z.string().min(1, "Dataset name is required"),
  description: z.string().optional(),
  permission: z.enum(["public", "private"]),
  category: z.string().optional(),
  tags: z.array(z.string()).optional(),
});

// Type for the complete form data
type CompleteFormData = {
  datasetInformation: z.infer<typeof datasetInformationSchema>;
  dataSelection: {
    file_id: string;
  };
  configuration?: {
    isSpatial: boolean;
    isTemporal: boolean;
    spatialHierarchy?: {
      lat?: number;
      long?: number;
      country?: string;
      state?: string;
      district?: string;
      village?: string;
    };
    temporalHierarchy?: string;
  };
};

export default function Create() {
  const [files, setFiles] = useState<File[] | null>(null);
  const [fileUrls, setFileUrls] = useState<string[]>([]);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadedFileData, setUploadedFileData] = useState<{
    dataset_id: string;
    file_id: string;
  } | null>(null);
  const { toast } = useToast();
  const { data: session } = useSession();

  const dropZoneConfig = {
    accept: {
      "text/csv": [".csv"],
    },
    maxFiles: 1,
    multiple: false,
    maxSize: 4 * 1024 * 1024,
  };

  const form = useForm<z.infer<typeof datasetInformationSchema>>({
    resolver: zodResolver(datasetInformationSchema),
    defaultValues: {
      name: "",
      description: "",
      permission: "public",
      tags: [],
    },
  });

  // Check if all required fields are filled
  useEffect(() => {
    const checkFormValidity = () => {
      const datasetInfoValid = form.formState.isValid;
      const dataSelectionValid = fileUrls.length > 0;

      setIsFormValid(datasetInfoValid && dataSelectionValid);
    };

    checkFormValidity();
  }, [form.formState.isValid, fileUrls.length]);

  async function onSubmit(
    data: z.infer<typeof datasetInformationSchema>,
    configData: DatasetConfigFormData,
  ) {
    setIsSubmitting(true);

    try {
      // Validate that we have uploaded file data
      if (!uploadedFileData) {
        toast({
          title: "Error",
          description:
            "File upload data not available. Please upload the file again.",
          variant: "destructive",
        });
        return;
      }

      const completeData: CompleteFormData = {
        datasetInformation: data,
        dataSelection: {
          file_id: fileUrls[0] || "",
        },
        configuration: configData,
      };

      console.log("Complete form data:", completeData);
      console.log("Uploaded file data:", uploadedFileData);

      // Prepare the dataset object for the API
      const datasetPayload: CreateDatasetInformationRequest  = {
        dataset_id: uploadedFileData.dataset_id,
        file_id: uploadedFileData.file_id,
        dataset_name: data.name,
        description: data.description || '',
        dataset_type: data.category || '',
        tags: data.tags || [],
        permission: data.permission,
        is_spatial: configData.isSpatial,
        is_temporal: configData.isTemporal,
        spatial_granularities: [],
        temporal_granularities: [],
        location_columns: [],
        time_columns: []
      };
      console.log("Dataset payload:", datasetPayload);

      // Make the API call
      const response =
        await createDataset({
          body: datasetPayload,
          headers: {
            Authorization: `Bearer ${session?.user?.apiToken}`,
          },
        });
      const responseData = response.data as CreateDatasetInformationResponse;
      if(!responseData.status){
        throw new Error("Failed to create dataset");
      }
      if (response.data && response.data.status === "success") {
        toast({
          title: "Success!",
          description: "Dataset created successfully.",
        });

        // Reset the form
        form.reset({
          name: "",
          description: "",
          permission: "public",
          tags: [],
        });
        setFiles(null);
        setFileUrls([]);
        setUploadedFileData(null);
        setIsConfigDialogOpen(false);
      } else {
        console.error("API Error:", response.error);
        toast({
          title: "Error",
          description: "Failed to create dataset. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error creating dataset:", error);
      toast({
        title: "Error",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleConfigureDataset = () => {
    setIsConfigDialogOpen(true);
  };

  const handleConfigComplete = (data: DatasetConfigFormData) => {
    console.log("Configuration completed:", data);
    setIsConfigDialogOpen(false);
  };

  const handleSubmitForm = async (configData: DatasetConfigFormData) => {
    const data = form.getValues();
    await onSubmit(data, configData);
  };

  return (
    <ContentLayout title="Create">
      <Form {...form}>
        <form className="h-full flex flex-col space-y-6 p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-background shadow-none">
              <CardHeader>
                <CardTitle>Dataset Information</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-6">
                <div className="space-y-2">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Dataset Name
                          <span className="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter dataset name"
                            {...field}
                            type="text"
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description (Optional)</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Enter dataset description"
                            {...field}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <FormField
                    control={form.control}
                    name="permission"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Permission<span className="text-destructive">*</span>
                        </FormLabel>
                        <FormControl>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <SelectTrigger id="permission" className="w-full">
                              <SelectValue placeholder="Select permission" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="public">Public</SelectItem>
                              <SelectItem value="private">Private</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <FormField
                    control={form.control}
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Dataset Type</FormLabel>
                        <FormControl>
                          <SearchDatatype
                            options={[]}
                            value={field.value}
                            onValueChange={field.onChange}
                            placeholder="Implement soon"
                            searchPlaceholder="Search categories..."
                            emptyMessage="No categories found."
                            disabled={true}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <div className="space-y-2">
                  <FormField
                    control={form.control}
                    name="tags"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Tags</FormLabel>
                        <FormControl>
                          <TagInput
                            value={field.value || []}
                            onChange={field.onChange}
                            placeholder="Add tags (press Enter or comma to add)"
                            maxTags={5}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-background shadow-none">
              <CardHeader>
                <CardTitle>Data Selection</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-6">
                <p className="text-sm text-muted-foreground">
                  Choose a file with relevant data from your computer to upload.
                  <br />
                  Acceptable file format: CSV
                </p>
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    File Upload<span className="text-destructive">*</span>
                  </label>
                  <FileUploader
                    value={files}
                    onValueChange={(value) => {
                      setFiles(value);
                    }}
                    onUploadComplete={(urls, fileData) => {
                      setFileUrls(urls);
                      if (fileData) {
                        setUploadedFileData(fileData);
                      }
                    }}
                    dropzoneOptions={dropZoneConfig}
                    className="relative bg-background rounded-lg p-2"
                    authToken={session?.user?.apiToken || ""}
                  >
                    <FileInput
                      id="file-input"
                      className="outline-dashed outline-1 outline-border"
                    >
                      <div className="flex items-center justify-center flex-col p-8 w-full">
                        <CloudUpload className="text-muted-foreground w-8 h-8" />
                        <p className="mb-1 text-sm text-muted-foreground text-center">
                          Click&nbsp;to&nbsp;upload or drag&nbsp;and&nbsp;drop
                        </p>
                      </div>
                    </FileInput>
                    <FileUploaderContent />
                  </FileUploader>
                </div>
                {fileUrls.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">Uploaded File</h3>
                    <div className="space-y-2">
                      {fileUrls.map((url, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 p-2 border rounded-lg"
                        >
                          <Paperclip className="h-4 w-4 stroke-current" />
                          <span className="flex-1 truncate">{url}</span>
                          <FileDownloadButton
                            fileID={url}
                            variant="outline"
                            size="sm"
                            downloadName={`File-${index + 1}`}
                            accessToken={session?.user?.apiToken || ""}
                          >
                            View File
                          </FileDownloadButton>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <Button
                  className="w-full"
                  disabled={!isFormValid || isSubmitting}
                  onClick={handleConfigureDataset}
                  type="button"
                >
                  {isSubmitting ? "Creating Dataset..." : "Configure Dataset"}
                </Button>
              </CardContent>
            </Card>
          </div>
        </form>
      </Form>
      <DatasetConfigurationDialog
        open={isConfigDialogOpen}
        onOpenChange={setIsConfigDialogOpen}
        onComplete={handleConfigComplete}
        onSubmitForm={handleSubmitForm}
        isSubmitting={isSubmitting}
      />
    </ContentLayout>
  );
}
