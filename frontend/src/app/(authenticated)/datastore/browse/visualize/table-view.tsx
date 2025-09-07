"use client";
import { DataTable } from "@/components/TableView/data-table";

interface TableViewProps {
  data: [];
  isLoading?: boolean;
}

export function TableView({ data, isLoading }: TableViewProps) {
  return <DataTable columns={[]} data={data} isLoading={isLoading} />;
}
