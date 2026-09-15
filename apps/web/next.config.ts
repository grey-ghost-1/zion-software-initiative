import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@zion/ui", "@zion/api-client"],
};

export default nextConfig;
