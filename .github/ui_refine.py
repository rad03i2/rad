from pathlib import Path
import re

# 1) Keep the animated code background, but make it more subdued so the UI stays dominant.
styles = Path('styles.css')
s = styles.read_text(encoding='utf-8')
old_bg = ".code-bg{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;user-select:none;opacity:.55;filter:blur(.7px);-webkit-mask-image:linear-gradient(to bottom,transparent,#000 10%,#000 88%,transparent);mask-image:linear-gradient(to bottom,transparent,#000 10%,#000 88%,transparent)}"
new_bg = ".code-bg{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;user-select:none;opacity:.38;filter:blur(.75px) brightness(.78);-webkit-mask-image:linear-gradient(to bottom,transparent,#000 10%,#000 88%,transparent);mask-image:linear-gradient(to bottom,transparent,#000 10%,#000 88%,transparent)}"
if old_bg not in s:
    raise SystemExit('code background rule not found')
s = s.replace(old_bg, new_bg, 1)

old_mobile = "@media(max-width:760px){.code-bg{opacity:.4}}"
new_mobile = "@media(max-width:760px){.code-bg{opacity:.30;filter:blur(.7px) brightness(.78)}}"
if old_mobile not in s:
    raise SystemExit('mobile code background rule not found')
s = s.replace(old_mobile, new_mobile, 1)
styles.write_text(s, encoding='utf-8')

# 2) Replace the static textual technology ticker in the initial HTML with an icon-only ticker shell.
index = Path('index.html')
h = index.read_text(encoding='utf-8')
pattern = r'<div class="enh-tech-strip enh-reveal"><div class="enh-tech-track">.*?</div></div>'
replacement = '<div class="enh-tech-strip enh-reveal" aria-label="Programming languages and technologies"><div class="enh-tech-track" id="programmingIconTicker" aria-hidden="true"></div></div>'
h, n = re.subn(pattern, replacement, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'ticker replacement expected 1, found {n}')
index.write_text(h, encoding='utf-8')

# 3) Build a large, lightweight icon ticker from Devicon's single icon font/CSS asset.
js = Path('enhancements.js')
j = js.read_text(encoding='utf-8')
marker = "  const consultationUrl = `${calendlyConsultation}?utm_source=rdwan.dev&utm_medium=website&utm_campaign=project_consultation`;\n"
tech_line = '''  const techIcons = [["aarch64","AArch64"],["apl","APL"],["arduino","Arduino"],["awk","AWK"],["bash","Bash"],["c","C"],["cairo","Cairo"],["ceylon","Ceylon"],["clojure","Clojure"],["coffeescript","CoffeeScript"],["cplusplus","C++"],["crystal","Crystal"],["csharp","C#"],["dart","Dart"],["elixir","Elixir"],["elm","Elm"],["embeddedc","Embedded C"],["erlang","Erlang"],["fortran","Fortran"],["fsharp","F#"],["go","Go"],["groovy","Groovy"],["haskell","Haskell"],["haxe","Haxe"],["java","Java"],["javascript","JavaScript"],["jule","Jule"],["julia","Julia"],["kotlin","Kotlin"],["labview","LabVIEW"],["latex","LaTeX"],["lua","Lua"],["matlab","MATLAB"],["nim","Nim"],["objectivec","Objective-C"],["ocaml","OCaml"],["perl","Perl"],["php","PHP"],["powershell","PowerShell"],["r","R"],["ruby","Ruby"],["rust","Rust"],["scala","Scala"],["solidity","Solidity"],["swift","Swift"],["typescript","TypeScript"],["vala","Vala"],["visualbasic","Visual Basic"],["vyper","Vyper"],["wasm","WebAssembly"],["zig","Zig"],["html5","HTML5"],["css3","CSS3"],["sass","Sass"],["less","Less"],["markdown","Markdown"],["json","JSON"],["nodejs","Node.js"],["denojs","Deno"],["bun","Bun"],["react","React"],["vuejs","Vue.js"],["angular","Angular"],["svelte","Svelte"],["nextjs","Next.js"],["nuxtjs","Nuxt"],["django","Django"],["flask","Flask"],["fastapi","FastAPI"],["laravel","Laravel"],["rails","Ruby on Rails"],["spring","Spring"],["dotnetcore",".NET Core"],["flutter","Flutter"],["electron","Electron"],["qt","Qt"],["tensorflow","TensorFlow"],["pytorch","PyTorch"],["opencv","OpenCV"],["mysql","MySQL"],["postgresql","PostgreSQL"],["mongodb","MongoDB"],["sqlite","SQLite"],["redis","Redis"],["mariadb","MariaDB"],["microsoftsqlserver","SQL Server"],["oracle","Oracle"],["cassandra","Cassandra"],["neo4j","Neo4j"],["firebase","Firebase"],["supabase","Supabase"],["docker","Docker"],["kubernetes","Kubernetes"],["git","Git"],["github","GitHub"],["gitlab","GitLab"],["npm","npm"],["yarn","Yarn"],["pnpm","pnpm"],["vitejs","Vite"],["webpack","Webpack"],["cmake","CMake"],["gradle","Gradle"],["maven","Maven"],["terraform","Terraform"],["ansible","Ansible"],["jenkins","Jenkins"],["githubactions","GitHub Actions"],["linux","Linux"],["android","Android"]];\n'''
if 'const techIcons = ' not in j:
    if marker not in j:
        raise SystemExit('tech icon insertion marker missing')
    j = j.replace(marker, marker + tech_line, 1)

