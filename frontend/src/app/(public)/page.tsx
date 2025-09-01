"use client";
import { FeatureCard } from "@/components/feature-card";
import { ThemeToggle } from "@/components/theme-toggle";
import { LoginDialog } from "@/components/logindialogue";

export default function LandingPage() {
  return (
    <div className="flex flex-col h-screen">
      <header className="border-b">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold px-4">CSA Datastore</h1>
          <div className="flex h-16 items-center px-4 justify-end space-x-4">
            <ThemeToggle />
            <LoginDialog />
          </div>
        </div>
      </header>
      <div className="flex-1 flex">
        <div className="flex-1 flex flex-col">
          {/* Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="container mx-auto px-4 py-8">
              <div className="max-w-4xl mx-auto text-center mb-16">
                <h1 className="text-4xl font-bold mb-6">
                  Welcome to CSA Data Store
                </h1>
                <p className="text-xl text-muted-foreground mb-4">
                  Empowering sustainable agriculture through open data and
                  collaboration.
                </p>
                <p className="text-lg text-muted-foreground">
                  Access valuable agricultural data and tools to drive
                  evidence-based policy making.
                </p>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
                <FeatureCard
                  title="Open Data Access"
                  description="Explore a vast collection of agricultural datasets from research institutions across India."
                />
                <FeatureCard
                  title="Collaborative Platform"
                  description="Connect with researchers, policymakers, and farmers to share knowledge and insights."
                />
                <FeatureCard
                  title="Policy Insights"
                  description="Utilize analytical tools to extract meaningful insights for informed decision-making."
                />
              </div>
            </div>
          </main>
          {/* Footer */}
          <footer className="border-t py-6 text-center text-sm text-muted-foreground">
            © 2024 CSA Data Store. All rights reserved.
          </footer>
        </div>
      </div>
    </div>
  );
}
