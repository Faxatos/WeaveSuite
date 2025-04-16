'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();
  
  const isActive = (path: string): string => {
    if (path === '/' && pathname === '/') return 'bg-gray-700';
    if (path === '/tests' && pathname === '/tests') return 'bg-gray-700';
    return '';
  };
  
  return (
    <div className="bg-gray-800 text-white w-64 p-4 h-full">
      <h2 className="text-2xl font-bold mb-6">WeaveSuite</h2>
      <nav className="space-y-2">
        <Link href="/" className={`block p-3 rounded hover:bg-gray-700 ${isActive('/')}`}>
          Microservices Graph
        </Link>
        <Link href="/tests" className={`block p-3 rounded hover:bg-gray-700 ${isActive('/tests')}`}>
          System Tests
        </Link>
      </nav>
    </div>
  );
}