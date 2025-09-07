import { DatePickerWithRange } from "@/components/ui/date-range-picker";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { ContentLayout } from "@/components/admin-panel/content-layout";

const data = [
  {
    id: "1",
    commands: "Pipeline 2",
    dateTime: "22-02-2024 10:00 AM",
    user: "User1",
    status: "Running",
    duration: "--",
  },
];

export default function LogStatistics() {
  return (
    <ContentLayout title="Pipeline Statistics">
      <div className="h-full flex flex-col space-y-4 p-4">
        <div className="relative p-4 shrink-0">
          <Search className="absolute left-7 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search dataset"
            className="pl-10 w-full"
          />
        </div>

        <div className="grid gap-6 md:grid-cols-2 mb-6">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Choose Command
            </label>
            <Select defaultValue="pipeline2">
              <SelectTrigger>
                <SelectValue placeholder="Select pipeline" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pipeline1">Pipeline 1</SelectItem>
                <SelectItem value="pipeline2">Pipeline 2</SelectItem>
                <SelectItem value="pipeline3">Pipeline 3</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Date Range</label>
            <DatePickerWithRange />
          </div>
        </div>

        <DataTable columns={columns} data={data} />
      </div>
    </ContentLayout>
  );
}
