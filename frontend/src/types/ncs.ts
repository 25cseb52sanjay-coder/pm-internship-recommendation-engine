/**
 * National Career Service (NCS) Internship Data Interface
 * Isolated TypeScript interface matching the NCS integration specification.
 */
export interface NCSInternshipRecord {
  source: string; // Default: "NCS"
  title: string;
  company: string;
  location: string;
  skills: string[];
  eligibility: string;
  stipend: string;
  duration: string;
  deadline: string;
  description: string;
  apply_url: string;
  status: "active" | "pending" | "expired";
}
