import { ApiState, date, EvidenceLink, ExecutiveNav } from "@/components/executive";
import { MediaGallery, PublicMedia } from "@/components/public-media";
import { executive, ExecutiveApiError } from "@/lib/executive-api";
import AuthorityNotFound from "./not-found";

export default async function Authority({ params }: { params: Promise<{ id: string }> }) {
  try {
    const id = (await params).id;
    const [a, media] = await Promise.all([executive.authorityDetail(id), executive.authorityMedia(id)]);
    return <div className="shell section">
      <ExecutiveNav />
      <header className="media-hero media-hero-authority">
        <div className="media-hero-copy">
          <p className="eyebrow">Autoridad pública</p>
          <h1>{a.public_name}</h1>
          <p>{a.positions.join(" · ")}</p>
        </div>
        <PublicMedia collection={media} label={a.public_name} preferred={["authority_portrait", "fallback"]} variant="portrait" />
      </header>
      {a.appointments.map(x => <section className="card" key={x.appointment_id}><h2>{x.position}</h2><p>{x.institution.official_name}</p><p>{date(x.start_date)} – {x.end_date ? date(x.end_date) : "Actual"}</p><p>{x.appointment_status} · {x.verification_level}</p>{x.appointment_evidence.map(e => <p key={e.id}><EvidenceLink evidence={e} /></p>)}</section>)}
      <MediaGallery collection={media} />
      {a.limitations.length > 0 && <section className="notice"><h2>Limitaciones</h2><p>{media.limitation}</p><ul>{a.limitations.map(x => <li key={x}>{x}</li>)}</ul></section>}
    </div>;
  } catch (e) {
    if (e instanceof ExecutiveApiError && e.kind === "not_found") return <AuthorityNotFound />;
    return <div className="shell section"><ApiState message={e instanceof Error ? e.message : "API no disponible"} /></div>;
  }
}
