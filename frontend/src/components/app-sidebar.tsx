"use client";
import * as React from "react";
import {
  AudioWaveform,
  BookOpen,
  Bot,
  Command,
  Frame,
  GalleryVerticalEnd,
  Map,
  PieChart,
  Settings2,
  SquareTerminal,
} from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

// This is sample data.
const data = {
  user: {
    name: "User",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "Acme Inc",
      logo: GalleryVerticalEnd,
      plan: "Enterprise",
    },
    {
      name: "Acme Corp.",
      logo: AudioWaveform,
      plan: "Startup",
    },
    {
      name: "Evil Corp.",
      logo: Command,
      plan: "Free",
    },
  ],
  navMain: [
    {
      title: "CSA Datastore",
      url: "#",
      icon: SquareTerminal,
      isActive: true,
      items: [
        {
          title: "Browse",
          url: "/datastore/browse",
        },
        {
          title: "Manage",
          url: "/datastore/manage",
        },
        {
          title: "Create",
          url: "/datastore/create",
        },
      ],
    },
    {
      title: "Pipeline Management",
      url: "#",
      icon: Bot,
      items: [
        {
          title: "Run Logs",
          url: "/pipeline/runlogs",
        },
        {
          title: "Log Statistics",
          url: "/pipeline/logstatistics",
        },
      ],
    },
    {
      title: "User Management",
      url: "/usermanagement",
      icon: BookOpen,
    },
    {
      title: "About Us",
      url: "/about",
      icon: BookOpen,
    },
    {
      title: "Settings",
      url: "/settings",
      icon: Settings2,
    },
  ],
  projects: [
    {
      name: "Design Engineering",
      url: "#",
      icon: Frame,
    },
    {
      name: "Sales & Marketing",
      url: "#",
      icon: PieChart,
    },
    {
      name: "Travel",
      url: "#",
      icon: Map,
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const isAdmin = true; // TODO: Move to outside proos session?.user?.role === 'Admin'

  const filteredNavItems = React.useMemo(() => {
    return data.navMain.filter((item) => {
      // Hide Pipeline Management if user is not admin
      if (item.title === "Pipeline Management" && !isAdmin) {
        return false;
      }
      return true;
    });
  }, [isAdmin]);

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <h1 className="text-xl font-semibold text-center">CSA Datastore</h1>
      </SidebarHeader>
      <SidebarContent className="font-medium">
        <NavMain items={filteredNavItems} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
