// Global type declarations for Vercel deployment
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
      [key: string]: string | undefined;
    }
  }
  
  var process: {
    env: NodeJS.ProcessEnv;
  };
}

export {};
