import { spawn } from "node:child_process";
import { resolve } from "node:path";
import { Plugin } from "@opencode/plugin";

interface RunSlopResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

function runSloperator(
  projectDirectory: string,
  file: string,
): Promise<RunSlopResult> {
  return new Promise((finish) => {
    const child = spawn("uv", ["run", "--no-active", "sloperator.py", file], {
      cwd: projectDirectory,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk;
    });

    // Spawn failures (for example, uv not on PATH) surface here, not on "close".
    child.on("error", (error) => {
      finish({ stdout, stderr: stderr + `${error.message}\n`, exitCode: -1 });
    });

    child.on("close", (code) => {
      finish({ stdout, stderr, exitCode: code ?? -1 });
    });
  });
}

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    const projectDirectory = ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang program with the Sloperator interpreter from the project root and return its stdout, stderr, and exit code as JSON.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Path to the .slop file, relative to the project root.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path } = input as { path: string };
          const result = await runSloperator(
            projectDirectory,
            resolve(projectDirectory, path),
          );
          return { content: JSON.stringify(result, null, 2) };
        },
      });
    });
  },
});
