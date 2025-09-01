import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://localhost:8000/openapi.json",
  output: "src/lib/hey-api/client",
  plugins: [
    {
      baseUrl: false,
      name: "@hey-api/client-fetch",
      runtimeConfigPath: "./lib/hey-api/hey-api.ts",
    },
  ],
});
