/**
 * Footer Component
 *
 * Bottom footer with system info and links.
 *
 * Version: 8.0.0
 * Week: 7 Day 1
 */

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-gray-50 mt-auto">
      <div className="container mx-auto px-8 py-6">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            <span className="font-medium">SPEK Atlantis</span>
            <span className="mx-2">•</span>
            <span>v8.0.0</span>
            <span className="mx-2">•</span>
            <span>Week 7 Day 1</span>
          </div>

          <div className="flex items-center gap-6">
            <a
              href="https://github.com/yourusername/spek-v2"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors"
            >
              GitHub
            </a>
            <a
              href="/help"
              className="hover:text-blue-600 transition-colors"
            >
              Documentation
            </a>
            <span>© {currentYear} SPEK Platform</span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-4 gap-4 text-xs text-gray-500">
            <div>
              <span className="font-medium">Backend:</span> Ready
            </div>
            <div>
              <span className="font-medium">WebSocket:</span> Connected
            </div>
            <div>
              <span className="font-medium">Agents:</span> 22/22
            </div>
            <div>
              <span className="font-medium">Status:</span> Operational
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