hydrate = r'''
  function hydrateTechIconTicker() {
    const track = $('#programmingIconTicker') || $('.enh-tech-track');
    if (!track || track.dataset.iconsReady === '1') return;

    if (!document.querySelector('link[data-devicon]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdn.jsdelivr.net/npm/devicon@2.17.0/devicon.min.css';
      link.dataset.devicon = '2.17.0';
      document.head.appendChild(link);
    }

    const icons = techIcons.map(([slug,label]) =>
      `<span class="enh-tech-icon" title="${label}"><i class="devicon-${slug}-plain devicon-${slug}-original colored"></i></span>`
    ).join('');

    track.innerHTML = `<div class="enh-tech-sequence">${icons}</div><div class="enh-tech-sequence" aria-hidden="true">${icons}</div>`;
    track.dataset.iconsReady = '1';
  }

'''
if 'function hydrateTechIconTicker()' not in j:
    needle = '  function addStatsAndTicker() {'
    if needle not in j:
        raise SystemExit('addStatsAndTicker marker missing')
    j = j.replace(needle, hydrate + needle, 1)

old_fallback_ticker = """    const tech = document.createElement('div'); tech.className = 'enh-tech-strip enh-reveal';
    const names = ['Python','C#','.NET','JavaScript','HTML','CSS','Git','GitHub','PowerShell','C++','SQL','Android','Kotlin','PHP','Automation','IoT'];
    tech.innerHTML = `<div class=\"enh-tech-track\">${[...names,...names].map(x=>`<span class=\"enh-tech-chip\">${x}</span>`).join('')}</div>`;
    stats.insertAdjacentElement('afterend', tech);"""
new_fallback_ticker = """    const tech = document.createElement('div'); tech.className = 'enh-tech-strip enh-reveal'; tech.setAttribute('aria-label','Programming languages and technologies');
    tech.innerHTML = '<div class=\"enh-tech-track\" id=\"programmingIconTicker\" aria-hidden=\"true\"></div>';
    stats.insertAdjacentElement('afterend', tech);
    hydrateTechIconTicker();"""
if old_fallback_ticker in j:
    j = j.replace(old_fallback_ticker, new_fallback_ticker, 1)

# 4) Remove the Tools / Areas / Timeline section from startup entirely.
old_tasks = "const tasks=[addStatsAndTicker,addFeaturedSinax,addServices,addProcess,addToolsAreasTimeline,addServiceComparison,"
new_tasks = "const tasks=[hydrateTechIconTicker,addStatsAndTicker,addFeaturedSinax,addServices,addProcess,addServiceComparison,"
if old_tasks not in j:
    raise SystemExit('task list marker missing')
