import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { LabsArchive } from "@/components/LabsArchive";
import { loadLabsArchive } from "@/lib/labs.server";

export const metadata: Metadata = {
  title: "Labs · Zion Software Initiative",
};

export default function LabsPage() {
  const archive = loadLabsArchive();

  return (
    <PageShell active="labs">
      <LabsArchive archive={archive} />
    </PageShell>
  );
}
