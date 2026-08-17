import { StateBranchDirectory } from "@/components/state-branch-directory";

export default function LegislativeBranchPage() {
  return (
    <StateBranchDirectory
      branch="legislative"
      title="Poder Legislativo"
      description="Senado, Cámara de Diputados y las instituciones legislativas que el OED vaya incorporando con fuentes públicas trazables."
    />
  );
}
