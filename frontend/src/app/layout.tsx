import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CyberGuard - AI-Powered Cyberbullying Detection',
  description: 'Protect your community with advanced AI-powered cyberbullying detection',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-dark-900 text-white antialiased">
        {children}
      </body>
    </html>
  );
}
