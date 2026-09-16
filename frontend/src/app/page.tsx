import { redirect } from "next/navigation";

/**
 * Root route. AegisOps opens on the incident dashboard, so redirect there.
 */
export default function HomePage() {
  redirect("/incidents");
}
