"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Bar, BarChart, CartesianGrid, YAxis, Cell } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

interface GraphViewProps {
  data: [];
}

const chartConfig = {
  yieldPerHectare: {
    label: "Yield Per Hectare",
    color: "hsl(var(--chart-1))",
  },
};

export function GraphView({ data }: GraphViewProps) {
  return (
    <Card className="h-[450px">
      <CardContent className="h-[400px]">
        <ChartContainer config={chartConfig}>
          <div className="w-full overflow-x-auto">
            <BarChart
              data={data}
              width={Math.max(800, data.length * 60)}
              height={400}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <YAxis dataKey="YieldPerHectare" />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    labelFormatter={(label) => `Location: ${label}`}
                    formatter={(value) => [
                      `Yield Per Hectare: ${Number(value).toFixed(1)}`,
                    ]}
                  />
                }
              />
              <Bar dataKey="YieldPerHectare" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={chartConfig.yieldPerHectare.color}
                  />
                ))}
              </Bar>
            </BarChart>
          </div>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
