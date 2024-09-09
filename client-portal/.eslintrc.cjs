module.exports = {
  extends: [
    "universe",
    "universe/native",
    "universe/web",
    "universe/shared/typescript-analysis",
  ],
  overrides: [
    {
      files: ["*.ts", "*.tsx", "*.d.ts"],
      parserOptions: {
        project: "./tsconfig.json",
      },
    },
  ],
  plugins: ["react-hooks"],
  rules: {
    "import/order": "off",
  },
  env: {
    node: true,
  },
};
