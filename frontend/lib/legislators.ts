export type LegislativeChamber = "senate" | "deputies";
export type EducationStatus = "verified" | "partial" | "not_found" | "pending";

export type EducationRecord = {
  level?: string;
  credential: string;
  institution?: string;
  status?: "completed" | "in_progress" | "incomplete" | "honorary";
  sourceUrl: string;
};

export type Legislator = {
  id: string;
  fullName: string;
  chamber: LegislativeChamber;
  province: string;
  constituency?: string;
  representation?: "provincial" | "national" | "exterior";
  party?: string;
  photoUrl?: string;
  officialProfileUrl: string;
  rosterSourceUrl: string;
  education: EducationRecord[];
  educationStatus: EducationStatus;
  educationNote?: string;
};

// Canonical 2024-2028 Senate roster. Names/provinces are grounded in the
// official Senate certificate-delivery roster. Education/photo fields are
// enriched only when a traceable institutional source has been verified.
export const senators: Legislator[] = [
  ["lia-ynocencia-diaz-santana", "Lía Ynocencia Díaz Santana", "Azua", "PRM"],
  ["andres-guillermo-lama-perez", "Andrés Guillermo Lama Pérez", "Bahoruco", "PRM"],
  ["moises-ayala-perez", "Moisés Ayala Pérez", "Barahona", "PRM"],
  ["manuel-maria-rodriguez-ortega", "Manuel María Rodríguez Ortega", "Dajabón", "PRM"],
  ["omar-leonel-fernandez-dominguez", "Omar Leonel Fernández Domínguez", "Distrito Nacional", "FP"],
  ["franklin-martin-romero-morillo", "Franklin Martín Romero Morillo", "Duarte", "PRM"],
  ["santiago-jose-zorrilla", "Santiago José Zorrilla", "El Seibo", "PRM"],
  ["jonhson-encarnacion-diaz", "Jonhson Encarnación Díaz", "Elías Piña", "PRM"],
  ["carlos-manuel-gomez-urena", "Carlos Manuel Gómez Ureña", "Espaillat", "PRM"],
  ["cristobal-venerado-castillo-liriano", "Cristóbal Venerado Antonio Castillo Liriano", "Hato Mayor", "PRM"],
  ["maria-mercedes-ortiz-dilone", "María Mercedes Ortiz Diloné", "Hermanas Mirabal", "PRM"],
  ["dagoberto-rodriguez-adames", "Dagoberto Rodríguez Adames", "Independencia", "PRM"],
  ["rafael-baron-duluc-rijo", "Rafael Barón Duluc Rijo", "La Altagracia", "PLR"],
  ["eduard-alexis-espiritusanto-castillo", "Eduard Alexis Espiritusanto Castillo", "La Romana", "FP"],
  ["ramon-rogelio-genao-duran", "Ramón Rogelio Genao Durán", "La Vega", "PRSC"],
  ["alexis-victoria-yeb", "Alexis Victoria Yeb", "María Trinidad Sánchez", "PRM"],
  ["hector-elpidio-acosta-restituyo", "Héctor Elpidio Acosta Restituyo", "Monseñor Nouel", "PRM"],
  ["bernardo-aleman-rodriguez", "Bernardo Alemán Rodríguez", "Monte Cristi", "PRM"],
  ["pedro-antonio-tineo-nunez", "Pedro Antonio Tineo Núñez", "Monte Plata", "PRM"],
  ["secundino-velazquez-pimentel", "Secundino Velázquez Pimentel", "Pedernales", "PRM"],
  ["julito-fulcar-encarnacion", "Julito Fulcar Encarnación", "Peravia", "PRM"],
  ["ginnette-altagracia-bournigal", "Ginnette Altagracia Bournigal Socías de Jiménez", "Puerto Plata", "PRM"],
  ["pedro-manuel-catrain-bonilla", "Pedro Manuel Catrain Bonilla", "Samaná", "PRM"],
  ["gustavo-lara-salazar", "Gustavo Lara Salazar", "San Cristóbal", "PRM"],
  ["milciades-aneudy-ortiz-sajiun", "Milcíades Aneudy Ortiz Sajiun", "San José de Ocoa", "PRM"],
  ["felix-ramon-bautista-rosario", "Félix Ramón Bautista Rosario", "San Juan", "FP"],
  ["aracelis-villanueva-figueroa", "Aracelis Villanueva Figueroa", "San Pedro de Macorís", "PRM"],
  ["ricardo-de-los-santos-polanco", "Ricardo De Los Santos Polanco", "Sánchez Ramírez", "PRM"],
  ["daniel-enrique-rivera-reyes", "Daniel Enrique de Jesús Rivera Reyes", "Santiago", "PRM"],
  ["casimiro-antonio-marte-familia", "Casimiro Antonio Marte Familia", "Santiago Rodríguez", "PPG"],
  ["antonio-manuel-taveras-guzman", "Antonio Manuel Taveras Guzmán", "Santo Domingo", "PRM"],
  ["odalis-rafael-rodriguez-rodriguez", "Odalis Rafael Rodríguez Rodríguez", "Valverde", "PRM"],
].map(([id, fullName, province, party]) => ({
  id,
  fullName,
  chamber: "senate" as const,
  province,
  representation: "provincial" as const,
  party,
  officialProfileUrl: "https://www.senadord.gob.do/",
  rosterSourceUrl: "https://www.senadord.gob.do/senadores-reciben-certificados-de-elecciones-de-la-jce/",
  education: [],
  educationStatus: "pending" as const,
  educationNote: "Currículo educativo en verificación documental.",
}));

export const deputies: Legislator[] = [];

export const legislators = [...senators, ...deputies];
