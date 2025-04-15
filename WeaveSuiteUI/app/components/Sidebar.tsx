import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Chat', path: '/chat' },
    { name: 'System Tests', path: '/system-tests' },
  ];

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col h-full">
      <div className="p-4 text-xl font-bold">WeaveSuite</div>
      <nav className="flex-1">
        <ul>
          {navItems.map((item) => (
            <li key={item.path}>
              <Link 
                href={item.path}
                className={`block p-4 hover:bg-gray-700 ${
                  pathname === item.path ? 'bg-gray-700' : ''
                }`}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <div className="p-4 text-sm">© 2025 WeaveSuite</div>
    </div>
  );
}