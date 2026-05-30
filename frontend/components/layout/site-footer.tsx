import Link from "next/link";
import { Github, Linkedin, Mail, Sparkles } from "lucide-react";

import { env } from "@/lib/env";

const footerLinks = {
  Product: [
    { label: "Features", href: "/#features" },
    { label: "How it works", href: "/#workflow" },
    { label: "Pricing", href: "#" },
  ],
  Company: [
    { label: "About", href: "#" },
    { label: "Blog", href: "#" },
    { label: "Careers", href: "#" },
  ],
  Legal: [
    { label: "Privacy", href: "#" },
    { label: "Terms", href: "#" },
  ],
};

export function SiteFooter() {
  return (
    <footer id="footer" className="border-t border-border/60 bg-card/30">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <Sparkles className="h-5 w-5 text-primary" />
              IntervAI
            </Link>
            <p className="mt-4 max-w-sm text-sm text-muted-foreground">
              {env.appName} — AI-powered interview preparation and evaluation for modern hiring.
            </p>
            <div className="mt-6 flex gap-4 text-muted-foreground">
              <a href="#" aria-label="GitHub" className="hover:text-foreground">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" aria-label="LinkedIn" className="hover:text-foreground">
                <Linkedin className="h-5 w-5" />
              </a>
              <a href="#" aria-label="Email" className="hover:text-foreground">
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-sm font-semibold">{title}</h4>
              <ul className="mt-4 space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border/60 pt-8 text-sm text-muted-foreground md:flex-row">
          <p>
            © {new Date().getFullYear()} {env.appName}. All rights reserved.
          </p>
          <p>Built for candidates who interview with confidence.</p>
        </div>
      </div>
    </footer>
  );
}
