// Forwards all requests to a single container instance running the FastAPI app.
// The container is "basic" (1 GiB memory); the app uses about 470 MB with the grid loaded.
import { DurableObject } from "cloudflare:workers";

interface Env {
  BURN_APP: DurableObjectNamespace<BurnApp>;
}

const PORT = 8080;
const HEALTH_PATH = "/api/health";
// Keep the container warm for 30 minutes after the last request (judging traffic is bursty).
const INACTIVITY_TIMEOUT_MS = 30 * 60 * 1000;

export class BurnApp extends DurableObject<Env> {
  private starting: Promise<void> | undefined;

  async fetch(request: Request): Promise<Response> {
    this.starting ??= this.startAndWaitForPort().finally(() => {
      this.starting = undefined;
    });
    await this.starting;

    const url = new URL(request.url);
    url.protocol = "http:";
    url.host = "container";
    const forwarded = new Request(url, request);
    forwarded.headers.delete("host");
    return this.ctx.container!.getTcpPort(PORT).fetch(forwarded);
  }

  private async startAndWaitForPort(): Promise<void> {
    const container = this.ctx.container!;
    if (!container.running) {
      container.start({
        image: container.images.base,
        instance: "basic",
        enableInternet: true, // map tiles load in the browser; the app itself needs no outbound calls
      });
    }
    await container.setInactivityTimeout(INACTIVITY_TIMEOUT_MS);

    // Loading the Parquet grid takes a few seconds; wait up to 60 s for /api/health.
    const port = container.getTcpPort(PORT);
    for (let attempt = 0; attempt < 120; attempt++) {
      try {
        const r = await port.fetch(`http://container${HEALTH_PATH}`, {
          signal: AbortSignal.timeout(1000),
        });
        await r.body?.cancel();
        if (r.ok) return;
      } catch {
        // not listening yet
      }
      await scheduler.wait(500);
    }
    throw new Error(`Container did not become ready on port ${PORT}`);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return env.BURN_APP.getByName("singleton").fetch(request);
  },
} satisfies ExportedHandler<Env>;
