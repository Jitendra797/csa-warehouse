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
import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function LoginDialog() {
  const router = useRouter();
  const { status } = useSession();
  const [error, setError] = useState<string | null>(null);

  // Redirect if already authenticated
  if (status === "authenticated") {
    router.push("/datastore/browse");
    return null;
  }

  const handleGoogleSignIn = async () => {
    try {
      const result = await signIn("google", {
        callbackUrl: "/datastore/browse",
        redirect: false,
      });

      if (result?.error) {
        setError("Not authorized. Please contact administrator.");
      } else if (result?.ok) {
        router.push("/datastore/browse");
      }
    } catch (error) {
      console.error("Sign in error:", error);
      setError("An error occurred during sign in");
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">
          {status === "loading" ? "Loading..." : "Login"}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle className="text-center">Login Page</DialogTitle>
          <DialogDescription className="text-center">
            Sign in with your authorized Google account.
          </DialogDescription>
          {error && <p className="text-red-500 text-center text-sm">{error}</p>}
        </DialogHeader>
        <DialogFooter>
          <Button
            onClick={handleGoogleSignIn}
            className="w-full"
            variant="outline"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Loading..." : "Sign In with Google"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
