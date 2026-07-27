export type AnalyticsEvent = "page_view" | "search" | "filter" | "export" | "error";
export interface Analytics { track(event: AnalyticsEvent, properties?: Record<string, string | number | boolean>): void }
export const analytics: Analytics = { track() { /* No provider is enabled by default. */ } };
