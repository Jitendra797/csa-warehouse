"use client";

import type { ColumnDef } from "@tanstack/react-table";

export type LogEntry = {
  id: string;
  commands: string;
  dateTime: string;
  user: string;
  status: string;
  duration: string;
};

export const columns: ColumnDef<LogEntry>[] = [
  {
    accessorKey: "id",
    header: "ID",
  },
  {
    accessorKey: "commands",
    header: "Commands",
  },
  {
    accessorKey: "dateTime",
    header: "Date/Time",
  },
  {
    accessorKey: "user",
    header: "User",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <div
          className={
            status === "Running" ? "text-green-600 dark:text-green-400" : ""
          }
        >
          {status}
        </div>
      );
    },
  },
  {
    accessorKey: "duration",
    header: "Duration",
  },
];
