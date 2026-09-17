import { AppShell } from "@/components/shell/app-shell";

/** Layout for operator-facing pages: wraps them in the app shell. */
export default function AppGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
