"use client";

import { useState } from "react";
import { ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ContentLayout } from "@/components/admin-panel/content-layout";

interface User {
  id: number;
  name: string;
  email: string;
  role: "Admin" | "Contributor";
}

export default function UserManagement() {
  const [users] = useState<User[]>([
    { id: 1, name: "User 1", email: "ken99@yahoo.com", role: "Admin" },
    { id: 2, name: "User 2", email: "abe45@gmail.com", role: "Admin" },
    {
      id: 3,
      name: "User 3",
      email: "monserrat44@gmail.com",
      role: "Contributor",
    },
    { id: 4, name: "User 4", email: "silas22@gmail.com", role: "Contributor" },
    {
      id: 5,
      name: "User 5",
      email: "carmella@hotmail.com",
      role: "Contributor",
    },
  ]);

  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRows] = useState<number[]>([]);

  // Filter users based on search term
  const filteredUsers = users.filter((user) =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  // Sort users by email
  const sortedUsers = [...filteredUsers].sort((a, b) => {
    if (sortDirection === "asc") {
      return a.email.localeCompare(b.email);
    } else {
      return b.email.localeCompare(a.email);
    }
  });

  // Toggle sort direction
  const toggleSort = () => {
    setSortDirection(sortDirection === "asc" ? "desc" : "asc");
  };

  // Toggle row selection
  //   const toggleRowSelection = (id: number) => {
  //     if (selectedRows.includes(id)) {
  //       setSelectedRows(selectedRows.filter((rowId) => rowId !== id))
  //     } else {
  //       setSelectedRows([...selectedRows, id])
  //     }
  //   }

  return (
    <ContentLayout title="User Management">
      <div className="flex flex-col h-full p-6">
        <div className="flex-1 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold tracking-tight">
              User Management
            </h2>
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 max-w-sm">
              <Input
                placeholder="Filter emails..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline">Add User</Button>
          </div>

          <div className="rounded-md border">
            <div className="relative overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px] sm:w-[150px]">
                      User Name
                    </TableHead>
                    <TableHead className="w-[150px] sm:w-[200px]">
                      <div
                        className="flex items-center cursor-pointer"
                        onClick={toggleSort}
                      >
                        Email
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                      </div>
                    </TableHead>
                    <TableHead className="hidden sm:table-cell">Role</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell className="hidden sm:table-cell">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            user.role === "Admin"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {user.role}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="hidden sm:inline-flex"
                          >
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="hidden sm:inline-flex"
                          >
                            Permission
                          </Button>
                          <Button variant="destructive" size="sm">
                            Delete
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {selectedRows.length} of {users.length} row(s) selected.
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled={true}>
                Previous
              </Button>
              <Button variant="outline" size="sm">
                Next
              </Button>
            </div>
          </div>
        </div>
      </div>
    </ContentLayout>
  );
}
