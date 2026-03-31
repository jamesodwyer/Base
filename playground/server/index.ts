import path from "path";
import { createApp } from "./routes";

const PORT = 3099;
const tokensDir = path.resolve(import.meta.dirname, "../../tokens");

const app = createApp(tokensDir);

app.listen(PORT, () => {
  console.log(`Token Playground API running at http://localhost:${PORT}`);
  console.log(`Reading tokens from: ${tokensDir}`);
});
