/// <reference types="vite/client" />

declare module "*.css" {
  const css: string;
  export default css;
}

interface ImportMetaEnv {
  readonly VITE_FIELDOPS_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}