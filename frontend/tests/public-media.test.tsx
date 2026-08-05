import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { PublicMedia, selectPrimaryMedia } from "../components/public-media";
import type { PublicMediaCollection } from "../types/executive";

afterEach(() => cleanup());

const collection: PublicMediaCollection = {
  fallback_required: false,
  limitation: "Solo activos aprobados.",
  items: [
    {
      id: "logo",
      asset_type: "institution_logo",
      public_url: "https://example.test/logo.png",
      source_url: "https://example.test/source",
      source_name: "Portal oficial",
      verified_at: "2026-08-05T00:00:00Z",
      is_primary: true,
      alt_text: "Logo oficial",
      caption: "Identidad institucional",
      license_note: null,
      width: 400,
      height: 400,
    },
    {
      id: "building",
      asset_type: "institution_building",
      public_url: "https://example.test/building.jpg",
      source_url: null,
      source_name: "Archivo institucional",
      verified_at: null,
      is_primary: false,
      alt_text: "Edificio institucional",
      caption: null,
      license_note: "Uso informativo",
      width: 1200,
      height: 800,
    },
  ],
};

describe("media pública trazable", () => {
  it("respeta el orden editorial de tipos preferidos", () => {
    expect(selectPrimaryMedia(collection, ["institution_building", "institution_logo"])?.id).toBe("building");
    expect(selectPrimaryMedia(collection, ["official_banner", "institution_logo"])?.id).toBe("logo");
  });

  it("muestra fuente, texto alternativo y atribución", () => {
    render(<PublicMedia collection={collection} label="Presidencia" preferred={["institution_logo"]} variant="logo" />);
    expect(screen.getByRole("img", { name: "Logo oficial" })).toHaveAttribute("src", "https://example.test/logo.png");
    expect(screen.getByRole("link", { name: "Portal oficial" })).toHaveAttribute("href", "https://example.test/source");
    expect(screen.getByText("Identidad institucional")).toBeInTheDocument();
  });

  it("no inventa imágenes cuando no existe un activo aprobado", () => {
    render(<PublicMedia collection={{ items: [], fallback_required: true, limitation: "Pendiente" }} label="Ministerio de Salud Pública" preferred={["institution_logo"]} />);
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByText("MSP")).toBeInTheDocument();
    expect(screen.getByText(/Imagen oficial aprobada pendiente/i)).toBeInTheDocument();
  });
});