j = j.replace(old_tasks, new_tasks, 1)

# Preserve the useful service comparison section even though its previous anchor is removed.
old_compare_head = "  function addServiceComparison() {\n    const tools=$('#enhToolsAreas'); if(!tools || $('#enhCompare')) return;"
new_compare_head = "  function addServiceComparison() {\n    const tools=$('#enhToolsAreas'); const projectsSection=$('#projects'); if((!tools && !projectsSection) || $('#enhCompare')) return;"
if old_compare_head not in j:
    raise SystemExit('comparison header marker missing')
j = j.replace(old_compare_head, new_compare_head, 1)

old_compare_insert = "    tools.insertAdjacentElement('afterend',sec);"
new_compare_insert = "    if (tools) tools.insertAdjacentElement('afterend',sec); else projectsSection.insertAdjacentElement('beforebegin',sec);"
if old_compare_insert not in j:
    raise SystemExit('comparison insert marker missing')
j = j.replace(old_compare_insert, new_compare_insert, 1)
js.write_text(j, encoding='utf-8')

# 5) Compact, polished icon ticker styling. No visible names, no oversized assets.
css = Path('enhancements.css')
c = css.read_text(encoding='utf-8')
if '/* programming-icon-ticker-v1 */' not in c:
    c += r'''

/* programming-icon-ticker-v1 */
.enh-tech-strip{position:relative;direction:ltr;overflow:hidden;border-block:1px solid var(--enh-line);background:rgba(255,255,255,.012);-webkit-mask-image:linear-gradient(to right,transparent 0,#000 4%,#000 96%,transparent 100%);mask-image:linear-gradient(to right,transparent 0,#000 4%,#000 96%,transparent 100%)}
.enh-tech-track{display:flex;width:max-content;gap:0;padding:9px 0;animation:enhTicker 64s linear infinite;will-change:transform;direction:ltr}
.enh-tech-sequence{display:flex;align-items:center;gap:9px;padding-inline-end:9px;flex:none}
.enh-tech-icon{width:31px;height:31px;display:grid;place-items:center;flex:0 0 31px;border:1px solid rgba(255,255,255,.075);border-radius:10px;background:rgba(255,255,255,.035);box-shadow:inset 0 1px 0 rgba(255,255,255,.025);transition:transform .18s ease,border-color .18s ease,background .18s ease}
.enh-tech-icon i{display:block;font-size:18px;line-height:1;filter:saturate(.92) brightness(1.07);transform:translateZ(0)}
.enh-tech-icon:hover{transform:translateY(-1px);border-color:rgba(198,241,108,.25);background:rgba(198,241,108,.045)}
.enh-tech-icon .devicon-github-plain,.enh-tech-icon .devicon-github-original,.enh-tech-icon .devicon-nextjs-plain,.enh-tech-icon .devicon-nextjs-original,.enh-tech-icon .devicon-bash-plain,.enh-tech-icon .devicon-bash-original,.enh-tech-icon .devicon-linux-plain,.enh-tech-icon .devicon-linux-original{color:#d9dfd4!important}
@media(max-width:640px){.enh-tech-track{padding:8px 0;animation-duration:54s}.enh-tech-sequence{gap:8px;padding-inline-end:8px}.enh-tech-icon{width:29px;height:29px;flex-basis:29px;border-radius:9px}.enh-tech-icon i{font-size:17px}}
'''
css.write_text(c, encoding='utf-8')

# 6) Force visitors off the previous cached assets after deployment.
sw = Path('service-worker.js')
w = sw.read_text(encoding='utf-8')
if "rad-portfolio-v3.10.0" not in w:
    raise SystemExit('unexpected service worker version')
sw.write_text(w.replace("rad-portfolio-v3.10.0", "rad-portfolio-v3.11.0", 1), encoding='utf-8')
