import { senators } from "@/lib/legislators";

function educationLabel(status: string) {
  if (status === "verified") return "Educación verificada";
  if (status === "partial") return "Educación parcial";
  if (status === "not_found") return "Sin formación publicada";
  return "Educación pendiente";
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function SenateDirectory() {
  const verified = senators.filter((senator) => senator.educationStatus === "verified").length;
  const partial = senators.filter((senator) => senator.educationStatus === "partial").length;
  const notFound = senators.filter((senator) => senator.educationStatus === "not_found").length;
  const pending = senators.filter((senator) => senator.educationStatus === "pending").length;
  const withPhoto = senators.filter((senator) => Boolean(senator.photoUrl)).length;

  return (
    <section className="section" id="senadores">
      <div className="shell">
        <p className="eyebrow">Directorio público · período 2024–2028</p>
        <h2>Senadores de la República</h2>
        <p className="lede">
          Los 32 senadores actuales, su provincia, partido y formación académica documentada. El OED
          diferencia entre datos verificados, información parcial y campos aún pendientes para no
          presentar como cierto lo que una fuente pública no respalda.
        </p>

        <div className="grid" aria-label="Cobertura del directorio del Senado">
          <article className="card"><strong className="metric">{senators.length}/32</strong><span>Senadores identificados</span></article>
          <article className="card"><strong className="metric">{verified}</strong><span>Currículos verificados</span></article>
          <article className="card"><strong className="metric">{partial}</strong><span>Currículos parciales</span></article>
          <article className="card"><strong className="metric">{notFound + pending}</strong><span>Sin currículo completo publicado</span></article>
          <article className="card"><strong className="metric">{withPhoto}/32</strong><span>Fotos ya conectadas al OED</span></article>
        </div>

        <div className="senator-grid">
          {senators.map((senator) => (
            <article className="senator-card" key={senator.id}>
              <div className="senator-photo" aria-label={`Foto de ${senator.fullName}`}>
                {senator.photoUrl ? (
                  // Official institutional image URL. Native img avoids coupling the public directory
                  // to a changing set of remote image host allow-lists while provenance is preserved.
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={senator.photoUrl} alt={senator.fullName} loading="lazy" />
                ) : (
                  <span aria-hidden="true">{initials(senator.fullName)}</span>
                )}
              </div>

              <div className="senator-body">
                <div className="senator-meta">
                  <span className="badge">{senator.province}</span>
                  {senator.party ? <span>{senator.party}</span> : null}
                </div>
                <h3>{senator.fullName}</h3>
                <p className={`education-status education-${senator.educationStatus}`}>
                  {educationLabel(senator.educationStatus)}
                </p>

                {senator.education.length > 0 ? (
                  <ul className="education-list">
                    {senator.education.map((item, index) => (
                      <li key={`${senator.id}-education-${index}`}>
                        <strong>{item.credential}</strong>
                        {item.institution ? <> · {item.institution}</> : null}
                        {item.status === "in_progress" ? " · En curso" : null}
                        {item.status === "incomplete" ? " · No concluido" : null}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>{senator.educationNote ?? "Currículo educativo en verificación documental."}</p>
                )}

                {senator.educationNote && senator.education.length > 0 ? (
                  <p className="senator-note">{senator.educationNote}</p>
                ) : null}

                <p className="senator-links">
                  <a href={senator.officialProfileUrl} target="_blank" rel="noreferrer">Fuente del perfil</a>
                  <a href={senator.rosterSourceUrl} target="_blank" rel="noreferrer">Fuente del roster</a>
                </p>
              </div>
            </article>
          ))}
        </div>

        <div className="notice">
          <strong>Cobertura en progreso.</strong> Los nombres y provincias cubren el Senado completo.
          Las fotografías y currículos se enriquecen solamente con fuentes trazables; los faltantes se
          muestran explícitamente en lugar de inferirse.
        </div>
      </div>
    </section>
  );
}
