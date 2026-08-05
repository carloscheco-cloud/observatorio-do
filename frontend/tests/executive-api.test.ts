import {afterEach,describe,expect,it,vi} from "vitest";
import {executiveApi,ExecutiveApiError} from "../lib/executive-api";
afterEach(()=>vi.unstubAllGlobals());
describe("cliente público PE-07",()=>{
  it("construye la ruta y devuelve JSON tipado",async()=>{vi.stubEnv("NEXT_PUBLIC_API_BASE_URL","https://api.example.test");const fetchMock=vi.fn().mockResolvedValue(new Response('{"total":25}',{status:200}));vi.stubGlobal("fetch",fetchMock);expect(await executiveApi<{total:number}>("/summary")).toEqual({total:25});expect(fetchMock).toHaveBeenCalledWith("https://api.example.test/api/v1/executive/summary",expect.anything())});
  it.each([[404,"not_found"],[422,"validation"],[503,"unavailable"]] as const)("clasifica HTTP %s",async(status,kind)=>{vi.stubEnv("NEXT_PUBLIC_API_BASE_URL","https://api.example.test");vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response("{}",{status})));await expect(executiveApi("/summary")).rejects.toMatchObject({kind})});
  it("no sustituye una respuesta vacía",async()=>{vi.stubEnv("NEXT_PUBLIC_API_BASE_URL","https://api.example.test");vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response("",{status:200})));await expect(executiveApi("/summary")).rejects.toBeInstanceOf(ExecutiveApiError)});
  it("rechaza una API no configurada",async()=>{vi.stubEnv("NEXT_PUBLIC_API_BASE_URL","");await expect(executiveApi("/summary")).rejects.toMatchObject({kind:"not_configured"})});
});
