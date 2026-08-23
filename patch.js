const fs = require('fs');
const file = 'bookmind-repo-fresh/components/bookmind-app.tsx';
let content = fs.readFileSync(file, 'utf8');

// Replace fetch('https://...') without headers to fetch('...', { headers: { ... } })
content = content.replace(/fetch\((['"`])https:\/\/fifty-swans-post\.loca\.lt([^'"`]+)(['"`])\)/g, "fetch($1https://fifty-swans-post.loca.lt$2$3, { headers: { 'Bypass-Tunnel-Reminder': 'true' } })");

// For fetches that already have headers, inject our bypass header
content = content.replace(/headers:\s*\{/g, "headers: { 'Bypass-Tunnel-Reminder': 'true', ");

fs.writeFileSync(file, content);
