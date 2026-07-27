import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BurnLens — Evidence before confidence",
  description:
    "A reproducible, baseline-first CV-to-GEOINT wildfire portfolio project with a rejected U-Net preserved as evidence.",
  openGraph: {
    type: "website",
    siteName: "BurnLens",
    title: "BurnLens — Evidence before confidence",
    description:
      "A reproducible, baseline-first CV-to-GEOINT wildfire portfolio project with a rejected U-Net preserved as evidence.",
  },
  twitter: {
    card: "summary",
    title: "BurnLens — Evidence before confidence",
    description:
      "The model failed. The evidence held. Inspect the baseline-first CV-to-GEOINT release.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
