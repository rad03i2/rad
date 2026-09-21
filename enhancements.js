(() => {
  'use strict';

  const VERSION = '3.0.0';
  const OWNER = 'rad03i2';
  const githubBase = `https://github.com/${OWNER}/`;
  const instagram = 'https://www.instagram.com/rad_03i';
  const facebook = 'https://www.facebook.com/rad03e';
  const tallyProjectForm = 'https://tally.so/r/RGAekK';
  const calendlyConsultation = 'https://calendly.com/rdwanbdalhady33/30min';
  const omnisendUpdates = 'https://omniform1.com/forms/v1/landingPage/6aa951449b0f973742e3f90d/6aa9b7a1f85082d5ccd3f79c';
  const projectRequestUrl = `${tallyProjectForm}?utm_source=rdwan.dev&utm_medium=website&utm_campaign=project_request`;
  const consultationUrl = `${calendlyConsultation}?utm_source=rdwan.dev&utm_medium=website&utm_campaign=project_consultation`;
  const techIcons = [["aarch64","AArch64"],["apl","APL"],["arduino","Arduino"],["awk","AWK"],["bash","Bash"],["c","C"],["cairo","Cairo"],["ceylon","Ceylon"],["clojure","Clojure"],["coffeescript","CoffeeScript"],["cplusplus","C++"],["crystal","Crystal"],["csharp","C#"],["dart","Dart"],["elixir","Elixir"],["elm","Elm"],["embeddedc","Embedded C"],["erlang","Erlang"],["fortran","Fortran"],["fsharp","F#"],["go","Go"],["groovy","Groovy"],["haskell","Haskell"],["haxe","Haxe"],["java","Java"],["javascript","JavaScript"],["jule","Jule"],["julia","Julia"],["kotlin","Kotlin"],["labview","LabVIEW"],["latex","LaTeX"],["lua","Lua"],["matlab","MATLAB"],["nim","Nim"],["objectivec","Objective-C"],["ocaml","OCaml"],["perl","Perl"],["php","PHP"],["powershell","PowerShell"],["r","R"],["ruby","Ruby"],["rust","Rust"],["scala","Scala"],["solidity","Solidity"],["swift","Swift"],["typescript","TypeScript"],["vala","Vala"],["visualbasic","Visual Basic"],["vyper","Vyper"],["wasm","WebAssembly"],["zig","Zig"],["html5","HTML5"],["css3","CSS3"],["sass","Sass"],["less","Less"],["markdown","Markdown"],["json","JSON"],["nodejs","Node.js"],["denojs","Deno"],["bun","Bun"],["react","React"],["vuejs","Vue.js"],["angular","Angular"],["svelte","Svelte"],["nextjs","Next.js"],["nuxtjs","Nuxt"],["django","Django"],["flask","Flask"],["fastapi","FastAPI"],["laravel","Laravel"],["rails","Ruby on Rails"],["spring","Spring"],["dotnetcore",".NET Core"],["flutter","Flutter"],["electron","Electron"],["qt","Qt"],["tensorflow","TensorFlow"],["pytorch","PyTorch"],["opencv","OpenCV"],["mysql","MySQL"],["postgresql","PostgreSQL"],["mongodb","MongoDB"],["sqlite","SQLite"],["redis","Redis"],["mariadb","MariaDB"],["microsoftsqlserver","SQL Server"],["oracle","Oracle"],["cassandra","Cassandra"],["neo4j","Neo4j"],["firebase","Firebase"],["supabase","Supabase"],["docker","Docker"],["kubernetes","Kubernetes"],["git","Git"],["github","GitHub"],["gitlab","GitLab"],["npm","npm"],["yarn","Yarn"],["pnpm","pnpm"],["vitejs","Vite"],["webpack","Webpack"],["cmake","CMake"],["gradle","Gradle"],["maven","Maven"],["terraform","Terraform"],["ansible","Ansible"],["jenkins","Jenkins"],["githubactions","GitHub Actions"],["linux","Linux"],["android","Android"]];
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const store = {
    get(k, f = null) { try { return localStorage.getItem(k) ?? f; } catch { return f; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} }
  };

  const projects = [
    {n:'01',name:'Smart File Manager',repo:'SmartFileManager',cats:['windows','tools'],tags:['C#','WinUI 3','.NET'],ar:'برنامج Windows لإدارة الملفات وإعادة التسمية الجماعية وفحص التكرار.',en:'A Windows file-management utility focused on batch renaming, previews and duplicate detection.',problemAr:'تنظيم الملفات بكميات كبيرة قد يصبح بطيئًا وعرضة للأخطاء اليدوية.',solutionAr:'واجهة مكتبية تجمع المعاينة وإعادة التسمية الجماعية وأدوات التحقق في مسار واحد.',problemEn:'Managing large batches of files can be slow and error-prone.',solutionEn:'A desktop workflow combining preview, batch renaming and verification tools.'},
    {n:'02',name:'Robotics Language Lab',repo:'robotics-language-lab',cats:['robotics','tools'],tags:['Python','C++','ROS 2'],ar:'مختبر برمجي لتجارب الروبوتات والتحكم والحساسات باستخدام أكثر من لغة.',en:'A multi-language robotics lab for control, sensors and ROS-oriented experiments.',problemAr:'تعلم الروبوتات يحتاج أمثلة مترابطة بين لغات وأدوات مختلفة.',solutionAr:'مختبر موحد يجمع أمثلة وتجارب صغيرة يمكن تطويرها تدريجيًا.',problemEn:'Robotics learning often spans several languages and tools.',solutionEn:'A single lab that groups small, extensible robotics experiments.'},
    {n:'03',name:'Python Toolbox',repo:'python-toolbox',cats:['python','tools'],tags:['Python','CLI','Automation'],ar:'مجموعة أدوات Python للملفات والنصوص والمهام اليومية السريعة.',en:'A practical Python toolbox for files, text and quick automation tasks.',problemAr:'المهام الصغيرة المتكررة تستهلك وقتًا عندما تُنفذ يدويًا.',solutionAr:'أدوات CLI صغيرة قابلة لإعادة الاستخدام لتسريع العمل اليومي.',problemEn:'Small repetitive tasks consume time when handled manually.',solutionEn:'Reusable CLI utilities that automate common day-to-day work.'},
    {n:'04',name:'JavaScript Lab',repo:'javascript-lab',cats:['web'],tags:['JavaScript','HTML','CSS'],ar:'تجارب JavaScript وواجهات ويب صغيرة تركز على التفاعل والتخزين المحلي.',en:'A JavaScript lab for UI interaction, local storage and small web experiments.',problemAr:'تجربة أفكار الواجهة تحتاج مساحة بسيطة وسريعة دون مشروع ضخم.',solutionAr:'مجموعة تجارب مستقلة يمكن اختبارها وتطويرها بسرعة.',problemEn:'UI ideas benefit from a lightweight place to experiment.',solutionEn:'Independent, focused experiments that are easy to test and extend.'},
    {n:'05',name:'AI Tools Lab',repo:'ai-tools-lab',cats:['ai','python','web'],tags:['Python','JavaScript','AI'],ar:'أدوات وتجارب إنتاجية مرتبطة بالذكاء الاصطناعي ومعالجة النصوص.',en:'Productivity experiments around AI-assisted workflows and text processing.',problemAr:'استخدام أدوات الذكاء الاصطناعي بشكل يدوي قد يكرر نفس الخطوات.',solutionAr:'أدوات صغيرة تنظّم خطوات الإدخال والمعالجة والنتيجة.',problemEn:'Manual AI workflows often repeat the same steps.',solutionEn:'Small utilities that structure input, processing and output.'},
    {n:'06',name:'Desktop Automation Suite',repo:'desktop-automation-suite',cats:['windows','automation','tools'],tags:['PowerShell','C#','AutoHotkey'],ar:'مجموعة أتمتة لأعمال Windows المتكررة والاختصارات وسير العمل.',en:'A desktop automation suite for recurring Windows tasks and keyboard-driven workflows.',problemAr:'الخطوات المتكررة على Windows تستهلك وقتًا وتشتت التركيز.',solutionAr:'اختصارات وسكربتات وأدوات مخصصة لتقليل عدد الخطوات اليدوية.',problemEn:'Repeated Windows actions waste time and attention.',solutionEn:'Shortcuts, scripts and utilities that reduce manual steps.'},
    {n:'07',name:'Windows System Toolkit',repo:'windows-system-toolkit',cats:['windows','tools'],tags:['Windows','PowerShell','C#'],ar:'أدوات لفحص النظام والتخزين وتنفيذ مهام صيانة آمنة.',en:'A Windows toolkit for system inspection, storage visibility and safe maintenance tasks.',problemAr:'معلومات النظام موزعة بين نوافذ وأدوات متعددة.',solutionAr:'لوحة أدوات تجمع أهم عمليات الفحص في مكان واحد.',problemEn:'System information is spread across many Windows tools.',solutionEn:'A unified toolkit for common inspection and maintenance tasks.'},
    {n:'08',name:'Arabic UI Components',repo:'arabic-ui-components',cats:['web'],tags:['RTL','HTML','CSS'],ar:'مكونات واجهات عربية RTL قابلة لإعادة الاستخدام في المواقع واللوحات.',en:'Reusable RTL interface components for Arabic websites and dashboards.',problemAr:'التعامل مع RTL يتطلب تفاصيل محاذاة واتجاه متكررة.',solutionAr:'مكونات جاهزة تقلل إعادة بناء الأنماط العربية من الصفر.',problemEn:'RTL interfaces repeatedly require direction and alignment adjustments.',solutionEn:'Reusable components that make Arabic-first interfaces faster to build.'},
    {n:'09',name:'Student Management System',repo:'student-management-system',cats:['desktop','data'],tags:['Java','SQL','OOP'],ar:'نموذج نظام لإدارة بيانات الطلاب والدرجات وقاعدة البيانات.',en:'A student-management sample covering records, grades and database-backed workflows.',problemAr:'بيانات الطلاب تحتاج هيكلة واضحة بدل الملفات المبعثرة.',solutionAr:'نموذج نظام يجمع السجلات والدرجات في بنية موحدة.',problemEn:'Student records need structure instead of scattered files.',solutionEn:'A simple system model that organizes records and grades.'},
    {n:'10',name:'File Processing Toolkit',repo:'file-processing-toolkit',cats:['python','tools','automation'],tags:['Python','C#','Bash'],ar:'أدوات لمعالجة الملفات وتجميعها وإعادة تسميتها واستخراج المعلومات منها.',en:'Utilities for file processing, grouping, renaming and information extraction.',problemAr:'عمليات الملفات الجماعية تختلف حسب النوع والمجلد.',solutionAr:'مجموعة أدوات مرنة لمعالجة سيناريوهات متنوعة.',problemEn:'Batch file operations vary across formats and folders.',solutionEn:'A flexible toolkit for multiple processing scenarios.'},
    {n:'11',name:'IoT Sensor Dashboard',repo:'iot-sensor-dashboard',cats:['iot','web','data'],tags:['Arduino','Node.js','IoT'],ar:'لوحة عرض لقراءات الحساسات والقياسات المرتبطة بمشاريع إنترنت الأشياء.',en:'An IoT dashboard concept for sensor readings and device-oriented monitoring.',problemAr:'قراءات الحساسات تحتاج عرضًا واضحًا بدل الأرقام الخام.',solutionAr:'واجهة تلخص القياسات وتعرضها بشكل قابل للمتابعة.',problemEn:'Sensor readings are easier to understand in a visual dashboard.',solutionEn:'A monitoring interface that presents readings in a clearer way.'},
    {n:'12',name:'Data Analysis Notebooks',repo:'data-analysis-notebooks',cats:['data','python'],tags:['Python','CSV','Analysis'],ar:'دفاتر تحليل بيانات تشمل الاستكشاف والإحصاءات والرسوم.',en:'Data-analysis notebooks for exploration, statistics and clear visual summaries.',problemAr:'البيانات الخام لا توضح الأنماط بمفردها.',solutionAr:'دفاتر تحليل قابلة للتكرار تنتقل من CSV إلى نتائج ورسوم.',problemEn:'Raw data does not reveal patterns by itself.',solutionEn:'Repeatable notebooks that turn CSV data into analysis and visuals.'},
    {n:'13',name:'Web Security Lab',repo:'web-security-lab',cats:['web','security'],tags:['PHP','JavaScript','Security'],ar:'مختبر تعليمي لمفاهيم أمان الويب والممارسات الدفاعية.',en:'A defensive learning lab for web-security concepts and safer implementation patterns.',problemAr:'مفاهيم أمان الويب تحتاج أمثلة تطبيقية وليست نظرية فقط.',solutionAr:'تجارب دفاعية صغيرة تشرح الفكرة ضمن بيئة تعليمية.',problemEn:'Web-security concepts are easier to learn with practical examples.',solutionEn:'Small defensive exercises designed for learning and safer development.'},
    {n:'14',name:'Mobile App Starter Kit',repo:'mobile-app-starter-kit',cats:['mobile'],tags:['Kotlin','Android','Python'],ar:'قاعدة بداية لتطبيقات الهاتف وتجارب Android وPython Kivy.',en:'A mobile starter kit for Android-oriented experiments and Python/Kivy prototypes.',problemAr:'بدء تطبيق جديد يتطلب تجهيزات متكررة للهيكل والواجهة.',solutionAr:'قاعدة انطلاق تختصر الخطوات الأولى للتجارب الجديدة.',problemEn:'Starting a mobile prototype repeats the same setup steps.',solutionEn:'A reusable starting point for faster mobile experiments.'},
    {n:'15',name:'C++ Algorithms Lab',repo:'cpp-algorithms-lab',cats:['cpp','tools'],tags:['C++','CMake','Algorithms'],ar:'تطبيقات تدريبية للخوارزميات والبحث والفرز وهياكل البيانات.',en:'A C++ algorithms lab covering search, sorting and data-structure practice.',problemAr:'الخوارزميات تحتاج تنفيذًا عمليًا لفهم سلوكها.',solutionAr:'أمثلة صغيرة يمكن تشغيلها ومقارنتها وتعديلها.',problemEn:'Algorithms are easier to understand through implementation.',solutionEn:'Runnable examples for practicing and comparing algorithm behavior.'},
    {n:'16',name:'Python Automation Hub',repo:'python-automation-hub',cats:['python','automation'],tags:['Python','Automation','CLI'],ar:'سكربتات Python لأتمتة الملفات والتقارير والنسخ الاحتياطي.',en:'A Python automation hub for files, reports and repeatable utility workflows.',problemAr:'المهام المتكررة يمكن تحويلها إلى خطوات آلية قابلة لإعادة الاستخدام.',solutionAr:'سكربتات منظمة لكل نوع من الأتمتة بدل حلول متفرقة.',problemEn:'Repeated utility work can be converted into reusable automation.',solutionEn:'Organized scripts for common automation categories.'},
    {n:'17',name:'Fullstack Mini Projects',repo:'fullstack-mini-projects',cats:['web','data'],tags:['PHP','JavaScript','SQL'],ar:'مشاريع Fullstack صغيرة تربط الواجهة بالخادم وقاعدة البيانات.',en:'Small full-stack projects connecting browser UI, server logic and SQL data.',problemAr:'فهم Fullstack يحتاج رؤية تدفق البيانات من الواجهة إلى الخادم.',solutionAr:'مشاريع مصغرة تركز على دورة كاملة بدل أجزاء منفصلة.',problemEn:'Full-stack learning benefits from seeing the entire request-to-data flow.',solutionEn:'Compact projects that demonstrate the full application cycle.'},
    {n:'18',name:'Developer Portfolio',repo:'developer-portfolio',cats:['web'],tags:['HTML','CSS','JavaScript'],ar:'تجربة موقع شخصي متجاوب لعرض الهوية والمهارات والمشاريع.',en:'A responsive developer-portfolio experiment for presenting identity, skills and work.',problemAr:'عرض الأعمال يحتاج هيكلة واضحة ومتجاوبة.',solutionAr:'واجهة شخصية منظمة يمكن تكييفها لمحتوى مختلف.',problemEn:'A portfolio needs clear structure across different screen sizes.',solutionEn:'A responsive layout for presenting work and developer identity.'},
    {n:'19',name:'Portfolio',repo:'portfolio',cats:['web'],tags:['HTML','CSS','JavaScript'],ar:'واجهة Portfolio لعرض الأعمال البرمجية بصورة منظمة.',en:'A portfolio interface for organizing and presenting software projects.',problemAr:'المشاريع المتعددة تحتاج طريقة مختصرة للتصفح.',solutionAr:'واجهة تركّز على الوصول السريع للمشاريع والروابط.',problemEn:'Multiple projects need a concise browsing experience.',solutionEn:'A focused interface for quick access to projects and links.'},
    {n:'20',name:'RAD / Main Portfolio',repo:'rad',cats:['web'],tags:['Portfolio','Projects','RAD'],ar:'الموقع الرئيسي الحالي لعرض الهوية والمشاريع وروابط التواصل.',en:'The main portfolio website presenting identity, projects and contact paths.',problemAr:'جمع الهوية والمشاريع والتواصل في تجربة واحدة متماسكة.',solutionAr:'موقع شخصي موحد يعرض الأعمال وروابط المصدر والتواصل.',problemEn:'Identity, projects and contact options need one coherent experience.',solutionEn:'A unified portfolio that brings work, source links and contact options together.',demo:true}
  ];

  const I18N = {
    ar:{dir:'rtl',lang:'ar',available:'متاح لتنفيذ المشاريع',services:'الخدمات',servicesTitle:'ماذا أستطيع أن أنجز لك؟',servicesSub:'حلول برمجية مركزة حسب احتياج المشروع، من الواجهة إلى الأتمتة والأدوات.',request:'اطلب مشروعك',process:'طريقة العمل',processTitle:'كيف نبدأ مشروعك؟',processSub:'مسار واضح من الفكرة حتى التسليم.',tools:'الأدوات',toolsTitle:'الأدوات والتقنيات التي أستخدمها',areas:'المجالات',areasTitle:'مجالات العمل',timeline:'المسار',timelineTitle:'كيف تطورت أعمالي',faq:'الأسئلة الشائعة',faqTitle:'أسئلة قد تهمك قبل بدء المشروع',contact:'لنبدأ',contactTitle:'لديك فكرة؟ يمكننا تحويلها إلى مشروع.',contactSub:'تصفح المشاريع، اختر ما يناسبك، ثم أرسل ملخص الفكرة مباشرة.',search:'ابحث في المشاريع...',all:'الكل',showMore:'عرض المزيد',showLess:'عرض أقل',github:'GitHub',demo:'معاينة المشروع',source:'Source Code',details:'تفاصيل المشروع',problem:'المشكلة',solution:'الحل',similar:'مشاريع مشابهة',copyLink:'نسخ رابط المشروع',ask:'اسأل عن هذا المشروع',prev:'السابق',next:'التالي',fullscreen:'ملء الشاشة',zoom:'تكبير',close:'إغلاق',sort:'الترتيب',sortDefault:'الترتيب الأصلي',sortName:'الاسم',sortNewest:'الأحدث تحديثًا',complexity:'تقدير التعقيد',simple:'بسيط',medium:'متوسط',advanced:'متقدم',generate:'إنشاء ملخص الطلب',copy:'نسخ',share:'مشاركة',install:'تثبيت الموقع',update:'تحديث الموقع',updated:'يتوفر تحديث جديد للموقع',version:'إصدار الموقع',continueProject:'متابعة آخر مشروع',welcome:'مرحبًا بك في ملفي البرمجي',welcomeSub:'يمكنك البحث في المشاريع أو استخدام Ctrl + K للوصول السريع.',command:'اكتب أمرًا أو ابحث عن مشروع...',noResults:'لا توجد نتائج',portfolioPdf:'Portfolio PDF',cv:'CV',reduceMotion:'تقليل الحركة',light:'فاتح',dark:'داكن',arabic:'العربية',english:'English',projectForm:'طلب مشروع',projectType:'نوع المشروع',features:'الميزات المطلوبة',deadline:'المدة التقريبية',notes:'تفاصيل إضافية',summary:'ملخص الطلب',featured:'مشروع بارز',inProgress:'قيد التطوير',githubActivity:'نشاط GitHub',latestRepos:'أحدث المستودعات تحديثًا',followGithub:'تابعني على GitHub',publicRepo:'مستودع عام',language:'اللغة',stars:'Stars',forks:'Forks',lastUpdate:'آخر تحديث',download:'تنزيل',printPdf:'حفظ Portfolio كـ PDF',serviceLink:'نسخ رابط الخدمة'},
    en:{dir:'ltr',lang:'en',available:'Available for projects',services:'Services',servicesTitle:'What can I build for you?',servicesSub:'Focused software solutions across web, desktop, mobile, automation and tooling.',request:'Start a project',process:'Process',processTitle:'How do we start your project?',processSub:'A clear path from idea to delivery.',tools:'Tools',toolsTitle:'Tools and technologies I use',areas:'Areas',areasTitle:'Areas I work in',timeline:'Journey',timelineTitle:'How my work evolved',faq:'FAQ',faqTitle:'Questions you may have before starting',contact:'Let’s build',contactTitle:'Have an idea? We can turn it into a project.',contactSub:'Browse the projects, choose a direction and send a concise project brief.',search:'Search projects...',all:'All',showMore:'Show more',showLess:'Show less',github:'GitHub',demo:'Live demo',source:'Source Code',details:'Project details',problem:'Problem',solution:'Solution',similar:'Similar projects',copyLink:'Copy project link',ask:'Ask about this project',prev:'Previous',next:'Next',fullscreen:'Fullscreen',zoom:'Zoom',close:'Close',sort:'Sort',sortDefault:'Original order',sortName:'Name',sortNewest:'Recently updated',complexity:'Complexity estimate',simple:'Simple',medium:'Medium',advanced:'Advanced',generate:'Generate project brief',copy:'Copy',share:'Share',install:'Install app',update:'Update site',updated:'A new site version is available',version:'Site version',continueProject:'Continue last project',welcome:'Welcome to my developer portfolio',welcomeSub:'Search projects or press Ctrl + K for quick navigation.',command:'Type a command or search projects...',noResults:'No results',portfolioPdf:'Portfolio PDF',cv:'CV',reduceMotion:'Reduce motion',light:'Light',dark:'Dark',arabic:'العربية',english:'English',projectForm:'Project request',projectType:'Project type',features:'Required features',deadline:'Approximate timeline',notes:'Additional details',summary:'Project brief',featured:'Featured project',inProgress:'In development',githubActivity:'GitHub activity',latestRepos:'Recently updated repositories',followGithub:'Follow on GitHub',publicRepo:'Public repository',language:'Language',stars:'Stars',forks:'Forks',lastUpdate:'Last update',download:'Download',printPdf:'Save portfolio as PDF',serviceLink:'Copy service link'}
  };

  let lang = store.get('rad-lang', document.documentElement.lang === 'en' ? 'en' : 'ar');
  let projectSort = 'default';
  let projectFilter = 'all';
  let projectTech = 'all';
  let currentModalIndex = -1;
  let repoCache = new Map();
  let deferredInstallPrompt = null;
  let swRegistration = null;
  const t = key => I18N[lang][key] || key;

  const icons = {
    github:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .7A11.3 11.3 0 0 0 8.43 22.72c.57.11.78-.25.78-.55v-2c-3.16.69-3.83-1.35-3.83-1.35-.52-1.31-1.27-1.67-1.27-1.67-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.18 1.74 1.18 1.02 1.73 2.67 1.23 3.32.94.1-.73.4-1.23.72-1.51-2.52-.29-5.18-1.26-5.18-5.62 0-1.24.45-2.25 1.17-3.05-.12-.29-.5-1.45.12-3.02 0 0 .95-.3 3.12 1.16a10.8 10.8 0 0 1 5.69 0c2.16-1.46 3.11-1.16 3.11-1.16.62 1.57.23 2.73.11 3.02.73.8 1.16 1.81 1.16 3.05 0 4.37-2.66 5.33-5.19 5.61.41.35.78 1.05.78 2.12v2.99c0 .3.21.66.79.55A11.3 11.3 0 0 0 12 .7Z"/></svg>',
    search:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="m21 21-4.6-4.6m2.1-4.9a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/></svg>',
    share:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M18 8a3 3 0 1 0-2.8-4A3 3 0 0 0 18 8ZM6 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm12 7a3 3 0 1 0-2.8-4A3 3 0 0 0 18 22ZM8.7 10.5l6.6-3.7M8.7 13.5l6.6 3.7"/></svg>',
    up:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m6 15 6-6 6 6"/></svg>',
    sun:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    moon:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 15.5A8.2 8.2 0 0 1 8.5 3.5 8.5 8.5 0 1 0 20.5 15.5Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
  };

  function showToast(message, actionText = '', action = null) {
    let box = $('#enhToast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'enhToast';
      box.className = 'enh-toast';
      box.setAttribute('role', 'status');
      box.setAttribute('aria-live', 'polite');
      document.body.appendChild(box);
    }
    box.innerHTML = `<span>${message}</span>${actionText ? `<button type="button">${actionText}</button>` : ''}`;
    box.classList.add('is-visible');
    clearTimeout(box._timer);
    if (actionText && action) $('button', box)?.addEventListener('click', action, { once: true });
    box._timer = setTimeout(() => box.classList.remove('is-visible'), actionText ? 7000 : 2200);
  }

  function injectHead() {
    if (!document.querySelector('link[href="enhancements.css"]')) {
      const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = 'enhancements.css'; document.head.appendChild(link);
    }
    if (!document.querySelector('link[rel="manifest"]')) {
      const link = document.createElement('link'); link.rel = 'manifest'; link.href = 'manifest.webmanifest'; document.head.appendChild(link);
    }
    const theme = document.querySelector('meta[name="theme-color"]') || Object.assign(document.createElement('meta'), { name: 'theme-color' });
    theme.content = store.get('rad-theme', 'dark') === 'light' ? '#f4f6ef' : '#111410';
    if (!theme.parentNode) document.head.appendChild(theme);
    if (!document.querySelector('link[rel="canonical"]')) {
      const c = document.createElement('link'); c.rel = 'canonical'; c.href = location.origin + location.pathname; document.head.appendChild(c);
    }
  }

  function addProgressBar() {
    if ($('#enhProgress')) return;
    const bar = document.createElement('div'); bar.id = 'enhProgress'; bar.className = 'enh-progress'; bar.innerHTML = '<span></span>'; document.body.prepend(bar);
    const update = () => {
      const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      $('span', bar).style.transform = `scaleX(${Math.min(1, scrollY / max)})`;
    };
    addEventListener('scroll', update, { passive: true }); addEventListener('resize', update, { passive: true }); update();
  }

  function addLoadingScreen() {
    if (sessionStorage.getItem('rad-loaded')) return;
    sessionStorage.setItem('rad-loaded', '1');
    const s = document.createElement('div'); s.className = 'enh-loader'; s.innerHTML = '<div><b>&lt;RAD /&gt;</b><span></span></div>'; document.body.prepend(s);
    requestAnimationFrame(() => setTimeout(() => s.classList.add('is-done'), 260));
    setTimeout(() => s.remove(), 900);
  }

  function applyTheme(theme = store.get('rad-theme', 'dark')) {
    theme = theme === 'light' ? 'light' : 'dark'; store.set('rad-theme', theme);
    document.documentElement.classList.toggle('enh-light', theme === 'light');
    document.documentElement.dataset.theme = theme;
    const meta = document.querySelector('meta[name="theme-color"]'); if (meta) meta.content = theme === 'light' ? '#f4f6ef' : '#111410';
    const btn = $('#enhThemeToggle'); if (btn) { btn.innerHTML = theme === 'light' ? icons.moon : icons.sun; btn.dataset.tip = theme === 'light' ? t('dark') : t('light'); }
  }

  function setMotion(reduced) {
    store.set('rad-motion', reduced ? 'reduced' : 'normal');
    document.documentElement.classList.toggle('enh-reduce-motion', reduced);
    const b = $('#enhMotionToggle'); if (b) b.classList.toggle('is-active', reduced);
  }

  function addHeaderControls() {
    const header = $('.header-inner') || $('.site-header'); if (!header) return;
    let wrap = $('#enhHeaderControls');
    if (!wrap) {
      wrap = document.createElement('div'); wrap.id = 'enhHeaderControls'; wrap.className = 'enh-header-controls';
      wrap.innerHTML = `<button id="enhLangToggle" type="button" data-tip="Language">EN</button><button id="enhThemeToggle" type="button"></button><button id="enhCommandOpen" type="button" data-tip="Ctrl + K">⌘K</button><button id="enhMotionToggle" type="button" data-tip="${t('reduceMotion')}">≈</button>`;
      header.appendChild(wrap);
    }
    if (wrap.dataset.bound !== '1') {
      wrap.dataset.bound = '1';
      $('#enhLangToggle')?.addEventListener('click', () => setLanguage(lang === 'ar' ? 'en' : 'ar'));
      $('#enhThemeToggle')?.addEventListener('click', () => applyTheme(document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'));
      $('#enhCommandOpen')?.addEventListener('click', openCommandPalette);
      $('#enhMotionToggle')?.addEventListener('click', () => setMotion(!document.documentElement.classList.contains('enh-reduce-motion')));
    }
    applyTheme(); setMotion(store.get('rad-motion') === 'reduced');
  }

  function saveBaseText() {
    const candidates = ['.brand-text small', '.eyebrow', '.hero-role', '.hero-description', '.hero-actions .button', '.hero-actions .text-link', '#projects-title'];
    candidates.forEach(sel => $$(sel).forEach(el => { if (!el.dataset.arHtml) el.dataset.arHtml = el.innerHTML; }));
    $$('#navigation a').forEach(a => { if (!a.dataset.arHtml) a.dataset.arHtml = a.innerHTML; });
  }

  function translateBase() {
    saveBaseText();
    const isEn = lang === 'en';
    const navMap = { '#about':'About', '#skills':'Skills', '#projects':'Projects', '#services':'Services', '#contact':'Contact' };
    $$('#navigation a').forEach(a => {
      const href = a.getAttribute('href');
      if (isEn && navMap[href]) a.textContent = navMap[href];
      else if (!isEn && a.dataset.arHtml) a.innerHTML = a.dataset.arHtml;
    });
    const eyebrow = $('.eyebrow'); if (eyebrow) eyebrow.innerHTML = isEn ? 'HELLO, I\'M' : (eyebrow.dataset.arHtml || eyebrow.innerHTML);
    const role = $('.hero-role'); if (role) role.innerHTML = isEn ? 'Software Developer <span>&lt;/&gt;</span>' : (role.dataset.arHtml || role.innerHTML);
    const desc = $('.hero-description'); if (desc) desc.textContent = isEn ? 'I build web, desktop, mobile and automation tools with a focus on practical interfaces and maintainable workflows.' : (desc.dataset.arHtml ? stripHtml(desc.dataset.arHtml) : desc.textContent);
    const heroBtn = $('.hero-actions .button'); if (heroBtn) heroBtn.innerHTML = isEn ? 'Explore projects <span aria-hidden="true">←</span>' : (heroBtn.dataset.arHtml || heroBtn.innerHTML);
    const heroLink = $('.hero-actions .text-link'); if (heroLink) heroLink.innerHTML = isEn ? 'About me <span aria-hidden="true">↓</span>' : (heroLink.dataset.arHtml || heroLink.innerHTML);
    const projectsTitle = $('#projects-title'); if (projectsTitle) projectsTitle.textContent = isEn ? 'My projects' : 'مشاريعي الخاصة';
  }

  function stripHtml(html) { const d = document.createElement('div'); d.innerHTML = html; return d.textContent || ''; }

  function setLanguage(next) {
    lang = next === 'en' ? 'en' : 'ar'; store.set('rad-lang', lang);
    document.documentElement.lang = I18N[lang].lang; document.documentElement.dir = I18N[lang].dir;
    const b = $('#enhLangToggle'); if (b) b.textContent = lang === 'ar' ? 'EN' : 'AR';
    translateBase(); renderDynamicText(); renderProjectsLanguage();
    const servicesSection = $('#services'); if (servicesSection) renderCompactService(servicesSection, servicesSection.dataset.activeService || 'web', false);
    showToast(lang === 'ar' ? 'تم تفعيل العربية' : 'English enabled');
  }

  function renderProjectsLanguage() {
    const cards = $$('.showcase-card');
    cards.forEach((card, i) => {
      const p = projects[i]; if (!p) return;
      const desc = $('.showcase-content > p', card); if (desc) desc.textContent = lang === 'ar' ? p.ar : p.en;
      const sourceText = $('.showcase-github-link span', card); if (sourceText) sourceText.textContent = lang === 'ar' ? 'عرض المشروع على GitHub' : 'View on GitHub';
    });
  }

  function renderDynamicText() {
    $$('[data-i18n]').forEach(el => { const key = el.dataset.i18n; if (I18N[lang][key]) el.textContent = t(key); });
    $$('[data-i18n-placeholder]').forEach(el => { const key = el.dataset.i18nPlaceholder; if (I18N[lang][key]) el.placeholder = t(key); });
    const b = $('#enhLangToggle'); if (b) b.textContent = lang === 'ar' ? 'EN' : 'AR';
  }

  function addAvailability() {
    const copy = $('.hero-copy'); if (!copy || $('.enh-availability', copy)) return;
    const badge = document.createElement('div'); badge.className = 'enh-availability enh-reveal'; badge.dataset.i18n = 'available'; badge.textContent = t('available');
    const actions = $('.hero-actions', copy); if (actions) actions.insertAdjacentElement('beforebegin', badge); else copy.appendChild(badge);
  }


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

  function addStatsAndTicker() {
    const hero = $('.hero'); if (!hero || $('#enhStats')) return;
    const stats = document.createElement('section'); stats.id = 'enhStats'; stats.className = 'enh-shell enh-reveal';
    stats.innerHTML = `<div class="enh-stats"><div class="enh-stat enh-stat--projects"><div class="enh-stat-dual"><div class="enh-stat-pane"><strong data-count="${projects.length}">0</strong><span data-stat-label="displayed">${lang==='ar'?'مشروعًا معروضًا':'projects displayed'}</span></div><span class="enh-stat-divider" aria-hidden="true"></span><div class="enh-stat-pane enh-stat-pane--github"><strong id="githubRepoCount" data-github-count>—</strong><span data-stat-label="github">${lang==='ar'?'مستودعات GitHub':'GitHub repositories'}</span></div></div></div><div class="enh-stat enh-stat--dynamic" data-stat-group="web" data-stat-index="0" data-ghost="WEB"><div class="enh-stat-copy"><strong data-stat-title>Websites</strong><span data-stat-desc>مواقع شخصية وتجارية متجاوبة</span></div></div><div class="enh-stat enh-stat--dynamic" data-stat-group="desktop" data-stat-index="0" data-ghost="WIN"><div class="enh-stat-copy"><strong data-stat-title>Windows Apps</strong><span data-stat-desc>تطبيقات وأدوات Windows مخصصة</span></div></div><div class="enh-stat enh-stat--dynamic" data-stat-group="automation" data-stat-index="0" data-ghost="AUTO"><div class="enh-stat-copy"><strong data-stat-title>Automation</strong><span data-stat-desc>أتمتة المهام وسير العمل المتكرر</span></div></div></div>`;
    hero.insertAdjacentElement('afterend', stats);
    const tech = document.createElement('div'); tech.className = 'enh-tech-strip enh-reveal'; tech.setAttribute('aria-label','Programming languages and technologies');
    tech.innerHTML = '<div class="enh-tech-track" id="programmingIconTicker" aria-hidden="true"></div>';
    stats.insertAdjacentElement('afterend', tech);
    hydrateTechIconTicker();
  }

  function addFeaturedSinax() {
    const projectsSection = $('#projects'); if (!projectsSection || $('#enhFeatured')) return;
    const sec = document.createElement('section'); sec.id = 'enhFeatured'; sec.className = 'enh-featured enh-section';
    sec.innerHTML = `<div class="enh-shell"><div class="enh-featured-card enh-reveal"><div class="enh-featured-copy"><div class="enh-kicker" data-i18n="featured">${t('featured')}</div><h2>SINAX</h2><p>${lang==='ar'?'تطبيق Windows قيد التطوير يركز على إدارة الملفات وأدوات PDF والصور والصوت والنظام والتخزين ضمن واجهة واحدة.':'A Windows application in development, focused on file management plus PDF, image, audio, system and storage utilities in one interface.'}</p><div class="enh-tags"><span>Windows</span><span>C#</span><span>.NET</span><span data-i18n="inProgress">${t('inProgress')}</span></div></div><div class="enh-featured-mark">S<span>/</span>X</div></div></div>`;
    projectsSection.insertAdjacentElement('beforebegin', sec);
  }

  const serviceItems = [
    ['web','WEB','مواقع ويب','Websites','مواقع شخصية، صفحات تعريفية، لوحات وواجهات متجاوبة.','Portfolios, landing pages, dashboards and responsive interfaces.'],
    ['windows','WIN','تطبيقات Windows','Windows apps','أدوات سطح مكتب وإدارة ملفات وواجهات عملية.','Desktop utilities, file workflows and practical interfaces.'],
    ['mobile','APP','تطبيقات هاتف','Mobile apps','واجهات وتجارب Android وKivy قابلة للتطوير.','Android-oriented interfaces and extendable mobile prototypes.'],
    ['python','PY','Python','Python','سكربتات وأدوات لمعالجة الملفات والبيانات.','Scripts and utilities for files, data and automation.'],
    ['automation','AUTO','الأتمتة','Automation','اختصارات وسير عمل لتقليل المهام المتكررة.','Shortcuts and workflows that reduce repetitive work.'],
    ['ai','AI','أدوات AI','AI tools','دمج أدوات ذكية في تجارب وبرامج إنتاجية.','AI-assisted utilities for practical productivity workflows.']
  ];

  const compactServices = {
    web: {
      code:'WEB',
      arTitle:'الويب والمنصات',
      enTitle:'Web & Platforms',
      arDesc:'مواقع سريعة ومتجاوبة تشرح فكرتك بوضوح وتحوّلها إلى تجربة احترافية.',
      enDesc:'Fast, responsive web experiences that present your idea clearly and professionally.',
      arPoints:['مواقع وصفحات هبوط','متاجر ولوحات تحكم','واجهات عربية RTL'],
      enPoints:['Websites & landing pages','Stores & dashboards','Arabic RTL interfaces']
    },
    windows: {
      code:'WIN',
      arTitle:'Windows والحاسوب',
      enTitle:'Windows & Desktop',
      arDesc:'تطبيقات وأدوات حاسوب مخصصة للعمل اليومي وإدارة الملفات والمهام.',
      enDesc:'Purpose-built desktop apps and utilities for files, workflows and daily operations.',
      arPoints:['C# و.NET وWinUI','أدوات ملفات ونظام','برامج داخلية مخصصة'],
      enPoints:['C#, .NET & WinUI','File & system tools','Custom internal software']
    },
    mobile: {
      code:'APP',
      arTitle:'تطبيقات الهاتف',
      enTitle:'Mobile Apps',
      arDesc:'تجارب هاتف واضحة وقابلة للتطوير للفكرة أو الخدمة التي تريد إطلاقها.',
      enDesc:'Clear, extendable mobile experiences built around the product or service you want to launch.',
      arPoints:['تطبيقات Android','واجهات هاتف حديثة','نماذج قابلة للتطوير'],
      enPoints:['Android apps','Modern mobile UI','Extendable prototypes']
    },
    automation: {
      code:'AUTO',
      arTitle:'Python والأتمتة',
      enTitle:'Python & Automation',
      arDesc:'تحويل الخطوات المتكررة إلى أدوات وسير عمل أسرع وأكثر دقة.',
      enDesc:'Turning repetitive steps into faster, more reliable tools and automated workflows.',
      arPoints:['معالجة ملفات وبيانات','تقارير ونسخ احتياطي','أتمتة مهام متكررة'],
      enPoints:['File & data processing','Reports & backups','Workflow automation']
    },
    ai: {
      code:'AI',
      arTitle:'حلول الذكاء الاصطناعي',
      enTitle:'AI Solutions',
      arDesc:'إضافة قدرات ذكية إلى موقعك أو برنامجك أو سير عملك بطريقة عملية.',
      enDesc:'Practical AI capabilities integrated into your website, software or workflow.',
      arPoints:['مساعدون وأدوات AI','معالجة نصوص ومحتوى','تكامل نماذج وخدمات ذكية'],
      enPoints:['AI assistants & tools','Text & content workflows','Model & service integrations']
    },
    data: {
      code:'DATA',
      arTitle:'البيانات والأنظمة',
      enTitle:'Data, APIs & IoT',
      arDesc:'ربط البيانات والخدمات والأجهزة في نظام واحد واضح وسهل المتابعة.',
      enDesc:'Connecting data, services and devices into one clear, manageable system.',
      arPoints:['APIs وقواعد بيانات','لوحات بيانات وتقارير','IoT وحساسات'],
      enPoints:['APIs & databases','Dashboards & reports','IoT & sensors']
    }
  };

  function renderCompactService(section, id, animate=false) {
    if (!section) return;
    const service = compactServices[id] || compactServices.web;
    const panel = $('.enh-service-stage', section);
    if (!panel) return;
    const isEn = lang === 'en';

    const apply = () => {
      section.dataset.activeService = id;
      $$('.enh-service-tab', section).forEach(tab => {
        const active = tab.dataset.service === id;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.tabIndex = active ? 0 : -1;
      });

      const code = $('[data-service-code]', panel);
      const title = $('[data-service-title]', panel);
      const desc = $('[data-service-desc]', panel);
      const points = $('[data-service-points]', panel);
      const cta = $('[data-service-cta]', panel);
      const watermark = $('.enh-service-watermark', panel);

      if (code) code.textContent = service.code;
      if (watermark) watermark.textContent = service.code;
      if (title) title.textContent = isEn ? service.enTitle : service.arTitle;
      if (desc) desc.textContent = isEn ? service.enDesc : service.arDesc;
      if (points) {
        const list = isEn ? service.enPoints : service.arPoints;
        points.innerHTML = list.map(item => `<span>${item}</span>`).join('');
      }
      if (cta) cta.textContent = isEn ? 'Request this service' : 'اطلب هذه الخدمة';

      const sectionSubtitle = $('.enh-services-short', section);
      if (sectionSubtitle) sectionSubtitle.textContent = isEn
        ? 'Choose a direction. I will shape the right solution around your idea.'
        : 'اختر المجال فقط، وأنا أبني الحل المناسب حول فكرتك.';
    };

    if (!animate || document.documentElement.classList.contains('enh-reduce-motion') || matchMedia('(prefers-reduced-motion: reduce)').matches) {
      apply();
      return;
    }
    panel.classList.add('is-switching');
    window.setTimeout(() => {
      apply();
      requestAnimationFrame(() => panel.classList.remove('is-switching'));
    }, 180);
  }

  function addServices() {
    const projectsSection = $('#projects'); if (!projectsSection || $('#services')) return;
    const order = ['web','windows','mobile','automation','ai','data'];
    const sec = document.createElement('section');
    sec.id = 'services';
    sec.className = 'enh-services enh-section enh-snap';
    sec.dataset.activeService = 'web';

    sec.innerHTML = `
      <div class="enh-shell">
        <div class="enh-services-head">
          <div>
            <div class="enh-kicker" data-i18n="services">${t('services')}</div>
            <h2 class="enh-title" data-i18n="servicesTitle">${t('servicesTitle')}</h2>
          </div>
          <p class="enh-services-short">${lang==='ar'?'اختر المجال فقط، وأنا أبني الحل المناسب حول فكرتك.':'Choose a direction. I will shape the right solution around your idea.'}</p>
        </div>

        <div class="enh-service-tabs" role="tablist" aria-label="${lang==='ar'?'الخدمات':'Services'}">
          ${order.map((id,index)=>{
            const s=compactServices[id];
            return `<button type="button" class="enh-service-tab${index===0?' is-active':''}" role="tab" aria-selected="${index===0?'true':'false'}" tabindex="${index===0?'0':'-1'}" data-service="${id}"><b>${s.code}</b><span>${s.enTitle}</span></button>`;
          }).join('')}
        </div>

        <article class="enh-service-stage enh-reveal" role="tabpanel" aria-live="polite">
          <div class="enh-service-stage-glow" aria-hidden="true"></div>
          <div class="enh-service-stage-copy">
            <span class="enh-service-code" data-service-code>WEB</span>
            <h3 data-service-title>${compactServices.web.arTitle}</h3>
            <p data-service-desc>${compactServices.web.arDesc}</p>
            <div class="enh-service-points" data-service-points>
              ${compactServices.web.arPoints.map(item=>`<span>${item}</span>`).join('')}
            </div>
          </div>
          <div class="enh-service-stage-action">
            <span class="enh-service-watermark" aria-hidden="true">WEB</span>
            <a class="enh-primary" data-service-cta href="${projectRequestUrl}" target="_blank" rel="noopener noreferrer">اطلب هذه الخدمة</a>
          </div>
        </article>
      </div>`;

    const tabList = $('.enh-service-tabs', sec);
    tabList?.addEventListener('click', event => {
      const tab = event.target.closest('.enh-service-tab');
      if (!tab) return;
      renderCompactService(sec, tab.dataset.service, true);
    });

    tabList?.addEventListener('keydown', event => {
      if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      const tabs = $$('.enh-service-tab', sec);
      if (!tabs.length) return;
      const current = tabs.indexOf(document.activeElement);
      let next = current < 0 ? 0 : current;
      if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else {
        const rtl = document.documentElement.dir === 'rtl';
        const forward = event.key === (rtl ? 'ArrowLeft' : 'ArrowRight');
        next = (current + (forward ? 1 : -1) + tabs.length) % tabs.length;
      }
      event.preventDefault();
      tabs[next].focus();
      renderCompactService(sec, tabs[next].dataset.service, true);
    });

    projectsSection.insertAdjacentElement('beforebegin', sec);
    renderCompactService(sec, 'web', false);
  }

  function addProcess() {
    const services = $('#services'); if (!services || $('#enhProcess')) return;
    const items = lang==='ar' ? [['01','الفكرة','تحدد الهدف والنتيجة التي تريد الوصول إليها.'],['02','إرسال الطلب','تعبئ نموذج Tally بتفاصيل المشروع والميزانية والملفات إن وجدت.'],['03','الاستشارة','عند الحاجة تحجز جلسة Calendly لمدة 30 دقيقة لمناقشة المتطلبات.'],['04','الاتفاق','نحدد النطاق والسعر والمدة قبل بدء التنفيذ.'],['05','الدفع والتنفيذ','بعد الاتفاق يتم الدفع الآمن عبر Stripe ثم يبدأ التطوير والاختبار.'],['06','التسليم والمتابعة','بعد التسليم يمكن للعميل الاشتراك في تحديثات المشاريع عبر Omnisend ومتابعة الجديد.']] : [['01','Idea','Define the goal and the result you want to achieve.'],['02','Project request','Submit the Tally form with project details, budget and supporting files.'],['03','Consultation','If needed, book a 30-minute Calendly consultation to discuss requirements.'],['04','Agreement','Confirm scope, price and timeline before development starts.'],['05','Payment & build','After agreement, payment is handled securely through Stripe and development begins.'],['06','Delivery & follow-up','After delivery, clients can subscribe to project updates through Omnisend and follow new releases.']];
    const sec = document.createElement('section'); sec.id='enhProcess'; sec.className='enh-section enh-snap'; sec.innerHTML=`<div class="enh-shell"><div class="enh-kicker" data-i18n="process">${t('process')}</div><h2 class="enh-title" data-i18n="processTitle">${t('processTitle')}</h2><p class="enh-subtitle" data-i18n="processSub">${t('processSub')}</p><div class="enh-process-grid">${items.map(([n,h,p])=>`<article class="enh-process-card enh-reveal"><b>${n}</b><h3>${h}</h3><p>${p}</p></article>`).join('')}</div><div class="enh-request-row"><a class="enh-primary" href="${projectRequestUrl}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'ابدأ طلب مشروع':'Start a project request'}</a><a class="enh-secondary" href="${consultationUrl}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'احجز استشارة':'Book a consultation'}</a><a class="enh-secondary" href="${omnisendUpdates}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'تابع تحديثات المشاريع':'Project updates'}</a><small class="enh-muted">${lang==='ar'?'الدفع الآمن عبر Stripe يتم بعد الاتفاق على نطاق المشروع والسعر.':'Secure Stripe payment is provided after scope and price are agreed.'}</small></div></div>`;
    services.insertAdjacentElement('afterend', sec);
  }

  function addToolsAreasTimeline() {
    const projectsSection = $('#projects'); if (!projectsSection || $('#enhToolsAreas')) return;
    const tools=['Visual Studio','VS Code','GitHub','Git','Python','.NET','PowerShell','Android','SQL','C++'];
    const areas=lang==='ar'?['Web','Desktop','Mobile','Automation','AI Tools','Data & IoT']:['Web','Desktop','Mobile','Automation','AI Tools','Data & IoT'];
    const timeline = lang==='ar' ? [['البداية','تجارب الويب والبرمجة الأساسية.'],['التوسع','مشاريع Python وJavaScript وأدوات الملفات.'],['تطبيقات الحاسوب','التركيز على C# وWindows والأتمتة.'],['الآن','دمج الويب والحاسوب والهاتف والأدوات الذكية في مشاريع أوضح.']] : [['Foundation','Core programming and web experiments.'],['Expansion','Python, JavaScript and file-processing projects.'],['Desktop focus','More C#, Windows utilities and automation.'],['Now','Combining web, desktop, mobile and smart tooling in clearer projects.']];
    const sec=document.createElement('section'); sec.id='enhToolsAreas'; sec.className='enh-section'; sec.innerHTML=`<div class="enh-shell"><div class="enh-dual"><div><div class="enh-kicker" data-i18n="tools">${t('tools')}</div><h2 class="enh-title small" data-i18n="toolsTitle">${t('toolsTitle')}</h2><div class="enh-logo-grid">${tools.map(x=>`<span>${x}</span>`).join('')}</div></div><div><div class="enh-kicker" data-i18n="areas">${t('areas')}</div><h2 class="enh-title small" data-i18n="areasTitle">${t('areasTitle')}</h2><div class="enh-area-list">${areas.map(x=>`<span>${x}</span>`).join('')}</div></div></div><div class="enh-timeline-wrap"><div class="enh-kicker" data-i18n="timeline">${t('timeline')}</div><h2 class="enh-title small" data-i18n="timelineTitle">${t('timelineTitle')}</h2><div class="enh-timeline">${timeline.map(([h,p],i)=>`<article class="enh-reveal"><b>${String(i+1).padStart(2,'0')}</b><div><h3>${h}</h3><p>${p}</p></div></article>`).join('')}</div></div></div>`;
    projectsSection.insertAdjacentElement('beforebegin', sec);
  }

  function addServiceComparison() {
    const tools=$('#enhToolsAreas'); const projectsSection=$('#projects'); if((!tools && !projectsSection) || $('#enhCompare')) return;
    const sec=document.createElement('section'); sec.id='enhCompare'; sec.className='enh-section';
    const cols=lang==='ar' ? [['موقع ويب','أفضل للعرض والخدمات والوصول من أي جهاز.','واجهة متجاوبة','نشر على الويب'],['تطبيق Windows','أفضل للأدوات المحلية وإدارة الملفات والنظام.','واجهة مكتبية','تكامل مع Windows'],['أتمتة','أفضل لتقليل الخطوات المتكررة وتسريع العمل.','سكربتات واختصارات','سير عمل مخصص']] : [['Website','Best for presentation, services and cross-device access.','Responsive UI','Web deployment'],['Windows app','Best for local utilities, files and system workflows.','Desktop UI','Windows integration'],['Automation','Best for reducing repeated steps and speeding up work.','Scripts & shortcuts','Custom workflow']];
    sec.innerHTML=`<div class="enh-shell"><div class="enh-kicker">${lang==='ar'?'اختيار الخدمة':'Choose a service'}</div><h2 class="enh-title small">${lang==='ar'?'ما النوع الأنسب لفكرتك؟':'Which direction fits your idea?'}</h2><div class="enh-compare-grid">${cols.map(c=>`<article><h3>${c[0]}</h3><p>${c[1]}</p><ul><li>${c[2]}</li><li>${c[3]}</li></ul></article>`).join('')}</div></div>`;
    if (tools) tools.insertAdjacentElement('afterend',sec); else projectsSection.insertAdjacentElement('beforebegin',sec);
  }

  function prepareProjectCards() {
    const grid=$('#projectsShowcaseGrid'); if(!grid) return false;
    $$('.showcase-card',grid).forEach((card,i)=>{
      const p=projects[i]; if(!p) return;
      card.dataset.projectIndex=String(i); card.dataset.categories=p.cats.join(' '); card.dataset.tags=p.tags.join(' ').toLowerCase(); card.dataset.search=`${p.name} ${p.repo} ${p.tags.join(' ')} ${p.ar} ${p.en} بايثون python جافاسكربت javascript ويندوز windows أتمتة automation هاتف mobile`.toLowerCase();
      const img=$('img',card); if(img){img.loading='lazy';img.decoding='async'; img.addEventListener('load',()=>card.classList.add('is-image-loaded'),{once:true});}
      const imageLink=$('.showcase-image-link',card); if(imageLink){imageLink.href=projectLink(p.n); imageLink.removeAttribute('target'); imageLink.dataset.tip=t('details');}
      const gh=$('.github-icon-button',card); if(gh) gh.dataset.tip='GitHub';
      if(i===0 && !$('.enh-feature-badge',card)){ const badge=document.createElement('span');badge.className='enh-feature-badge';badge.textContent=lang==='ar'?'مميز':'Featured'; $('.showcase-image-link',card)?.appendChild(badge); }
    });
    renderProjectsLanguage(); return true;
  }

  function projectLink(n) { return `${location.origin}${location.pathname}#project=${n}`; }

  function addProjectTools() {
    const grid=$('#projectsShowcaseGrid'); if(!grid || $('#enhProjectTools')) return;
    const tags=[...new Set(projects.flatMap(p=>p.tags))].sort();
    const tools=document.createElement('div'); tools.id='enhProjectTools'; tools.className='enh-project-tools enh-reveal';
    tools.innerHTML=`<label class="enh-search">${icons.search}<input id="enhProjectSearch" type="search" data-i18n-placeholder="search" placeholder="${t('search')}" autocomplete="off" aria-label="${t('search')}"></label><div class="enh-filters" role="group"><button class="enh-filter is-active" data-filter="all" data-i18n="all">${t('all')}</button><button class="enh-filter" data-filter="web">Web</button><button class="enh-filter" data-filter="windows">Windows</button><button class="enh-filter" data-filter="python">Python</button><button class="enh-filter" data-filter="automation">Automation</button><button class="enh-filter" data-filter="mobile">Mobile</button><button class="enh-filter" data-filter="data">Data / IoT</button></div><label class="enh-select"><span>${lang==='ar'?'تقنية':'Tech'}</span><select id="enhTechFilter"><option value="all">${t('all')}</option>${tags.map(x=>`<option value="${x.toLowerCase()}">${x}</option>`).join('')}</select></label><label class="enh-select"><span data-i18n="sort">${t('sort')}</span><select id="enhProjectSort"><option value="default" data-i18n="sortDefault">${t('sortDefault')}</option><option value="name" data-i18n="sortName">${t('sortName')}</option><option value="newest" data-i18n="sortNewest">${t('sortNewest')}</option></select></label>`;
    grid.insertAdjacentElement('beforebegin',tools);
    const empty=document.createElement('div');empty.id='enhProjectEmpty';empty.className='enh-project-empty';empty.textContent=t('noResults');grid.insertAdjacentElement('afterend',empty);
    const moreWrap=$('.projects-more-wrap'); if(moreWrap&&!$('#enhProjectExtra')){const extra=document.createElement('div');extra.id='enhProjectExtra';extra.className='enh-project-extra-actions';extra.innerHTML=`<a class="enh-secondary" href="https://github.com/${OWNER}?tab=repositories" target="_blank" rel="noopener">${icons.github}<span>${lang==='ar'?'عرض جميع المستودعات':'All repositories'}</span></a><button class="enh-secondary" id="enhShareProjects" type="button">${icons.share}<span data-i18n="share">${t('share')}</span></button><button class="enh-secondary" id="enhPrintPortfolio" type="button"><span data-i18n="printPdf">${t('printPdf')}</span></button>`;moreWrap.insertAdjacentElement('afterend',extra);}
    $('#enhProjectSearch').addEventListener('input',applyProjectFilters);
    $$('.enh-filter',tools).forEach(btn=>btn.addEventListener('click',()=>{projectFilter=btn.dataset.filter;$$('.enh-filter',tools).forEach(b=>b.classList.toggle('is-active',b===btn));applyProjectFilters();}));
    $('#enhTechFilter').addEventListener('change',e=>{projectTech=e.target.value;applyProjectFilters();});
    $('#enhProjectSort').addEventListener('change',e=>{projectSort=e.target.value;sortProjectCards();});
    $('#enhShareProjects')?.addEventListener('click',shareSite); $('#enhPrintPortfolio')?.addEventListener('click',()=>window.print());
  }

  function applyProjectFilters(){
    const grid=$('#projectsShowcaseGrid');if(!grid)return;const q=($('#enhProjectSearch')?.value||'').trim().toLowerCase();const active=q||projectFilter!=='all'||projectTech!=='all';grid.classList.toggle('show-all',Boolean(active));const more=$('.projects-more-wrap');if(more)more.style.display=active?'none':'';let visible=0;
    $$('.showcase-card',grid).forEach(card=>{const text=card.dataset.search||'';const cats=(card.dataset.categories||'').split(' ');const tags=(card.dataset.tags||'').split(' ');const okText=!q||text.includes(q);const okCat=projectFilter==='all'||cats.includes(projectFilter)||(projectFilter==='data'&&(cats.includes('data')||cats.includes('iot')));const okTech=projectTech==='all'||tags.includes(projectTech);const hide=!(okText&&okCat&&okTech);card.classList.toggle('enh-hidden',hide);if(!hide)visible++;});
    $('#enhProjectEmpty')?.classList.toggle('is-visible',visible===0);
  }

  async function sortProjectCards(){
    const grid=$('#projectsShowcaseGrid'); if(!grid) return;
    const cards=$$('.showcase-card',grid);
    if(projectSort==='default') cards.sort((a,b)=>Number(a.dataset.projectIndex)-Number(b.dataset.projectIndex));
    if(projectSort==='name') cards.sort((a,b)=>projects[Number(a.dataset.projectIndex)].name.localeCompare(projects[Number(b.dataset.projectIndex)].name));
    if(projectSort==='newest'){
      await Promise.all(projects.map((p,i)=>getRepoInfo(p).then(x=>cards.find(c=>Number(c.dataset.projectIndex)===i).dataset.updated=x?.pushed_at||'').catch(()=>{})));
      cards.sort((a,b)=>(b.dataset.updated||'').localeCompare(a.dataset.updated||''));
    }
    cards.forEach(c=>grid.appendChild(c));
  }

  function ensureModal(){
    let modal=$('#enhProjectModal');if(modal)return modal;
    modal=document.createElement('div');modal.id='enhProjectModal';modal.className='enh-modal';modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-hidden','true');
    modal.innerHTML=`<div class="enh-modal-card" tabindex="-1"><button class="enh-modal-close" type="button" aria-label="${t('close')}">×</button><div class="enh-modal-breadcrumb"><button type="button" class="enh-modal-home">${lang==='ar'?'المشاريع':'Projects'}</button><span>/</span><span class="enh-modal-crumb-name"></span></div><div class="enh-modal-media"><img class="enh-modal-image" alt=""><button type="button" class="enh-image-zoom" data-i18n="zoom">${t('zoom')}</button><button type="button" class="enh-image-full" data-i18n="fullscreen">${t('fullscreen')}</button></div><div class="enh-modal-body"><div class="enh-modal-head"><div><div class="enh-kicker" data-i18n="details">${t('details')}</div><h3></h3></div><div class="enh-repo-badges"></div></div><p class="enh-modal-desc"></p><div class="enh-modal-tags"></div><div class="enh-case-grid"><article><b data-i18n="problem">${t('problem')}</b><p class="enh-problem"></p></article><article><b data-i18n="solution">${t('solution')}</b><p class="enh-solution"></p></article></div><div class="enh-repo-meta" aria-live="polite"></div><div class="enh-gallery" hidden></div><div class="enh-video" hidden></div><div class="enh-modal-actions"><a class="enh-primary enh-modal-github" href="https://github.com/rad03i2" target="_blank" rel="noopener">${icons.github}<span data-i18n="source">${t('source')}</span></a><a class="enh-secondary enh-modal-demo" href="https://rdwan.dev/" target="_blank" rel="noopener" hidden data-i18n="demo">${t('demo')}</a><button class="enh-secondary enh-copy-project" type="button" data-i18n="copyLink">${t('copyLink')}</button><button class="enh-secondary enh-ask-project" type="button" data-i18n="ask">${t('ask')}</button><a class="enh-secondary enh-desktop-link" href="https://github.com/rad03i2">GitHub Desktop</a></div><div class="enh-similar"><h4 data-i18n="similar">${t('similar')}</h4><div></div></div><div class="enh-modal-nav"><button type="button" class="enh-prev" data-i18n="prev">${t('prev')}</button><span class="enh-modal-count"></span><button type="button" class="enh-next" data-i18n="next">${t('next')}</button></div></div></div>`;
    document.body.appendChild(modal);
    const close=()=>closeProjectModal();$('.enh-modal-close',modal).addEventListener('click',close);modal.addEventListener('click',e=>{if(e.target===modal)close();});$('.enh-modal-home',modal).addEventListener('click',close);$('.enh-prev',modal).addEventListener('click',()=>openProject((currentModalIndex-1+projects.length)%projects.length,true));$('.enh-next',modal).addEventListener('click',()=>openProject((currentModalIndex+1)%projects.length,true));$('.enh-image-zoom',modal).addEventListener('click',()=>$('.enh-modal-media',modal).classList.toggle('is-zoomed'));$('.enh-image-full',modal).addEventListener('click',()=>$('.enh-modal-media',modal).requestFullscreen?.());$('.enh-copy-project',modal).addEventListener('click',()=>copyProjectLink(projects[currentModalIndex]));$('.enh-ask-project',modal).addEventListener('click',()=>askAboutProject(projects[currentModalIndex]));
    document.addEventListener('keydown',e=>{if(!modal.classList.contains('is-open'))return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')openProject((currentModalIndex+(lang==='ar'?1:-1)+projects.length)%projects.length,true);if(e.key==='ArrowRight')openProject((currentModalIndex+(lang==='ar'?-1:1)+projects.length)%projects.length,true);trapFocus(e,modal);});
    return modal;
  }

  function openProject(index, updateHash=true){
    const p=projects[index];if(!p)return;currentModalIndex=index;store.set('rad-last-project',p.n);const modal=ensureModal();$('.enh-modal-image',modal).src=`assets/images/projects/project-${p.n}.webp`;$('.enh-modal-image',modal).alt=p.name;$('.enh-modal h3',modal).textContent=p.name;$('.enh-modal-crumb-name',modal).textContent=p.name;$('.enh-modal-desc',modal).textContent=lang==='ar'?p.ar:p.en;$('.enh-problem',modal).textContent=lang==='ar'?p.problemAr:p.problemEn;$('.enh-solution',modal).textContent=lang==='ar'?p.solutionAr:p.solutionEn;$('.enh-modal-tags',modal).innerHTML=p.tags.map(x=>`<span>${x}</span>`).join('');$('.enh-modal-github',modal).href=githubBase+p.repo;const demo=$('.enh-modal-demo',modal);demo.hidden=!p.demo;if(p.demo)demo.href=location.origin+location.pathname;$('.enh-desktop-link',modal).href=`x-github-client://openRepo/${githubBase+p.repo}`;$('.enh-modal-count',modal).textContent=`${index+1} / ${projects.length}`;$('.enh-repo-meta',modal).innerHTML=`<span class="enh-loading-dot"></span>${lang==='ar'?'جلب بيانات GitHub...':'Loading GitHub data...'}`;renderSimilar(p,modal);renderDynamicText();modal.classList.add('is-open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';$('.enh-modal-card',modal).focus();if(updateHash)history.replaceState(null,'',`#project=${p.n}`);getRepoInfo(p).then(info=>renderRepoInfo(info,modal)).catch(()=>{$('.enh-repo-meta',modal).textContent=lang==='ar'?'تعذر جلب بيانات GitHub الآن.':'GitHub metadata is currently unavailable.';});
  }

  function closeProjectModal(){const modal=$('#enhProjectModal');if(!modal)return;modal.classList.remove('is-open');modal.setAttribute('aria-hidden','true');document.body.style.overflow='';if(location.hash.startsWith('#project='))history.replaceState(null,'',location.pathname+location.search);}

  function bindProjectModal(){const grid=$('#projectsShowcaseGrid');if(!grid)return;ensureModal();grid.addEventListener('click',e=>{const a=e.target.closest('.showcase-image-link');if(!a)return;const card=a.closest('.showcase-card');const i=Number(card?.dataset.projectIndex);if(!Number.isFinite(i))return;e.preventDefault();openProject(i);});}

  async function getRepoInfo(p){
    if(repoCache.has(p.repo))return repoCache.get(p.repo);const cacheKey=`rad-repo-${p.repo}`;try{const cached=JSON.parse(sessionStorage.getItem(cacheKey)||'null');if(cached&&Date.now()-cached.at<15*60*1000){repoCache.set(p.repo,cached.data);return cached.data;}}catch{}
    const r=await fetch(`https://api.github.com/repos/${OWNER}/${p.repo}`,{headers:{Accept:'application/vnd.github+json'}});if(!r.ok)throw new Error('github');const data=await r.json();repoCache.set(p.repo,data);try{sessionStorage.setItem(cacheKey,JSON.stringify({at:Date.now(),data}));}catch{}return data;
  }

  function renderRepoInfo(info,modal){const el=$('.enh-repo-meta',modal);if(!info||!el)return;const d=info.pushed_at?new Intl.DateTimeFormat(lang==='ar'?'ar-IQ':'en-US',{dateStyle:'medium'}).format(new Date(info.pushed_at)):'—';el.innerHTML=`${info.private===false?`<span>✓ ${t('publicRepo')}</span>`:''}${info.language?`<span>${t('language')}: <b>${info.language}</b></span>`:''}<span>${t('stars')}: <b>${info.stargazers_count??0}</b></span><span>${t('forks')}: <b>${info.forks_count??0}</b></span><span>${t('lastUpdate')}: <b>${d}</b></span>`;}

  function renderSimilar(p,modal){const similar=projects.filter(x=>x!==p&&x.cats.some(c=>p.cats.includes(c))).slice(0,3);$('.enh-similar>div',modal).innerHTML=similar.map(x=>`<button type="button" data-project="${x.n}">${x.name}</button>`).join('')||'<span>—</span>';$$('[data-project]',$('.enh-similar',modal)).forEach(b=>b.addEventListener('click',()=>openProject(projects.findIndex(x=>x.n===b.dataset.project),true)));}

  async function copyProjectLink(p){try{await navigator.clipboard.writeText(projectLink(p.n));showToast(lang==='ar'?'تم نسخ رابط المشروع':'Project link copied');}catch{showToast(projectLink(p.n));}}
  async function askAboutProject(p){const msg=lang==='ar'?`مرحبًا رضوان، أريد الاستفسار عن مشروع ${p.name}.\nرابط المشروع: ${projectLink(p.n)}`:`Hello Radwan, I would like to ask about ${p.name}.\nProject link: ${projectLink(p.n)}`;try{await navigator.clipboard.writeText(msg);showToast(lang==='ar'?'تم نسخ رسالة الاستفسار. افتح Instagram وأرسلها.':'Inquiry copied. Open Instagram and send it.','Instagram',()=>window.open(instagram,'_blank','noopener'));}catch{window.open(instagram,'_blank','noopener');}}

  function handleDirectLinks(){const match=location.hash.match(/^#project=(\d{2})$/);if(match){const i=projects.findIndex(p=>p.n===match[1]);if(i>=0)setTimeout(()=>openProject(i,false),350);}const svc=location.hash.match(/^#service=([\w-]+)$/);if(svc)setTimeout(()=>document.querySelector(`#service-${CSS.escape(svc[1])}`)?.scrollIntoView({behavior:'smooth',block:'center'}),300);}

  async function copyServiceLink(id){const url=`${location.origin}${location.pathname}#service=${id}`;try{await navigator.clipboard.writeText(url);showToast(lang==='ar'?'تم نسخ رابط الخدمة':'Service link copied');}catch{showToast(url);}}

  function addRequestModal(){if($('#enhRequestModal'))return;const modal=document.createElement('div');modal.id='enhRequestModal';modal.className='enh-modal enh-request-modal';modal.setAttribute('aria-hidden','true');modal.innerHTML=`<div class="enh-modal-card enh-request-card" tabindex="-1"><button class="enh-modal-close" type="button" aria-label="${t('close')}">×</button><div class="enh-modal-body"><div class="enh-kicker" data-i18n="projectForm">${t('projectForm')}</div><h3>${lang==='ar'?'حوّل فكرتك إلى ملخص واضح':'Turn your idea into a clear brief'}</h3><form id="enhRequestForm"><label><span data-i18n="projectType">${t('projectType')}</span><select name="type"><option>Website</option><option>Windows App</option><option>Mobile App</option><option>Automation</option><option>Python Tool</option><option>AI Tool</option></select></label><label><span data-i18n="features">${t('features')}</span><textarea name="features" rows="3" placeholder="${lang==='ar'?'مثال: تسجيل دخول، لوحة تحكم، رفع ملفات...':'e.g. login, dashboard, file upload...'}"></textarea></label><label><span data-i18n="deadline">${t('deadline')}</span><select name="timeline"><option>${lang==='ar'?'مرنة':'Flexible'}</option><option>${lang==='ar'?'أقل من أسبوع':'Less than a week'}</option><option>${lang==='ar'?'1 - 4 أسابيع':'1 - 4 weeks'}</option><option>${lang==='ar'?'أكثر من شهر':'More than a month'}</option></select></label><label><span data-i18n="notes">${t('notes')}</span><textarea name="notes" rows="3"></textarea></label><div class="enh-estimator"><b data-i18n="complexity">${t('complexity')}</b><label><input type="checkbox" name="auth"> Auth</label><label><input type="checkbox" name="database"> Database</label><label><input type="checkbox" name="files"> Files</label><label><input type="checkbox" name="api"> API</label><label><input type="checkbox" name="realtime"> Realtime</label><output id="enhComplexity">${t('simple')}</output></div><div class="enh-modal-actions"><button class="enh-primary" type="submit" data-i18n="generate">${t('generate')}</button><button class="enh-secondary" id="enhCopyBrief" type="button" disabled data-i18n="copy">${t('copy')}</button><a class="enh-secondary" href="${instagram}" target="_blank" rel="noopener">Instagram</a></div><textarea id="enhBriefOutput" class="enh-brief-output" rows="8" readonly placeholder="${t('summary')}"></textarea></form></div></div>`;document.body.appendChild(modal);$('.enh-modal-close',modal).addEventListener('click',()=>closeRequestModal());modal.addEventListener('click',e=>{if(e.target===modal)closeRequestModal();});const form=$('#enhRequestForm');form.addEventListener('change',updateComplexity);form.addEventListener('input',updateComplexity);form.addEventListener('submit',e=>{e.preventDefault();generateBrief();});$('#enhCopyBrief').addEventListener('click',async()=>{const text=$('#enhBriefOutput').value;if(!text)return;await navigator.clipboard.writeText(text);showToast(lang==='ar'?'تم نسخ ملخص الطلب':'Project brief copied');});}
  function openRequestModal(){window.open(projectRequestUrl,'_blank','noopener,noreferrer');}
  function openConsultation(){window.open(consultationUrl,'_blank','noopener,noreferrer');}
  function closeRequestModal(){const m=$('#enhRequestModal');if(!m)return;m.classList.remove('is-open');m.setAttribute('aria-hidden','true');document.body.style.overflow='';}
  function complexityLevel(){const f=$('#enhRequestForm');if(!f)return 0;return ['auth','database','files','api','realtime'].filter(x=>f.elements[x].checked).length;}
  function updateComplexity(){const n=complexityLevel();const level=n<=1?t('simple'):n<=3?t('medium'):t('advanced');if($('#enhComplexity'))$('#enhComplexity').textContent=level;}
  function generateBrief(){const f=$('#enhRequestForm');const n=complexityLevel();const level=n<=1?t('simple'):n<=3?t('medium'):t('advanced');const data=new FormData(f);const text=lang==='ar'?`طلب مشروع\n- النوع: ${data.get('type')}\n- الميزات: ${data.get('features')||'غير محدد'}\n- المدة: ${data.get('timeline')}\n- التعقيد التقديري: ${level}\n- ملاحظات: ${data.get('notes')||'لا يوجد'}\n- وظائف إضافية: ${['auth','database','files','api','realtime'].filter(x=>f.elements[x].checked).join(', ')||'لا يوجد'}`:`Project request\n- Type: ${data.get('type')}\n- Features: ${data.get('features')||'Not specified'}\n- Timeline: ${data.get('timeline')}\n- Estimated complexity: ${level}\n- Notes: ${data.get('notes')||'None'}\n- Additional functions: ${['auth','database','files','api','realtime'].filter(x=>f.elements[x].checked).join(', ')||'None'}`;$('#enhBriefOutput').value=text;$('#enhCopyBrief').disabled=false;}

  function addFaq(){const footer=$('.site-footer');if(!footer||$('#faq'))return;const data=lang==='ar'?[['هل يمكن تعديل المشروع بعد التسليم؟','يعتمد ذلك على نطاق العمل المتفق عليه، ويمكن ترتيب تحسينات أو تحديثات لاحقة بشكل مستقل.'],['هل سيكون الموقع متجاوبًا مع الهاتف؟','أي واجهة ويب أنشئها للموقع تستهدف الشاشات المختلفة ما لم يتطلب المشروع خلاف ذلك.'],['كيف نبدأ؟','اضغط «اطلب مشروعك» لإرسال التفاصيل عبر النموذج المخصص، أو اختر «احجز استشارة» إذا كانت الفكرة تحتاج نقاشًا مباشرًا قبل البدء.'],['هل يمكن مشاهدة الكود؟','المشاريع العامة في GitHub مرتبطة مباشرة من بطاقاتها.']]:[['Can a project be changed after delivery?','It depends on the agreed scope. Follow-up improvements can be planned separately.'],['Will the website work on mobile?','Web interfaces are designed responsively unless the project requires otherwise.'],['How do we start?','Use “Start a project” to submit the dedicated request form, or book a consultation if the idea needs a direct discussion first.'],['Can I inspect the source code?','Public GitHub repositories are linked directly from the project cards.']];const sec=document.createElement('section');sec.id='faq';sec.className='enh-section';sec.innerHTML=`<div class="enh-shell"><div class="enh-kicker" data-i18n="faq">${t('faq')}</div><h2 class="enh-title small" data-i18n="faqTitle">${t('faqTitle')}</h2><div class="enh-faq">${data.map(([q,a])=>`<details><summary>${q}</summary><p>${a}</p></details>`).join('')}</div></div>`;footer.insertAdjacentElement('beforebegin',sec);}

  function addContact(){const footer=$('.site-footer');if(!footer||$('#contact'))return;const sec=document.createElement('section');sec.id='contact';sec.className='enh-contact enh-section enh-snap';sec.innerHTML=`<div class="enh-shell"><div class="enh-contact-card enh-reveal"><div class="enh-kicker" data-i18n="contact">${t('contact')}</div><h2 class="enh-title" data-i18n="contactTitle">${t('contactTitle')}</h2><p class="enh-subtitle" data-i18n="contactSub">${t('contactSub')}</p><div class="enh-contact-actions"><a class="enh-primary" id="enhContactRequest" href="${projectRequestUrl}" target="_blank" rel="noopener noreferrer" data-i18n="request">${t('request')}</a><a class="enh-secondary" href="${consultationUrl}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'احجز استشارة':'Book a consultation'}</a><a class="enh-secondary" href="${omnisendUpdates}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'تحديثات المشاريع':'Project updates'}</a><a class="enh-secondary" href="${instagram}" target="_blank" rel="noopener">Instagram</a><a class="enh-secondary" href="${facebook}" target="_blank" rel="noopener">Facebook</a><a class="enh-secondary" href="https://github.com/${OWNER}" target="_blank" rel="noopener">${icons.github}<span>GitHub</span></a><button class="enh-secondary" id="enhCopyGithub" type="button">@${OWNER}</button><button class="enh-secondary" id="enhShareSite" type="button">${icons.share}<span data-i18n="share">${t('share')}</span></button><a class="enh-secondary" href="assets/Radwan-CV.pdf" download data-i18n="cv">${t('cv')}</a><a class="enh-secondary" href="assets/Radwan-Portfolio.pdf" download data-i18n="portfolioPdf">${t('portfolioPdf')}</a><button class="enh-secondary" id="enhQrButton" type="button">QR</button><button class="enh-secondary" id="enhInstallButton" type="button" hidden data-i18n="install">${t('install')}</button></div><div class="enh-version"><span data-i18n="version">${t('version')}</span> <b>v${VERSION}</b></div></div></div>`;footer.insertAdjacentElement('beforebegin',sec);$('#enhCopyGithub').addEventListener('click',async()=>{await navigator.clipboard.writeText(OWNER);showToast(lang==='ar'?'تم نسخ اسم GitHub':'GitHub username copied');});$('#enhShareSite').addEventListener('click',shareSite);$('#enhQrButton').addEventListener('click',showQr);$('#enhInstallButton').addEventListener('click',installPwa);}

  function showQr(){let m=$('#enhQrModal');if(!m){m=document.createElement('div');m.id='enhQrModal';m.className='enh-modal';m.innerHTML=`<div class="enh-modal-card enh-qr-card"><button class="enh-modal-close" type="button">×</button><div class="enh-modal-body"><h3>QR</h3><img alt="QR code"><p></p></div></div>`;document.body.appendChild(m);$('.enh-modal-close',m).addEventListener('click',()=>m.classList.remove('is-open'));m.addEventListener('click',e=>{if(e.target===m)m.classList.remove('is-open');});}const url=location.origin+location.pathname;$('img',m).src=`https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(url)}`;$('p',m).textContent=url;m.classList.add('is-open');}

  async function shareSite(){const data={title:document.title,text:lang==='ar'?'ملف رضوان عبد الهادي البرمجي':'Radwan Abdulhadi developer portfolio',url:location.origin+location.pathname};try{if(navigator.share)await navigator.share(data);else{await navigator.clipboard.writeText(data.url);showToast(lang==='ar'?'تم نسخ رابط الموقع':'Site link copied');}}catch{}}

  function addGithubActivity(){const contact=$('#contact');if(!contact||$('#enhGithubActivity'))return;const sec=document.createElement('section');sec.id='enhGithubActivity';sec.className='enh-section';sec.innerHTML=`<div class="enh-shell"><div class="enh-kicker" data-i18n="githubActivity">${t('githubActivity')}</div><h2 class="enh-title small" data-i18n="latestRepos">${t('latestRepos')}</h2><div class="enh-github-grid"><div class="enh-github-skeleton"></div><div class="enh-github-skeleton"></div><div class="enh-github-skeleton"></div></div><div class="enh-request-row"><a class="enh-primary" href="https://github.com/${OWNER}" target="_blank" rel="noopener">${icons.github}<span data-i18n="followGithub">${t('followGithub')}</span></a></div></div>`;contact.insertAdjacentElement('beforebegin',sec);fetchGithubActivity(sec);}
  async function fetchGithubActivity(sec){try{const r=await fetch(`https://api.github.com/users/${OWNER}/repos?sort=updated&per_page=6&type=owner`);if(!r.ok)throw 0;const data=await r.json();$('.enh-github-grid',sec).innerHTML=data.filter(x=>!x.fork).slice(0,6).map(x=>`<a href="${x.html_url}" target="_blank" rel="noopener"><b>${x.name}</b><p>${x.description||''}</p><span>${x.language||'—'} · ★ ${x.stargazers_count}</span></a>`).join('');}catch{$('.enh-github-grid',sec).innerHTML=`<p class="enh-muted">${lang==='ar'?'تعذر تحميل نشاط GitHub الآن.':'GitHub activity is temporarily unavailable.'}</p>`;}}

  function addCommandPalette(){if($('#enhCommandPalette'))return;const m=document.createElement('div');m.id='enhCommandPalette';m.className='enh-command';m.setAttribute('aria-hidden','true');m.innerHTML=`<div class="enh-command-card" role="dialog" aria-modal="true"><label>${icons.search}<input type="search" data-i18n-placeholder="command" placeholder="${t('command')}" autocomplete="off"></label><div class="enh-command-results"></div><footer><span>Ctrl + K</span><span>Esc</span></footer></div>`;document.body.appendChild(m);m.addEventListener('click',e=>{if(e.target===m)closeCommandPalette();});$('input',m).addEventListener('input',renderCommands);$('input',m).addEventListener('keydown',commandKeys);renderCommands();document.addEventListener('keydown',globalKeys);}
  function commandItems(){return [{label:lang==='ar'?'المشاريع':'Projects',hint:'P',action:()=>scrollToId('projects')},{label:t('servicesTitle'),hint:'S',action:()=>scrollToId('services')},{label:t('contactTitle'),hint:'C',action:()=>scrollToId('contact')},{label:'GitHub',hint:'G',action:()=>window.open(`https://github.com/${OWNER}`,'_blank','noopener')},{label:t('request'),hint:'R',action:openRequestModal},{label:lang==='ar'?'احجز استشارة':'Book a consultation',hint:'B',action:openConsultation},{label:lang==='ar'?'تابع تحديثات المشاريع':'Project updates',hint:'U',action:()=>window.open(omnisendUpdates,'_blank','noopener,noreferrer')},...projects.map((p,i)=>({label:p.name,hint:`#${p.n}`,action:()=>openProject(i)}))];}
  function renderCommands(){const m=$('#enhCommandPalette');if(!m)return;const q=$('input',m).value.trim().toLowerCase();const items=commandItems().filter(x=>!q||x.label.toLowerCase().includes(q)||x.hint.toLowerCase().includes(q)).slice(0,12);$('.enh-command-results',m).innerHTML=items.length?items.map((x,i)=>`<button type="button" data-cmd="${i}" class="${i===0?'is-active':''}"><span>${x.label}</span><kbd>${x.hint}</kbd></button>`).join(''):`<p>${t('noResults')}</p>`;$$('[data-cmd]',m).forEach((b,i)=>b.addEventListener('click',()=>{items[i].action();closeCommandPalette();}));m._items=items;}
  function commandKeys(e){const m=$('#enhCommandPalette');const bs=$$('[data-cmd]',m);if(!bs.length)return;let i=bs.findIndex(b=>b.classList.contains('is-active'));if(e.key==='ArrowDown'){e.preventDefault();i=(i+1)%bs.length;}else if(e.key==='ArrowUp'){e.preventDefault();i=(i-1+bs.length)%bs.length;}else if(e.key==='Enter'){e.preventDefault();m._items?.[i]?.action();closeCommandPalette();return;}else return;bs.forEach((b,j)=>b.classList.toggle('is-active',j===i));}
  function openCommandPalette(){const m=$('#enhCommandPalette');if(!m)return;m.classList.add('is-open');m.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';const i=$('input',m);i.value='';renderCommands();setTimeout(()=>i.focus(),20);}
  function closeCommandPalette(){const m=$('#enhCommandPalette');if(!m)return;m.classList.remove('is-open');m.setAttribute('aria-hidden','true');document.body.style.overflow='';}
  function globalKeys(e){if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openCommandPalette();return;}if(e.key==='Escape'){closeCommandPalette();closeRequestModal();}if(e.ctrlKey||e.metaKey||e.altKey||['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName))return;const k=e.key.toLowerCase();if(k==='p')scrollToId('projects');if(k==='c')scrollToId('contact');if(k==='g')window.open(`https://github.com/${OWNER}`,'_blank','noopener');if(k==='s')scrollToId('services');}
  function scrollToId(id){document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'});}

  function addBottomNav(){if($('#enhBottomNav'))return;const nav=document.createElement('nav');nav.id='enhBottomNav';nav.className='enh-bottom-nav';nav.setAttribute('aria-label','Mobile navigation');nav.innerHTML=`<button data-go="top">⌂<span>${lang==='ar'?'الرئيسية':'Home'}</span></button><button data-go="projects">◫<span>${lang==='ar'?'المشاريع':'Projects'}</span></button><button data-go="services">◇<span>${lang==='ar'?'الخدمات':'Services'}</span></button><button data-go="contact">@<span>${lang==='ar'?'تواصل':'Contact'}</span></button>`;document.body.appendChild(nav);$$('[data-go]',nav).forEach(b=>b.addEventListener('click',()=>b.dataset.go==='top'?scrollTo({top:0,behavior:'smooth'}):scrollToId(b.dataset.go)));}

  function addFloatingButtons(){if($('#enhBackTop'))return;const top=document.createElement('button');top.id='enhBackTop';top.className='enh-float enh-backtop';top.type='button';top.setAttribute('aria-label','Back to top');top.innerHTML=icons.up;const contact=document.createElement('a');contact.id='enhFloatContact';contact.className='enh-float enh-float-contact';contact.href=instagram;contact.target='_blank';contact.rel='noopener';contact.textContent='@';document.body.append(top,contact);top.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));const update=()=>{top.classList.toggle('is-visible',scrollY>650);contact.classList.toggle('is-visible',scrollY>450);};addEventListener('scroll',update,{passive:true});update();}

  function addWelcomeAndLastProject(){if(!store.get('rad-welcomed')){store.set('rad-welcomed','1');setTimeout(()=>showToast(`${t('welcome')} — ${t('welcomeSub')}`),900);}const last=store.get('rad-last-project');if(last){const p=projects.find(x=>x.n===last);if(p&&!$('#enhContinue')){const box=document.createElement('button');box.id='enhContinue';box.className='enh-continue';box.type='button';box.innerHTML=`<span data-i18n="continueProject">${t('continueProject')}</span><b>${p.name}</b>`;document.body.appendChild(box);box.addEventListener('click',()=>{openProject(projects.indexOf(p));box.remove();});setTimeout(()=>box.classList.add('is-visible'),1200);setTimeout(()=>box.classList.remove('is-visible'),9000);}}}

  function addQrPwa(){window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredInstallPrompt=e;const b=$('#enhInstallButton');if(b)b.hidden=false;});window.addEventListener('appinstalled',()=>{deferredInstallPrompt=null;const b=$('#enhInstallButton');if(b)b.hidden=true;showToast(lang==='ar'?'تم تثبيت الموقع':'Site installed');});if('serviceWorker'in navigator){navigator.serviceWorker.register('service-worker.js').then(reg=>{swRegistration=reg;reg.addEventListener('updatefound',()=>{const w=reg.installing;if(!w)return;w.addEventListener('statechange',()=>{if(w.state==='installed'&&navigator.serviceWorker.controller)showToast(t('updated'),t('update'),forceUpdate);});});navigator.serviceWorker.addEventListener('controllerchange',()=>{if(!sessionStorage.getItem('rad-reloaded')){sessionStorage.setItem('rad-reloaded','1');location.reload();}});}).catch(()=>{});}}
  async function installPwa(){if(!deferredInstallPrompt){showToast(lang==='ar'?'استخدم خيار «تثبيت التطبيق» من قائمة المتصفح إذا كان متاحًا.':'Use your browser “Install app” option if available.');return;}deferredInstallPrompt.prompt();await deferredInstallPrompt.userChoice;deferredInstallPrompt=null;const b=$('#enhInstallButton');if(b)b.hidden=true;}
  async function forceUpdate(){try{await swRegistration?.update();if('caches'in window){for(const k of await caches.keys())await caches.delete(k);}location.reload();}catch{location.reload();}}

  function addUpdateControl(){const footer=$('.site-footer');if(!footer||$('#enhUtilityBar'))return;const div=document.createElement('div');div.id='enhUtilityBar';div.className='enh-utility-bar';div.innerHTML=`<span>Portfolio v${VERSION}</span><button type="button" id="enhForceUpdate" data-i18n="update">${t('update')}</button><button type="button" id="enhPrint" data-i18n="printPdf">${t('printPdf')}</button><a href="admin.html" rel="nofollow">Admin</a>`;footer.insertAdjacentElement('beforebegin',div);$('#enhForceUpdate').addEventListener('click',forceUpdate);$('#enhPrint').addEventListener('click',()=>window.print());}

  function addAccessibility(){if(!$('#enhSkip')){const skip=document.createElement('a');skip.id='enhSkip';skip.className='enh-skip';skip.href='#projects';skip.textContent=lang==='ar'?'تجاوز إلى المشاريع':'Skip to projects';document.body.prepend(skip);}document.querySelectorAll('button,a,input,select,textarea').forEach(el=>{if(!el.getAttribute('aria-label')&&!el.textContent.trim()&&!el.getAttribute('title'))el.setAttribute('aria-label','interactive control');});}
  function trapFocus(e,root){if(e.key!=='Tab')return;const f=$$('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])',root).filter(x=>!x.disabled&&!x.hidden);if(!f.length)return;const first=f[0],last=f[f.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}

  function revealOnScroll(){const nodes=$$('.enh-reveal');if(!nodes.length)return;if(document.documentElement.classList.contains('enh-reduce-motion')||matchMedia('(prefers-reduced-motion: reduce)').matches){nodes.forEach(n=>n.classList.add('is-visible'));return;}const io=new IntersectionObserver(entries=>entries.forEach(x=>{if(x.isIntersecting){x.target.classList.add('is-visible');io.unobserve(x.target);}}),{threshold:.1,rootMargin:'0px 0px -28px'});nodes.forEach(n=>io.observe(n));}
  function animateCounters(){const nodes=$$('[data-count]');if(!nodes.length)return;const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(!e.isIntersecting)return;const el=e.target,target=Number(el.dataset.count)||0;if(document.documentElement.classList.contains('enh-reduce-motion')){el.textContent=target;io.unobserve(el);return;}let start=0;const s=performance.now(),dur=700;const tick=now=>{const p=Math.min(1,(now-s)/dur);el.textContent=Math.round(start+(target-start)*p);if(p<1)requestAnimationFrame(tick);};requestAnimationFrame(tick);io.unobserve(el);}),{threshold:.6});nodes.forEach(n=>io.observe(n));}

  function addMagneticAndSpotlight(){if(!matchMedia('(pointer:fine)').matches)return;$$('.enh-primary,.enh-secondary,.projects-more-button').forEach(el=>{el.addEventListener('mousemove',e=>{if(document.documentElement.classList.contains('enh-reduce-motion'))return;const r=el.getBoundingClientRect();const x=(e.clientX-r.left-r.width/2)*.08,y=(e.clientY-r.top-r.height/2)*.08;el.style.transform=`translate(${x}px,${y}px)`;});el.addEventListener('mouseleave',()=>el.style.transform='');});$$('.showcase-card,.enh-service').forEach(el=>el.addEventListener('pointermove',e=>{const r=el.getBoundingClientRect();el.style.setProperty('--mx',`${e.clientX-r.left}px`);el.style.setProperty('--my',`${e.clientY-r.top}px`);}));}

  function addFaqIfMissing(){addFaq();}

  function addProjectSkeletons(){ $$('.showcase-card').forEach(card=>{if(!$('.enh-skeleton',card)){const s=document.createElement('span');s.className='enh-skeleton';$('.showcase-image-link',card)?.appendChild(s);const img=$('img',card);if(img?.complete)card.classList.add('is-image-loaded');}}); }

  function applyImagePerf(){ $$('img').forEach((img,i)=>{if(!img.closest('.hero')||i>0)img.loading='lazy';img.decoding='async';}); }

  function polishTooltips(){ $$('.hero-socials a').forEach(a=>a.dataset.tip=a.getAttribute('title')||a.getAttribute('aria-label')||''); $$('.github-icon-button').forEach(a=>a.dataset.tip='GitHub'); }

  function addOpenGraphRuntime(){const set=(prop,content)=>{let m=document.querySelector(`meta[property="${prop}"]`);if(!m){m=document.createElement('meta');m.setAttribute('property',prop);document.head.appendChild(m);}m.content=content;};set('og:title',document.title);set('og:description',lang==='ar'?'ملف رضوان عبد الهادي - مشاريع ويب وحاسوب وأتمتة.':'Radwan Abdulhadi developer portfolio - web, desktop and automation projects.');set('og:url',location.origin+location.pathname);set('og:type','website');const name=document.querySelector('meta[name="description"]')||Object.assign(document.createElement('meta'),{name:'description'});name.content=lang==='ar'?'رضوان عبد الهادي - مطور برمجيات ومشاريع ويب وحاسوب وأتمتة.':'Radwan Abdulhadi - software developer portfolio for web, desktop and automation projects.';if(!name.parentNode)document.head.appendChild(name);}

  function addStructuredDataRuntime(){if($('#enhSchema'))return;const s=document.createElement('script');s.id='enhSchema';s.type='application/ld+json';s.textContent=JSON.stringify({'@context':'https://schema.org','@type':'Person',name:'Radwan Abdulhadi',url:location.origin+location.pathname,sameAs:[`https://github.com/${OWNER}`,instagram,facebook],jobTitle:'Software Developer',knowsAbout:['Python','C#','JavaScript','Web Development','Windows Applications','Automation']});document.head.appendChild(s);}

  function addServiceDeepLinkOnCards(){ serviceItems.forEach(([id])=>{document.getElementById(`service-${id}`)?.setAttribute('tabindex','-1');}); }

  function renderFirstLanguage(){document.documentElement.lang=I18N[lang].lang;document.documentElement.dir=I18N[lang].dir;translateBase();renderDynamicText();}

  function bootProjects(retries=0){if(!prepareProjectCards()){if(retries<50)setTimeout(()=>bootProjects(retries+1),100);return;}addProjectTools();bindProjectModal();addProjectSkeletons();renderProjectsLanguage();handleDirectLinks();polishTooltips();revealOnScroll();addMagneticAndSpotlight();}

  // INTERNAL-ACTION-LOADER
  function setupInternalActionLoader(){
    if(document.documentElement.dataset.internalLoaderBound==='1') return;
    document.documentElement.dataset.internalLoaderBound='1';

    const excludedButtons = '#enhLangToggle,#enhThemeToggle,#enhMotionToggle,#enhCommandOpen,.menu-button,.enh-modal-close,.enh-filter,[data-no-loader]';
    const showLoader = () => {
      let loader = document.querySelector('.enh-loader.enh-action-loader');
      if(loader){
        loader.classList.remove('is-done');
        clearTimeout(loader._hideTimer);
        clearTimeout(loader._removeTimer);
      } else {
        loader=document.createElement('div');
        loader.className='enh-loader enh-action-loader';
        loader.setAttribute('aria-hidden','true');
        loader.innerHTML='<div><b>&lt;RAD /&gt;</b><span></span></div>';
        document.body.appendChild(loader);
      }
      loader._hideTimer=setTimeout(()=>{
        loader.classList.add('is-done');
        loader._removeTimer=setTimeout(()=>loader.remove(),180);
      },320);
    };

    document.addEventListener('click',(event)=>{
      if(event.defaultPrevented || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const target=event.target.closest('a,button');
      if(!target || target.matches(excludedButtons) || target.disabled) return;

      if(target.tagName==='A'){
        const raw=(target.getAttribute('href')||'').trim();
        if(!raw || raw==='#' || raw.startsWith('mailto:') || raw.startsWith('tel:') || raw.startsWith('javascript:') || target.hasAttribute('download')) return;
        let url;
        try{ url=new URL(target.href,location.href); }catch{return;}
        if(url.origin!==location.origin) return;
        showLoader();
        return;
      }

      showLoader();
    },true);
  }

  function boot(){
    // Keep first paint small and stable; the loader is intentionally skipped.
    injectHead(); addProgressBar(); addHeaderControls(); renderFirstLanguage(); addAvailability(); addAccessibility(); applyImagePerf(); setupInternalActionLoader();

    // Project behavior is useful early, but does not need to block first paint.
    setTimeout(() => { try { bootProjects(); } catch (e) { console.warn(e); } }, 90);

    // Build below-the-fold enhancements one small task at a time.
    const tasks=[hydrateTechIconTicker,addStatsAndTicker,addFeaturedSinax,addServices,addProcess,addRequestModal,addFaqIfMissing,addContact,addGithubActivity,addCommandPalette,addBottomNav,addFloatingButtons,addWelcomeAndLastProject,addQrPwa,addUpdateControl,addOpenGraphRuntime,addStructuredDataRuntime,addServiceDeepLinkOnCards,revealOnScroll,animateCounters];
    const step=()=>{
      const fn=tasks.shift(); if(!fn) return;
      try { fn(); } catch(e) { console.warn(e); }
      if(!tasks.length) return;
      if('requestIdleCallback' in window) requestIdleCallback(step,{timeout:350}); else setTimeout(step,28);
    };
    if('requestIdleCallback' in window) requestIdleCallback(step,{timeout:500}); else setTimeout(step,180);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();

/* ACCESSIBILITY-FINAL */
(function(){
  const fixAccessibleNames=()=>{
    const brand=document.querySelector('a.brand');
    if(brand) brand.removeAttribute('aria-label');
    document.querySelectorAll('.showcase-image-link[aria-label]').forEach(a=>a.removeAttribute('aria-label'));
  };
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fixAccessibleNames,{once:true});
  else fixAccessibleNames();
  const observer=new MutationObserver(fixAccessibleNames);
  observer.observe(document.documentElement,{childList:true,subtree:true});
  setTimeout(()=>observer.disconnect(),5000);
})();


/* STATS-LIVE-V1 */
(() => {
  'use strict';

  const OWNER = 'rad03i2';
  const ROTATE_MS = 3000;
  const CACHE_KEY = 'rad-github-public-repos-v1';
  const CACHE_TTL = 6 * 60 * 60 * 1000;

  const slides = {
    web: [
      ['Websites','مواقع شخصية وتجارية متجاوبة','WEB',205],
      ['Landing Pages','صفحات هبوط احترافية للمشاريع والخدمات','LAND',334],
      ['E-Commerce','متاجر إلكترونية وتجارب شراء واضحة','SHOP',24],
      ['Web Apps','تطبيقات ويب سريعة وقابلة للتوسع','WEBAPP',188],
      ['RTL Interfaces','واجهات عربية RTL متجاوبة وحديثة','RTL',112],
      ['Dashboards','لوحات تحكم وواجهات بيانات تفاعلية','DASH',265],
      ['Mobile Apps','تطبيقات وتجارب هاتف قابلة للتطوير','MOBILE',292],
      ['Android Apps','تطبيقات وواجهات Android عملية','ANDROID',150],
      ['Business Sites','مواقع تعريفية وتجارية للأنشطة والخدمات','BIZ',44],
      ['Responsive UI','واجهات تعمل بسلاسة على الهاتف والحاسوب','UI',218]
    ],
    desktop: [
      ['Windows Apps','تطبيقات C# و.NET وWinUI مخصصة','WIN',146],
      ['Desktop Tools','أدوات سطح مكتب عملية حسب احتياجك','TOOLS',124],
      ['File Tools','إدارة الملفات ومعالجتها وتنظيمها','FILES',207],
      ['System Utilities','أدوات للنظام والتخزين والإنتاجية','SYSTEM',54],
      ['Internal Tools','برامج داخلية ولوحات تشغيل مخصصة','INTERNAL',182],
      ['PDF Tools','أدوات PDF للتحويل والمعالجة والتنظيم','PDF',15],
      ['Media Tools','أدوات للصور والصوت والفيديو','MEDIA',296],
      ['Developer Tools','أدوات ومساعدات مخصصة للمطورين','DEV',326],
      ['Custom Software','برامج مصممة حول فكرة أو سير عمل محدد','CUSTOM',86],
      ['Data Apps','تطبيقات بيانات وتقارير وواجهات تشغيل','DATA',192]
    ],
    automation: [
      ['Automation','أتمتة المهام وسير العمل المتكرر','AUTO',35],
      ['Python Automation','سكربتات Python للملفات والبيانات والمهام','PY',48],
      ['AI Integration','دمج خدمات ونماذج الذكاء الاصطناعي','AI',278],
      ['AI Assistants','مساعدون وأدوات ذكية للإنتاجية والمحتوى','ASSIST',304],
      ['API Integration','ربط الأنظمة والخدمات عبر واجهات API','API',198],
      ['Databases','قواعد بيانات وأنظمة إدارة وربط معلومات','DB',164],
      ['Data Dashboards','لوحات بيانات وتقارير ومؤشرات تفاعلية','REPORT',220],
      ['IoT Systems','مشاريع IoT وحساسات وربط أجهزة وبيانات','IOT',236],
      ['Browser Extensions','إضافات متصفح وأدوات تسهّل العمل','EXT',262],
      ['Backup & Reports','نسخ احتياطي وتقارير وعمليات تلقائية','BACKUP',108]
    ]
  };

  const isEnglish = () => (document.documentElement.lang || '').toLowerCase().startsWith('en');

  function paintCard(card, index, animate = true) {
    const list = slides[card.dataset.statGroup];
    if (!list?.length) return;
    const safeIndex = ((index % list.length) + list.length) % list.length;
    const [title, ar, ghost, hue] = list[safeIndex];
    const apply = () => {
      card.dataset.statIndex = String(safeIndex);
      card.dataset.ghost = ghost;
      card.style.setProperty('--stat-hue', String(hue));
      const titleEl = card.querySelector('[data-stat-title]');
      const descEl = card.querySelector('[data-stat-desc]');
      if (titleEl) titleEl.textContent = title;
      if (descEl) descEl.textContent = ar;
    };

    if (!animate) { apply(); return; }
    card.classList.add('is-switching');
    window.setTimeout(() => {
      apply();
      requestAnimationFrame(() => card.classList.remove('is-switching'));
    }, 300);
  }

  function renderLanguage() {
    const root = document.getElementById('enhStats');
    if (!root) return;
    const displayed = root.querySelector('[data-stat-label="displayed"]');
    const github = root.querySelector('[data-stat-label="github"]');
    if (displayed) displayed.textContent = isEnglish() ? 'projects displayed' : 'مشروعًا معروضًا';
    if (github) github.textContent = isEnglish() ? 'GitHub repositories' : 'مستودعات GitHub';
    root.querySelectorAll('[data-stat-group]').forEach(card => {
      paintCard(card, Number(card.dataset.statIndex || 0), false);
    });
    root.setAttribute('aria-label', isEnglish() ? 'Project statistics and capabilities' : 'إحصاءات ومجالات العمل');
  }

  function startRotationWhenVisible(root) {
    let timer = 0;
    const start = () => {
      if (timer) return;
      timer = window.setInterval(() => {
        if (document.hidden) return;
        root.querySelectorAll('[data-stat-group]').forEach(card => {
          paintCard(card, Number(card.dataset.statIndex || 0) + 1, true);
        });
      }, ROTATE_MS);
    };

    if (!('IntersectionObserver' in window)) { start(); return; }
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        start();
        observer.disconnect();
      }
    }, { threshold: .28, rootMargin: '0px 0px -8% 0px' });
    observer.observe(root);
  }

  function animateRepoCount(el, target) {
    if (!el || el.dataset.animated === '1') return;
    el.dataset.animated = '1';
    if (document.documentElement.classList.contains('enh-reduce-motion') ||
        matchMedia('(prefers-reduced-motion: reduce)').matches) {
      el.textContent = String(target);
      return;
    }
    const started = performance.now();
    const duration = 1050;
    const tick = now => {
      const progress = Math.min(1, (now - started) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = String(Math.round(target * eased));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function bindRepoCounterVisibility(root, el, target) {
    el.textContent = '0';
    if (!('IntersectionObserver' in window)) {
      animateRepoCount(el, target);
      return;
    }
    const observer = new IntersectionObserver(entries => {
      if (!entries.some(entry => entry.isIntersecting)) return;
      animateRepoCount(el, target);
      observer.disconnect();
    }, { threshold: .58, rootMargin: '0px 0px -5% 0px' });
    observer.observe(root);
  }

  async function hydrateGithubRepoCount(root) {
    const el = root.querySelector('[data-github-count]');
    if (!el) return;

    let cached = null;
    try { cached = JSON.parse(localStorage.getItem(CACHE_KEY) || 'null'); } catch {}
    const useCount = value => {
      const count = Number(value);
      if (!Number.isFinite(count) || count < 0) return false;
      bindRepoCounterVisibility(root, el, Math.round(count));
      return true;
    };

    if (cached && Date.now() - Number(cached.at || 0) < CACHE_TTL && useCount(cached.count)) return;

    try {
      const response = await fetch(`https://api.github.com/users/${OWNER}`, {
        headers: { Accept: 'application/vnd.github+json' }
      });
      if (!response.ok) throw new Error(`GitHub API ${response.status}`);
      const data = await response.json();
      const count = Number(data.public_repos);
      if (!Number.isFinite(count)) throw new Error('Invalid repository count');
      try { localStorage.setItem(CACHE_KEY, JSON.stringify({ count, at: Date.now() })); } catch {}
      useCount(count);
    } catch {
      if (cached) useCount(cached.count);
      else {
        el.textContent = '—';
        el.title = isEnglish() ? 'Repository count is temporarily unavailable' : 'تعذر جلب عدد المستودعات مؤقتًا';
      }
    }
  }

  function init() {
    const root = document.getElementById('enhStats');
    if (!root || root.dataset.liveStatsReady === '1') return;
    root.dataset.liveStatsReady = '1';
    renderLanguage();
    root.querySelectorAll('[data-stat-group]').forEach(card => paintCard(card, 0, false));
    startRotationWhenVisible(root);
    hydrateGithubRepoCount(root);

    const languageObserver = new MutationObserver(renderLanguage);
    languageObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['lang', 'dir'] });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
