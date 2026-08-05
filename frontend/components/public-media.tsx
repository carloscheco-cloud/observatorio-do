import type { MediaAssetType, PublicMediaAsset, PublicMediaCollection } from "@/types/executive";

const labels: Record<MediaAssetType, string> = {
  institution_building: "Edificio institucional",
  authority_portrait: "Retrato oficial",
  institution_logo: "Identidad visual institucional",
  official_banner: "Imagen institucional oficial",
  fallback: "Representación visual",
};

function initials(label: string) {
  return label
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 3)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function selectPrimaryMedia(collection: PublicMediaCollection, preferred: MediaAssetType[]) {
  for (const type of preferred) {
    const primary = collection.items.find((asset) => asset.asset_type === type && asset.is_primary);
    if (primary) return primary;
    const candidate = collection.items.find((asset) => asset.asset_type === type);
    if (candidate) return candidate;
  }
  return collection.items.find((asset) => asset.is_primary) ?? collection.items[0] ?? null;
}

function Attribution({ asset }: { asset: PublicMediaAsset }) {
  return (
    <figcaption className="media-attribution">
      <strong>{labels[asset.asset_type]}</strong>
      {asset.caption && <span>{asset.caption}</span>}
      <span>
        Fuente: {asset.source_url ? <a href={asset.source_url} rel="noreferrer" target="_blank">{asset.source_name}</a> : asset.source_name}
      </span>
      {asset.license_note && <span>{asset.license_note}</span>}
    </figcaption>
  );
}

export function PublicMedia({ collection, label, preferred, variant = "landscape" }: { collection: PublicMediaCollection; label: string; preferred: MediaAssetType[]; variant?: "landscape" | "portrait" | "logo" }) {
  const asset = selectPrimaryMedia(collection, preferred);
  if (!asset) {
    return (
      <aside className={`media-fallback media-${variant}`} aria-label={`Imagen no disponible para ${label}`}>
        <span aria-hidden="true">{initials(label) || "OED"}</span>
        <p>Imagen oficial aprobada pendiente de incorporación.</p>
      </aside>
    );
  }
  return (
    <figure className={`public-media media-${variant}`}>
      {/* External URLs are accepted only after PE-09 editorial approval and remain fully attributed. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={asset.public_url} alt={asset.alt_text} width={asset.width ?? undefined} height={asset.height ?? undefined} loading="eager" />
      <Attribution asset={asset} />
    </figure>
  );
}

export function MediaGallery({ collection }: { collection: PublicMediaCollection }) {
  if (collection.items.length < 2) return null;
  return (
    <section className="section-block" aria-labelledby="media-gallery-title">
      <h2 id="media-gallery-title">Galería visual documentada</h2>
      <div className="media-gallery">
        {collection.items.map((asset) => (
          <figure className="public-media media-gallery-item" key={asset.id}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={asset.public_url} alt={asset.alt_text} width={asset.width ?? undefined} height={asset.height ?? undefined} loading="lazy" />
            <Attribution asset={asset} />
          </figure>
        ))}
      </div>
      <p className="media-limitation">{collection.limitation}</p>
    </section>
  );
}
