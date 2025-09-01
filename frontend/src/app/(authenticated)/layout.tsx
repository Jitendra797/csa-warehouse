import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../globals.css";
import AdminPanelLayout from "@/components/admin-panel/admin-panel-layout";
import { Toaster } from "@/components/ui/toaster";

export const metadata: Metadata = {
  title: "CSA Data Store",
  description: "warehouse management system",
};

const inter = Inter({ subsets: ["latin"] });

export default function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className={inter.className}>
      <AdminPanelLayout>{children}</AdminPanelLayout>
      <Toaster />
    </div>
  );
}
