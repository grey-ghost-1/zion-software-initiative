import type { ApiErrorBody } from "./types";

/** Thrown for any non-2xx response that uses the API's typed error envelope. */
export class ZionApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.name = "ZionApiError";
    this.status = status;
    this.code = body.error.code;
    this.requestId = body.error.request_id;
  }
}
