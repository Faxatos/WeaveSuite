import type { NextConfig } from 'next';
import { resolve } from 'path';

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      'autoprefixer': resolve('./node_modules/autoprefixer')
    };
    return config;
  }
};

export default nextConfig;