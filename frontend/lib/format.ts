export const money = (value: number | null, currency = "DOP") =>
  value === null ? "Dato no disponible" : new Intl.NumberFormat("es-DO", { style: "currency", currency }).format(value);
export const date = (value: string | null) =>
  value ? new Intl.DateTimeFormat("es-DO", { dateStyle: "medium" }).format(new Date(value)) : "Dato no disponible";
