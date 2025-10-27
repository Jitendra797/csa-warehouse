"use client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { signIn } from "next-auth/react";

export function LoginDialog() {
  const handleGoogleSignIn = async () => {
    await signIn("google", {
      callbackUrl: "/datastore/browse",
    });
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Login</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Login Page</DialogTitle>
          <DialogDescription>
            Sign in with your authorized Google account.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button onClick={handleGoogleSignIn} className="w-full">
            Sign In with Google
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
