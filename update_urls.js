const fs = require('fs');
const path = require('path');

const RENDER_BACKEND_URL = 'https://book-recommender-6cy9.onrender.com';

const filesToUpdate = [
  path.join(__dirname, 'bookmind-repo-fresh', 'components', 'bookmind-app.tsx'),
  path.join(__dirname, 'bookmind-repo-fresh', 'components', 'ui', 'book-cover-image.tsx'),
  path.join(__dirname, 'frontend', 'components', 'bookmind-app.tsx'),
  path.join(__dirname, 'frontend', 'components', 'ui', 'book-cover-image.tsx')
];

for (const file of filesToUpdate) {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    
    // Replace old tunnel and localhost URLs with Render backend URL
    content = content.replace(/https:\/\/fifty-swans-post\.loca\.lt/g, RENDER_BACKEND_URL);
    content = content.replace(/http:\/\/localhost:8000/g, RENDER_BACKEND_URL);
    content = content.replace(/http:\/\/127\.0\.0\.1:8000/g, RENDER_BACKEND_URL);
    
    // Clean up any redundant 'Bypass-Tunnel-Reminder' headers if present
    content = content.replace(/'Bypass-Tunnel-Reminder':\s*'true',\s*/g, '');
    
    fs.writeFileSync(file, content, 'utf8');
    console.log(`Updated ${file}`);
  }
}
