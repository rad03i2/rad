    // JavaScript مضمّن: القائمة المتنقلة وتحديد القسم الحالي وتحديث السنة.
    (() => {
      'use strict';
      const menuButton = document.querySelector('.menu-button');
      const navigation = document.getElementById('navigation');
      const navigationLinks = Array.from(navigation.querySelectorAll('a'));
      const setMenu = open => {
        navigation.classList.toggle('is-open', open);
        menuButton.setAttribute('aria-expanded', String(open));
        menuButton.setAttribute('aria-label', open ? 'إغلاق قائمة التنقل' : 'فتح قائمة التنقل');
      };
      menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
      navigationLinks.forEach(link => link.addEventListener('click', () => {
        const target = document.querySelector(link.getAttribute('href'));
        setMenu(false);
        // انقل تركيز لوحة المفاتيح إلى القسم بدل إبقائه داخل القائمة المخفية.
        if (target) {
          target.setAttribute('tabindex', '-1');
          target.focus({ preventScroll: true });
          target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
        }
      }));
      document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
          setMenu(false);
          menuButton.focus();
        }
      });
      document.addEventListener('click', event => {
        if (!event.target.closest('.header-inner')) setMenu(false);
      });
      const mobileViewport = window.matchMedia('(max-width: 760px)');
      const resetMenu = () => setMenu(false);
      if (mobileViewport.addEventListener) mobileViewport.addEventListener('change', resetMenu);
      document.documentElement.classList.add('js');
      document.getElementById('year').textContent = String(new Date().getFullYear());
      const sections = navigationLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
      let framePending = false;
      const updateCurrentSection = () => {
        let current = sections[0];
        const threshold = document.querySelector('.site-header').offsetHeight + 90;
        for (const section of sections) {
          if (section.getBoundingClientRect().top <= threshold) current = section;
        }
        navigationLinks.forEach(link => {
          if (link.getAttribute('href') === '#' + current.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
        framePending = false;
      };
      window.addEventListener('scroll', () => {
        if (!framePending) {
          framePending = true;
          window.requestAnimationFrame(updateCurrentSection);
        }
      }, { passive: true });
      updateCurrentSection();
    })();
  

    // خلفية أكواد متحركة: زخرفية بالكامل، لا تتفاعل مع الصفحة ولا تُقرأ بواسطة قارئ الشاشة (aria-hidden).
    (() => {
      'use strict';
      const stream = document.getElementById('codeStream');
      if (!stream || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

      const KEYWORDS = ['import','from','const','let','var','function','return','class','constructor','new','this','export','default','extends','if','else','npm','run','git','commit','SELECT','FROM','WHERE','console','log','useState'];
      const lines = [
        "import { createServer } from 'http';",
        "const app = createServer((req, res) => {",
        "  res.writeHead(200, { 'Content-Type': 'text/html' });",
        "  res.end(renderPage());",
        "});",
        "app.listen(3000, () => console.log('server ready'));",
        "npm run build",
        "✓ compiled successfully in 812ms",
        "function debounce(fn, delay = 200) {",
        "  let timer;",
        "  return (...args) => {",
        "    clearTimeout(timer);",
        "    timer = setTimeout(() => fn(...args), delay);",
        "  };",
        "}",
        "class Renderer {",
        "  constructor(root) { this.root = root; }",
        "  paint(state) { this.root.innerHTML = template(state); }",
        "}",
        "git commit -m 'optimize render loop'",
        "✓ 1 file changed, 12 insertions(+), 3 deletions(-)",
        "SELECT id, name FROM users WHERE active = 1;",
        "→ 128 rows returned in 4ms",
        "const cache = new Map();",
        "export default function useTheme() {",
        "  const [dark, setDark] = useState(true);",
        "  return { dark, toggle: () => setDark(d => !d) };",
        "}",
        "deploying to production...",
        "✓ build passed · 0 errors · 0 warnings"
      ];

      function tokenize(text) {
        let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        if (html.startsWith('✓')) return '<span class="tok-ok">' + html + '</span>';
        if (html.startsWith('→')) return '<span class="tok-arrow">' + html + '</span>';
        html = html.replace(/('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")/g, '<span class="tok-str">$&</span>');
        html = html.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-num">$1</span>');
        html = html.replace(new RegExp('\\b(' + KEYWORDS.join('|') + ')\\b', 'g'), '<span class="tok-kw">$1</span>');
        html = html.replace(/\b([a-zA-Z_$][\w$]*)(?=\()/g, '<span class="tok-fn">$1</span>');
        return html;
      }

      const rand = (a, b) => a + Math.random() * (b - a);
      const maxLines = Math.max(16, Math.ceil(window.innerHeight / 24) + 4);
      let index = 0;
      let timerId = null;

      function trimLines() {
        while (stream.children.length > maxLines) stream.removeChild(stream.firstChild);
      }

      function typeChar(el, text, i) {
        el.textContent = text.slice(0, i) + (i < text.length ? '▌' : '');
        if (i < text.length) {
          timerId = setTimeout(() => typeChar(el, text, i + 1), text[i] === ' ' ? 8 : rand(2,7));
        } else {
          el.innerHTML = tokenize(text);
          timerId = setTimeout(nextLine, rand(90, 240));
        }
      }

      function nextLine() {
        const text = lines[index % lines.length];
        index++;
        const el = document.createElement('div');
        el.className = 'cb-line';
        stream.appendChild(el);
        trimLines();
        if (text.startsWith('✓') || text.startsWith('→')) {
          el.innerHTML = tokenize(text);
          el.classList.add('cb-status');
          timerId = setTimeout(nextLine, rand(200, 380));
        } else {
          typeChar(el, text, 0);
        }
      }

      nextLine();
      document.addEventListener('visibilitychange', () => {
        if (document.hidden && timerId) { clearTimeout(timerId); timerId = null; }
        else if (!document.hidden && !timerId) { timerId = setTimeout(nextLine, 200); }
      });
    })();
  
