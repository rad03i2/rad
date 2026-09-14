// Main portfolio interactions + project showcase cards
(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  // Mobile menu
  const menuButton = $('.menu-button');
  const navigation = $('#navigation');
  if (menuButton && navigation) {
    const setMenu = (open) => {
      navigation.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'إغلاق قائمة التنقل' : 'فتح قائمة التنقل');
    };
    menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    $$('#navigation a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menuButton.focus();
      }
    });
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.header-inner')) setMenu(false);
    });
  }

  document.documentElement.classList.add('js');
  const year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());

  // Highlight active navigation section
  const navLinks = $$('#navigation a[href^="#"]');
  const sections = navLinks.map((link) => $(link.getAttribute('href'))).filter(Boolean);
  if (sections.length) {
    let ticking = false;
    const updateCurrentSection = () => {
      const header = $('.site-header');
      const threshold = (header ? header.offsetHeight : 0) + 90;
      let current = sections[0];
      sections.forEach((section) => {
        if (section.getBoundingClientRect().top <= threshold) current = section;
      });
      navLinks.forEach((link) => {
        if (link.getAttribute('href') === `#${current.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateCurrentSection);
      }
    }, { passive: true });
    updateCurrentSection();
  }

  // Subtle code-stream background, if the original site has it
  const stream = $('#codeStream');
  if (stream && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const lines = [
      "import { createServer } from 'http';",
      "const app = createServer((req, res) => {",
      "  res.writeHead(200, { 'Content-Type': 'text/html' });",
      "  res.end(renderPage());",
      "});",
      "npm run build",
      "✓ compiled successfully in 812ms",
      "function debounce(fn, delay = 200) {",
      "  let timer;",
      "  return (...args) => {",
      "    clearTimeout(timer);",
      "    timer = setTimeout(() => fn(...args), delay);",
      "  };",
      "}",
      "git commit -m 'optimize project cards'",
      "✓ project showcase updated",
      "SELECT id, name FROM projects WHERE featured = 1;",
      "→ 20 rows returned in 4ms",
      "const cache = new Map();",
      "deploying to production...",
      "✓ build passed · 0 errors · 0 warnings"
    ];
    const maxLines = Math.max(16, Math.ceil(window.innerHeight / 24) + 4);
    let index = 0;
    const escapeHtml = (text) => text.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    const tokenise = (text) => {
      let html = escapeHtml(text);
      if (html.startsWith('✓')) return `<span class="tok-ok">${html}</span>`;
      if (html.startsWith('→')) return `<span class="tok-arrow">${html}</span>`;
      html = html.replace(/\b(import|from|const|let|function|return|git|commit|npm|run|SELECT|FROM|WHERE)\b/g, '<span class="tok-kw">$1</span>');
      html = html.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-num">$1</span>');
      html = html.replace(/('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")/g, '<span class="tok-str">$1</span>');
      return html;
    };
    const pushLine = () => {
      const el = document.createElement('div');
      el.className = 'cb-line';
      el.innerHTML = tokenise(lines[index % lines.length]);
      index += 1;
      stream.appendChild(el);
      while (stream.children.length > maxLines) stream.removeChild(stream.firstChild);
      window.setTimeout(pushLine, Math.random() * 150 + 120);
    };
    pushLine();
  }
})();

// Project showcase: 20 ordered images, Arabic descriptions, GitHub buttons, and show more.
(() => {
  'use strict';

  const section = document.getElementById('projects');
  if (!section) return;

  if (!document.querySelector('link[href="projects.css"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'projects.css';
    document.head.appendChild(link);
  }

  const projects = [
    ['01', 'Smart File Manager', 'برنامج Windows لإدارة الملفات، إعادة التسمية الجماعية، وفحص التكرار.', ['C#', 'WinUI 3', '.NET'], 'SmartFileManager'],
    ['02', 'Robotics Language Lab', 'مختبر روبوتات متعدد اللغات يجمع التحكم، الملاحة، والحساسات.', ['Python', 'C++', 'ROS 2'], 'robotics-language-lab'],
    ['03', 'Python Toolbox', 'مجموعة أدوات Python عملية للملفات، النصوص، والفحص السريع.', ['Python', 'CLI', 'Automation'], 'python-toolbox'],
    ['04', 'JavaScript Lab', 'تجارب واجهات JavaScript تشمل التخزين المحلي ولوحات بسيطة.', ['JavaScript', 'HTML', 'CSS'], 'javascript-lab'],
    ['05', 'AI Tools Lab', 'أدوات إنتاجية للذكاء الاصطناعي لتنظيف المطالبات وتلخيص النصوص.', ['Python', 'JavaScript', 'AI'], 'ai-tools-lab'],
    ['06', 'Desktop Automation Suite', 'أتمتة أعمال Windows المتكررة عبر اختصارات وسير عمل آمن.', ['PowerShell', 'C#', 'AutoHotkey'], 'desktop-automation-suite'],
    ['07', 'Windows System Toolkit', 'لوحة أدوات لفحص النظام، التخزين، وتنظيف آمن قبل التنفيذ.', ['Windows', 'PowerShell', 'C#'], 'windows-system-toolkit'],
    ['08', 'Arabic UI Components', 'مكونات واجهات عربية RTL جاهزة للنماذج واللوحات المتجاوبة.', ['RTL', 'HTML', 'CSS'], 'arabic-ui-components'],
    ['09', 'Student Management System', 'نموذج نظام تعليمي لإدارة الطلاب والدرجات وقاعدة البيانات.', ['Java', 'SQL', 'OOP'], 'student-management-system'],
    ['10', 'File Processing Toolkit', 'أدوات لمعالجة الملفات: فحص، تجميع، إعادة تسمية، واستخراج.', ['Python', 'C#', 'Bash'], 'file-processing-toolkit'],
    ['11', 'IoT Sensor Dashboard', 'لوحة مراقبة تربط الحساسات بالقياسات ولوحة عرض للمتابعة.', ['Arduino', 'Node.js', 'IoT'], 'iot-sensor-dashboard'],
    ['12', 'Data Analysis Notebooks', 'دفاتر تحليل بيانات بيئية من CSV إلى إحصاءات ورسوم واضحة.', ['Python', 'CSV', 'Analysis'], 'data-analysis-notebooks'],
    ['13', 'Web Security Lab', 'مختبر دفاعي لتعلم مفاهيم أمان الويب والسياسات الوقائية.', ['PHP', 'JavaScript', 'Security'], 'web-security-lab'],
    ['14', 'Mobile App Starter Kit', 'قاعدة بداية لتطبيقات Android وتجارب Python Kivy للهواتف.', ['Kotlin', 'Android', 'Python'], 'mobile-app-starter-kit'],
    ['15', 'C++ Algorithms Lab', 'تطبيقات تدريبية للخوارزميات، البحث، الفرز، وهياكل البيانات.', ['C++', 'CMake', 'Algorithms'], 'cpp-algorithms-lab'],
    ['16', 'Python Automation Hub', 'مركز سكربتات Python لأتمتة الملفات، التقارير، والنسخ الاحتياطي.', ['Python', 'Automation', 'CLI'], 'python-automation-hub'],
    ['17', 'Fullstack Mini Projects', 'تجارب Fullstack صغيرة تربط الواجهة بالخادم وقاعدة البيانات.', ['PHP', 'JavaScript', 'SQL'], 'fullstack-mini-projects'],
    ['18', 'Developer Portfolio', 'موقع شخصي متجاوب يعرض الهوية، المهارات، والمشاريع المختارة.', ['HTML', 'CSS', 'JavaScript'], 'developer-portfolio'],
    ['19', 'Portfolio', 'واجهة شخصية لعرض أعمال الويب والحاسوب والهاتف بصورة مرتبة.', ['HTML', 'CSS', 'JavaScript'], 'portfolio'],
    ['20', 'RAD / Main Portfolio', 'الموقع الرئيسي لعرض الهوية، SINAX، والمشاريع بواجهة ثنائية اللغة.', ['Portfolio', 'Projects', 'RAD'], 'rad']
  ].map(([number, name, description, tags, repo]) => ({
    number,
    name,
    description,
    tags,
    repo,
    github: `https://github.com/rad03i2/${repo}`,
    image: `assets/images/projects/project-${number}.webp`
  }));

  const githubIcon = `
    <svg class="project-github-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path fill="currentColor" d="M12 .5A11.5 11.5 0 0 0 8.36 22.9c.58.11.79-.25.79-.56v-2.02c-3.22.7-3.9-1.38-3.9-1.38-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.04 1.76 2.72 1.25 3.38.96.1-.75.4-1.25.73-1.54-2.57-.29-5.27-1.28-5.27-5.72 0-1.26.45-2.3 1.19-3.11-.12-.29-.52-1.47.11-3.07 0 0 .98-.31 3.18 1.19a11 11 0 0 1 5.8 0c2.2-1.5 3.17-1.19 3.17-1.19.64 1.6.24 2.78.12 3.07.74.81 1.18 1.85 1.18 3.11 0 4.45-2.7 5.43-5.28 5.71.42.36.79 1.07.79 2.16v3.03c0 .31.21.68.8.56A11.5 11.5 0 0 0 12 .5Z"/>
    </svg>`;

  const cards = projects.map((project, index) => `
    <article class="showcase-card ${index >= 10 ? 'is-extra' : ''}">
      <a class="showcase-image-link" href="${project.github}" target="_blank" rel="noopener noreferrer" aria-label="${project.name}">
        <img src="${project.image}" alt="${project.name}" loading="lazy" decoding="async">
        <span class="showcase-number">PROJECT ${project.number}</span>
      </a>
      <div class="showcase-content">
        <div class="showcase-title-row">
          <h3>${project.name}</h3>
          <a class="github-icon-button" href="${project.github}" target="_blank" rel="noopener noreferrer" aria-label="GitHub - ${project.name}">${githubIcon}</a>
        </div>
        <p>${project.description}</p>
        <div class="showcase-tags">${project.tags.map((tag) => `<span>${tag}</span>`).join('')}</div>
        <a class="showcase-github-link" href="${project.github}" target="_blank" rel="noopener noreferrer">${githubIcon}<span>عرض المشروع على GitHub</span></a>
      </div>
    </article>
  `).join('');

  section.classList.add('project-showcase-section');
  section.innerHTML = `
    <div class="container">
      <div class="section-header showcase-header">
        <div>
          <p class="section-label"><span>03 /</span> المشاريع</p>
          <h2 id="projects-title">مشاريع مختارة.<br><em>مرتبة حسب تسلسل الصور.</em></h2>
        </div>
        <p class="section-intro">صور تعريفية احترافية لكل مشروع، مع شرح موجز ورابط مباشر إلى المستودع على GitHub.</p>
      </div>
      <div class="projects-showcase-grid" id="projectsShowcaseGrid">${cards}</div>
      <div class="projects-more-wrap">
        <button class="projects-more-button" id="projectsMoreButton" type="button" aria-expanded="false">
          <span class="projects-more-label">عرض المزيد</span>
          <span class="projects-more-count">+10</span>
        </button>
      </div>
    </div>
  `;

  const grid = document.getElementById('projectsShowcaseGrid');
  const button = document.getElementById('projectsMoreButton');
  if (grid && button) {
    button.addEventListener('click', () => {
      const expanded = grid.classList.toggle('show-all');
      button.setAttribute('aria-expanded', String(expanded));
      button.querySelector('.projects-more-label').textContent = expanded ? 'عرض أقل' : 'عرض المزيد';
      button.querySelector('.projects-more-count').textContent = expanded ? '−10' : '+10';
      if (!expanded) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
