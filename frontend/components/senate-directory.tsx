import Link from "next/link";

import { senators } from "@/lib/legislators";
import { senatorCompletion } from "@/lib/senator-completion";

function educationLabel(status: string) {
  if (status === "verified") return "Educación verificada";
  if (status === "partial") return "Educación parcial";
  if (status === "not_found") return "Sin formación publicada";
  return "Educación pendiente";
}

export function SenateDirectory() {
  const completedSenators = senators.map((senator) => ({
    ...senator,
    ...senatorCompletion[senator.id],
    photoUrl: senator.photoUrl ?? `/api/senator-photo/${senator.id}`,
  }));

  const verified = completedSenators.filter((senator) => senator.educationStatus === "verified").length;
  const partial = completedSenators.filter((senator) => senator.educationStatus === "partial").length;
  const notFound = completedSenators.filter((senator) => senator.educationStatus === "not_found").length;
  const pending = completedSenators.filter((senator) => senator.educationStatus === "pending").length;
  const withPhoto = completedSenators.filter((senator) => Boolean(senator.photoUrl)).length;

  return (
    <section className="section" id="senadores">
      <div className="shell">
        <p className="eyebrow">Directorio público · período 2024–2028</p>
        <h2>Senadores de la República</h2>
        <p className="lede">Los 32 senadores actuales, su provincia, partido, fotografía oficial y formación académica documentada. Cada tarjeta abre ahora el expediente legislativo individual dentro del OED.</p>

        <div className="grid" aria-label="Cobertura del directorio del Senado">
          <article className="card"><strong className="metric">{completedSenators.length}/32</strong><span>Senadores identificados</span></article>
          <article className="card"><strong className="metric">{verified}</strong><span>Currículos verificados</span></article>
          <article className="card"><strong className="metric">{partial}</strong><span>Currículos parciales</span></article>
          <article className="card"><strong className="metric">{notFound + pending}</strong><span>Sin currículo completo publicado</span></article>
          <article className="card"><strong className="metric">{withPhoto}/32</strong><span>Fotos oficiales conectadas</span></article>
        </div>

        <div className="senator-grid">
          {completedSenators.map((senator) => (
            <article className="senator-card" key={senator.id}>
              <div className="senator-photo" aria-label={`Foto de ${senator.fullName}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={senator.photoUrl} alt={senator.fullName} loading="lazy" />
              </div>
              <div className="senator-body">
                <div className="senator-meta"><span className="badge">{senator.province}</span>{senator.party ? <span>{senator.party}</span> : null}</div>
                <h3><Link href={`/poder-legislativo/senadores/${senator.id}`}>{senator.fullName}</Link></h3>
                <p className={`education-status education-${senator.educationStatus}`}>{educationLabel(senator.educationStatus)}</p>
                {senator.education.length > 0 ? <ul className="education-list">{senator.education.slice(0, 3).map((item,index) => <li key={`${senator.id}-education-${index}`}><strong>{item.credential}</strong>{item.institution ? <> · {item.institution}</> : null}{item.status === "in_progress" ? " · En curso" : null}</li>)}</ul> : <p>{senator.educationNote ?? "Currículo educativo en verificación documental."}</p>}
                <p className="senator-links"><Link className="button" href={`/poder-legislativo/senadores/${senator.id}`}>Ver expediente completo</Link><a href={senator.officialProfileUrl} target="_blank" rel="noreferrer">Fuente oficial</a></p>
              </div>
            </article>
          ))}
        </div>

        <div className="notice"><strong>Cobertura del Senado consolidada.</strong> Los 32 nombres, provincias y fotografías se conectan a fuentes institucionales. Los expedientes individuales incorporan territorio, educación, remuneración, asistencia e iniciativas con trazabilidad documental.</div>
      </div>
    </section>
  );
}
