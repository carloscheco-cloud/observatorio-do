const provinceMapFiles: Record<string, string> = {
  "Azua": "Azua in Dominican Republic.svg",
  "Bahoruco": "Baoruco in Dominican Republic.svg",
  "Barahona": "Barahona in Dominican Republic.svg",
  "Dajabón": "Dajabon in Dominican Republic.svg",
  "Distrito Nacional": "Distrito Nacional in Dominican Republic (special marker).svg",
  "Duarte": "Duarte in Dominican Republic.svg",
  "El Seibo": "El Seibo in Dominican Republic.svg",
  "Elías Piña": "Elias Pina in Dominican Republic.svg",
  "Espaillat": "Espaillat in Dominican Republic.svg",
  "Hato Mayor": "Hato Mayor in Dominican Republic.svg",
  "Hermanas Mirabal": "Hermanas Mirabal in Dominican Republic.svg",
  "Independencia": "Independencia in Dominican Republic.svg",
  "La Altagracia": "La Altagracia in Dominican Republic.svg",
  "La Romana": "La Romana in Dominican Republic.svg",
  "La Vega": "La Vega in Dominican Republic.svg",
  "María Trinidad Sánchez": "Maria Trinidad Sanchez in Dominican Republic.svg",
  "Monseñor Nouel": "Monsenor Nouel in Dominican Republic.svg",
  "Monte Cristi": "Monte Cristi in Dominican Republic.svg",
  "Monte Plata": "Monte Plata in Dominican Republic.svg",
  "Pedernales": "Pedernales in Dominican Republic.svg",
  "Peravia": "Peravia in Dominican Republic.svg",
  "Puerto Plata": "Puerto Plata in Dominican Republic.svg",
  "Samaná": "Samana in Dominican Republic.svg",
  "San Cristóbal": "San Cristobal in Dominican Republic.svg",
  "San José de Ocoa": "San Jose de Ocoa in Dominican Republic.svg",
  "San Juan": "San Juan in Dominican Republic.svg",
  "San Pedro de Macorís": "San Pedro de Macoris in Dominican Republic.svg",
  "Sánchez Ramírez": "Sanchez Ramirez in Dominican Republic.svg",
  "Santiago": "Santiago in Dominican Republic.svg",
  "Santiago Rodríguez": "Santiago Rodriguez in Dominican Republic.svg",
  "Santo Domingo": "Santo Domingo in Dominican Republic.svg",
  "Valverde": "Valverde in Dominican Republic.svg",
};

export function provinceLocatorMapUrl(province: string) {
  const filename = provinceMapFiles[province];
  if (!filename) return null;
  return `https://commons.wikimedia.org/wiki/Special:Redirect/file/${encodeURIComponent(filename)}`;
}

export const provinceMapAttributionUrl =
  "https://commons.wikimedia.org/wiki/Category:SVG_locator_maps_of_provinces_in_the_Dominican_Republic_(red_location_map_scheme)";
