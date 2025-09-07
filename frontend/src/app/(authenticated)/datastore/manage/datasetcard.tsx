import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import { Mail, User, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export interface DatasetCardProps {
  dataset_id: string;
  dataset_name: string;
  description: string;
  pulled_from_pipeline: boolean;
  usernames: string[];
  useremails: string[];
  updated_at: string;
}

export function DatasetCard({
  dataset_id,
  dataset_name,
  description,
  useremails,
  usernames,
  updated_at,
  pulled_from_pipeline,
}: DatasetCardProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const usernameslength = usernames.length;
  const useremailslength = useremails.length;
  const username = usernames[usernameslength - 1];
  const useremail = useremails[useremailslength - 1];

  const handleView = async () => {
    setIsLoading(true);
    try {
      await router.push(`/datastore/browse/${encodeURIComponent(dataset_id)}`);
    } catch (error) {
      console.error("Navigation error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="bg-background h-[280px] flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <CardTitle className="text-lg font-semibold truncate">
          {dataset_name}
        </CardTitle>
        <CardDescription className="text-sm text-muted-foreground line-clamp-2 min-h-[2.5rem]">
          {description ? description : "No description"}
        </CardDescription>
        <p className="text-sm font-semibold text-foreground py-2">
          {pulled_from_pipeline ? (
            <>
              <span className="font-semibold">Pipeline Run on</span>{" "}
              {formatDate(updated_at)}
            </>
          ) : (
            <>
              <span className="font-semibold">Last Updated on</span>{" "}
              {formatDate(updated_at)}
            </>
          )}
        </p>
      </CardHeader>
      <CardContent className="pt-0 flex-1 flex flex-col">
        <div className="flex-1">
          <p className="text-sm font-semibold text-foreground mb-2">
            Pipeline Run By
          </p>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center">
              <User className="w-3 h-3 mr-1.5" />
              {username}
            </p>
            <p className="text-xs text-muted-foreground flex items-center">
              <Mail className="w-3 h-3 mr-1.5" />
              {useremail}
            </p>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <Button
            variant="outline"
            className="flex-1 border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            disabled
          >
            Edit
          </Button>
          <Button
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground"
            onClick={handleView}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              "View"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
