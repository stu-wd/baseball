import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Nav } from "@/components/nav";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Baseball Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geist.className} h-full`}>
      <body className="h-full flex bg-gray-900 text-gray-100">
        <Providers>
          <aside className="w-52 shrink-0 bg-gray-800 border-r border-gray-700">
            <Nav />
          </aside>
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
