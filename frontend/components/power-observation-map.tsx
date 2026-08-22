type Branch = "executive" | "legislative" | "judicial";

type Observation = {
  title: string;
  description: string;
};

const observations: Record<Branch, Observation[]> = {
  executive: [
    { title: "Instituciones y jerarquía", description: "Mapa institucional, dependencias, naturaleza jurídica, funciones y relaciones de subordinación." },
    { title: "Autoridades", description: "Titular actual, foto, cargo, acto de designación, fecha de inicio, trayectoria y evidencia pública." },
    { title: "Presupuesto", description: "Presupuesto aprobado por año, modificaciones y comparación histórica por institución." },
    { title: "Ejecución presupuestaria", description: "Monto ejecutado, porcentaje de ejecución, clasificación del gasto y evolución mensual cuando exista." },
    { title: "Nómina y empleo público", description: "Cantidad de empleados, masa salarial, cargos, remuneraciones públicas y evolución temporal." },
    { title: "Compras y contrataciones", description: "Procesos, adjudicaciones, contratos, proveedores, montos, modalidades, pagos y concentración de proveedores." },
    { title: "Patrimonio, deuda y activos", description: "Activos, pasivos, deuda u obligaciones públicas cuando la naturaleza de la institución lo permita." },
    { title: "Fuentes y nivel de cobertura", description: "Procedencia de cada dato, fecha de actualización, campos faltantes y porcentaje de completitud de la ficha." },
  ],
  legislative: [
    { title: "Congreso y representación territorial", description: "Senado, Cámara de Diputados, provincia o circunscripción representada y mapa territorial." },
    { title: "Legisladores", description: "Foto, cargo, período, biografía, educación, experiencia profesional y trayectoria pública." },
    { title: "Partido e historia política", description: "Partido actual y cambios de afiliación política documentados históricamente." },
    { title: "Declaraciones juradas e intereses", description: "Patrimonio declarado y actividades empresariales públicamente documentadas como información para revisión, sin convertirlas en acusaciones." },
    { title: "Asistencia y trabajo legislativo", description: "Asistencia, comisiones, cargos internos, sesiones y participación registrada." },
    { title: "Iniciativas y leyes", description: "Proyectos presentados, coautorías, estado de tramitación, leyes aprobadas y promulgadas." },
    { title: "Votaciones", description: "Votos nominales cuando estén disponibles y trazabilidad de decisiones legislativas relevantes." },
    { title: "Beneficios y recursos", description: "Salario, asignaciones, dietas, exoneraciones u otros beneficios públicos documentados." },
  ],
  judicial: [
    { title: "Estructura judicial", description: "Suprema Corte, Consejo del Poder Judicial, cortes, tribunales y órganos relacionados." },
    { title: "Jueces y magistrados", description: "Foto, posición actual, órgano, período y ficha pública individual." },
    { title: "Formación y trayectoria", description: "Educación, especialidad, experiencia profesional, cargos anteriores y carrera judicial." },
    { title: "Designación", description: "Mecanismo de selección o designación, fecha, órgano competente y evidencia documental." },
    { title: "Decisiones y sentencias", description: "Decisiones públicas relevantes vinculadas documentalmente al tribunal o magistrado, sin calificaciones personales." },
    { title: "Casos públicos relevantes", description: "Participación institucional en casos de interés público cuando sea jurídicamente apropiado y verificable." },
    { title: "Recursos institucionales", description: "Presupuesto, ejecución, nómina y compras de los órganos judiciales cuando exista información pública trazable." },
    { title: "Fuentes y cobertura", description: "Documento, URL, fecha de consulta, actualización y nivel de completitud de cada ficha." },
  ],
};

const titles: Record<Branch, string> = {
  executive: "Qué observará el OED en el Poder Ejecutivo",
  legislative: "Qué observará el OED en el Poder Legislativo",
  judicial: "Qué observará el OED en el Poder Judicial",
};

export function PowerObservationMap({ branch }: { branch: Branch }) {
  return (
    <section className="shell section">
      <p className="eyebrow">Mapa de observación</p>
      <h2>{titles[branch]}</h2>
      <p className="lede">
        Cada dimensión se irá conectando a datos públicos verificables. El OED mostrará también lo que todavía falta, en lugar de ocultar los vacíos de información.
      </p>
      <div className="grid">
        {observations[branch].map((item) => (
          <article className="card" key={item.title}>
            <p className="eyebrow">Cobertura progresiva</p>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
