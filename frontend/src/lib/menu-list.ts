import {
    Group,
    LucideIcon,
    Box,
    Settings,
    Users,
    Workflow,
    Info,
    HelpCircle,
    Grid
  } from "lucide-react";
  
  type Submenu = {
    href: string;
    label: string;
    active?: boolean;
  };
  
  type Menu = {
    href: string;
    label: string;
    active?: boolean;
    icon: LucideIcon;
    submenus?: Submenu[];
  };
  
  type Group = {
    groupLabel: string;
    menus: Menu[];
  };
  
  export function getMenuList(): Group[] {
    return [
      {
        groupLabel: "",
        menus: [
            {
                href: "/dashboard",
                label: "Dashboards",
                icon: Grid,
                submenus: [
                    {
                        href: "/dashboard/kisanmitra",
                        label: "Kisanmitra",
                    },
                ]
            },
            {
                href: "/datastore",
                label: "Data Store",
                icon: Box,
                submenus: [
                    {
                        href: "/datastore/browse",
                        label: "Browse",
                    },
                    {
                        href: "/datastore/manage",
                        label: "Manage",
                    },
                    {
                        href: "/datastore/create",
                        label: "Create",
                    },
                ]
            },
            {
                href:"/pipeline",
                label: "Pipeline Management",
                icon: Workflow,
                submenus: [
                    {
                        href: "/pipeline/logstatistics",
                        label: "Pipeline Statistics",
                    },
                    {
                        href: "/pipeline/runlogs",
                        label: "Pipelines",
                    },
                ]
            },
            {
                href:"/usermanagement",
                label: "User Management",
                icon: Users,
            },
            {
                href:"/settings",
                label: "Settings",
                icon: Settings,
            },
            {
                href:"/about",
                label: "About",
                icon: Info,
            },
            {
                href:"/support",
                label: "Support",
                icon: HelpCircle,
            },
        ]
      },
    ];
  }
  