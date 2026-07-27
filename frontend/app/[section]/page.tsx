import type { Metadata } from "next";
import Link from "next/link";
import { EmptyState, ExportButton, MethodologyNotice } from "@/components/ui";
const sections: Record<string,{title:string;description:string}> = {
  instituciones:{title:"Instituciones",description:"Directorio de instituciones confirmadas y respaldadas por evidencia."},
  personas:{title:"Personas públicas",description:"Trayectorias públicas vinculadas a cargos y designaciones."},
  territorios:{title:"Territorios",description:"Consulta territorial de instituciones, cobertura e indicadores."},
  nomina:{title:"Nómina pública",description:"Empleo observado y masa salarial por períodos compatibles."},
  presupuesto:{title:"Presupuesto",description:"Apropiación, vigencia y ejecución con trazabilidad."},
  compras:{title:"Compras públicas",description:"Procesos, contratos, pagos y proveedores."},
  contratos:{title:"Contratos",description:"Contratos públicos revisados y sus cambios históricos."},
  proveedores:{title:"Proveedores",description:"Proveedores canónicos sin identificadores registrales sensibles."},
  deuda:{title:"Deuda pública",description:"Instrumentos, servicio y evolución de obligaciones públicas."},
  patrimonio:{title:"Patrimonio público",description:"Activos públicos sin seriales ni ubicaciones restringidas."},
  alertas:{title:"Alertas públicas",description:"Señales observables publicadas tras revisión humana."},
  comparar:{title:"Comparar",description:"Compara entidades, períodos e indicadores compatibles."},
  fuentes:{title:"Fuentes",description:"Procedencia, frescura, cobertura y calidad de los datos."},
  metodologia:{title:"Metodología",description:"Cómo adquirimos, revisamos, publicamos y explicamos los datos."},
  acerca:{title:"Acerca del Observatorio",description:"Una iniciativa independiente para facilitar la consulta ciudadana."}
};
export async function generateMetadata({params}:{params:Promise<{section:string}>}):Promise<Metadata>{const {section}=await params;return {title:sections[section]?.title ?? "Consulta"}}
export default async function Section({params}:{params:Promise<{section:string}>}) { const {section}=await params; const item=sections[section]; if(!item) return <div className="shell section"><EmptyState title="Página no encontrada"/></div>; return <div className="shell section"><p className="eyebrow">Consulta pública</p><h1>{item.title}</h1><p className="lede">{item.description}</p>{["instituciones","nomina","presupuesto","compras","contratos","proveedores","deuda","patrimonio","alertas"].includes(section)&&<ExportButton resource={section==="alertas"?"findings":"institutions"}/>}<MethodologyNotice/><EmptyState title="Sin resultados para los filtros actuales">Conecta el backend y selecciona filtros para consultar datos públicos. La ausencia no representa cero.</EmptyState><p><Link href="/buscar">Ir al buscador global</Link></p></div> }
