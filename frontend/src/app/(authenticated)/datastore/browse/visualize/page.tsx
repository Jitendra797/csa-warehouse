"use client";
import { useState } from "react";
import { BarChart2, Map, Table2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TableView } from "./table-view";
import { GraphView } from "./graph-view";
import { MapView } from "./map-view";
import { ContentLayout } from "@/components/admin-panel/content-layout";

export default function Visualize() {
  const [tab, setTab] = useState("table");

  return (
    <ContentLayout title="Visualize">
      <div className="space-y-8 p-6">
        <Tabs
          defaultValue="table"
          value={tab}
          onValueChange={setTab}
          className="w-full"
        >
          <div className="flex items-center justify-between mb-6">
            <TabsList className="grid w-[400px] grid-cols-3">
              <TabsTrigger value="table" className="flex items-center gap-2">
                <Table2 className="h-4 w-4" />
                Table
              </TabsTrigger>
              <TabsTrigger value="graph" className="flex items-center gap-2">
                <BarChart2 className="h-4 w-4" />
                Graph
              </TabsTrigger>
              <TabsTrigger value="map" className="flex items-center gap-2">
                <Map className="h-4 w-4" />
                Map
              </TabsTrigger>
            </TabsList>
          </div>
          <TabsContent value="table">
            <TableView data={[]} />
          </TabsContent>
          <TabsContent value="graph">
            <GraphView data={[]} />
          </TabsContent>
          <TabsContent value="map">
            <MapView data={[]} />
          </TabsContent>
        </Tabs>
      </div>
    </ContentLayout>
  );
}
