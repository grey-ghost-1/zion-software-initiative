import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@zion/ui", "@zion/api-client"],
  async redirects() {
    return [
      { source: "/harbor", destination: "/flagships/harbor", permanent: true },
      { source: "/initiatives", destination: "/flagships", permanent: true },
      { source: "/initiatives/haven", destination: "/flagships/haven", permanent: true },
      { source: "/projects", destination: "/flagships", permanent: true },
      {
        source: "/projects/community-aid-hub",
        destination: "/flagships/harbor",
        permanent: true,
      },
      {
        source: "/projects/health-navigator",
        destination: "/flagships/haven",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
