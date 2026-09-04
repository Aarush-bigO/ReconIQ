import type { Metadata } from "next";
import "./globals.css";
import LayoutBody from "@/components/LayoutBody";

export const metadata: Metadata = {
  title: "ReconIQ Enterprise — AI Finance Control Center",
  description:
    "Reconcile payment, settlement, ledger and bank records using probabilistic record linkage. Deterministic systems decide. AI explains.",
  keywords: ["reconciliation", "fintech", "payments", "razorpay", "finance", "AI", "audit"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <LayoutBody>{children}</LayoutBody>
    </html>
  );
}
